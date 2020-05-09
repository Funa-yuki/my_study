import socket
import re
import MySQLdb
import StringIO
import mimetools
import redis
import uuid
import json
import ConfigParser
import time
import random
import ast

import multiprocessing

# read config
conf = ConfigParser.SafeConfigParser()
conf.read('./conf.ini')

# Check Pattarn
HTTP_PATTARN = r'Host: (.*):'
API_PATTARN = r'/api'
CONNECTION_PATTARN = r'Connection:'
PATH_PATTARN= r'([A-Z]{3,6}) (.*) HTTP/1.1'
RESPONSECODE_PATTARN = r'HTTP/1.1 ([0-9]{3}) (.*)'

# config Data for core system
L_PORT = int(conf.get('core', 'listen_port'))
D_PORT = conf.get('core', 'forward_port')
EXPIRE_TIME = int(conf.get('core', 'session_expire'))
APIMODE_LIMIT = int(conf.get('core', 'api_limit'))

# config Data for DNS log
dns_conf_path = conf.get('dns', 'log_path')
framework_domain = conf.get('dns', 'fw_domain')

# config Data for MySQL
DB_USER = conf.get('mysql', 'user')
DB_PASS = conf.get('mysql', 'password')
DB_HOST = conf.get('mysql', 'host')
DB_NAME = conf.get('mysql', 'dbname')

# worker Process
PROCESSES = int(conf.get('core', 'processes'))

host_head = re.compile(HTTP_PATTARN)
api_head = re.compile(API_PATTARN)
connect_head = re.compile(CONNECTION_PATTARN)
path_head = re.compile(PATH_PATTARN)
response_code = re.compile(RESPONSECODE_PATTARN)

# MySQL
conn = MySQLdb.connect(
    user=DB_USER,
    passwd=DB_PASS,
    host=DB_HOST,
    db=DB_NAME
)
c_sql = conn.cursor()

# Redis
p_sql = redis.Redis('localhost', 6379, 0)
d_sql = redis.Redis('localhost', 6379, 1)

def create_session(ip_addr):
    # Redis
    if p_sql.exists(ip_addr):
        json_data = p_sql.get(ip_addr)
        return json.loads(json_data)
    else:
        # port
        port = int(random.choice(ast.literal_eval(D_PORT)))
        session_id = uuid.uuid4().hex

        # json
        ret = {"Port": port, "Session": session_id}
        p_sql.set(ip_addr, json.dumps(ret, ensure_ascii=False))
        p_sql.expire(ip_addr, EXPIRE_TIME)

        return ret

def check_response(response_code):
    if response_code == '404':
        return True
    elif response_code == '403':
        return True
    elif response_code == '401':
        return True
    else:
        return False

def check_apimode(ip_addr):
    return True

# read a log file, fetch ip_list, and return ip_list
# need import re to execute
def ip_listing(path, domain):
    dns_patturn = re.compile(r'.*? %s from .*?' % domain)
    log = open(path, "r")
    ip_list = []
    for line in log:
        if dns_patturn.findall(line):
            result = re.findall(r'[0-9]+\.[0-9]+\.[0-9]+', line)
            ip_list.extend(result)
            return ip_list

# accept socket
def accept_req(cs):
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.settimeout(2)

    unique_id = uuid.uuid4().hex
    ip_addr = cs.getpeername()[0]

    # session_create
    session = create_session(ip_addr)


    #check_direct_access
    client_ip_list = ip_listing(dns_conf_path, framework_domain)
    for ip in client_ip_list:
        d_sql.set(ip, ip)
        
    # print session

    # Request Header Create
    head = cs.recv(4096)
    s_sql = 'select API_mode from session where IP_address = %s and SESSION_id = %s'
    c_sql.execute(s_sql, (ip_addr, session['Session']))
    log = c_sql.fetchone()
    if log == None:
        sql = 'insert into session (IP_address, SESSION_id, API_mode) values (%s, %s, %s)'
        c_sql.execute(sql, (ip_addr, session['Session'], 0))
        conn.commit()

    s2_sql = 'select BADREQUEST_num, DIRECTACCESS_num from attack_label where SESSION_id = %s'
    c_sql.execute(s2_sql, (session['Session'],))
    bad_access_log = c_sql.fetchone()
    if bad_access_log == None:
        attack_label = 'insert into attack_label (SESSION_id, BADREQUEST_num, DIRECTACCESS_num) values (%s, %s, %s)'
        c_sql.execute(attack_label, (session['Session'], 0, 0))
        conn.commit()

    if d_sql.get(ip_addr) == None:# first session and DNS access
        attack_count_up = 'update attack_label set DIRECTACCESS_num = DIRECTACCESS_num + 1 where SESSION_id = %s'
        c_sql.execute(attack_count_up, (session['Session'],))
        conn.commit()
######check until this (17:04)
    DirectAccess_sql = 'select DIRECTACCESS_num from attack_label where SESSION_id = %s'
    c_sql.execute(DirectAccess_sql, (session['Session'],))
    DirectAccess_num = c_sql.fetchone()

    BadRequest_sql = 'select BADREQUEST_num from attack_label where SESSION_id = %s'
    c_sql.execute(BadRequest_sql, (session['Session'],))
    BadRequest_num = c_sql.fetchone()

    bad_access_num = DirectAccess_num + BadRequest_num

    # when attacks detected, change api mode from true to fake
    if bad_access_num > APIMODE_LIMIT:
        sql = 'update session set API_mode = 1 where SESSION_id = %s'
        c_sql.execute(sql, (session['Session'],))
        conn.commit()

    c_sql.execute(s_sql, (ip_addr, session['Session'],))
    log = c_sql.fetchone()



    msg = ''
    for header in head:
        msg = msg + header

    # Forward Port Translate
    if host_head.search(msg):
        msg = re.sub(str(L_PORT), str(session['Port']), msg)

    #if log[0] > APIMODE_LIMIT:
    # log[0] is API_mode
    if  log[0] > 0:
        if msg.__len__() > 0:
            request_line, headers_alone = msg.split('\r\n', 1)
            print headers_alone
            # old
            headers = mimetools.Message(StringIO.StringIO(headers_alone))
            cut, header_data = headers_alone.rsplit('\r\n', 1)

            if header_data.__len__() > 0:
                p_sql.set(unique_id, header_data)

        # Request
        if path_head.search(msg):
            sql = 'insert into request (SESSION_id, REQUEST_path, METHOD, PARAMETERS) values (%s, %s, %s, %s)'
            if p_sql.exists(unique_id):
                c_sql.execute(sql, (
                session['Session'], path_head.search(msg).group(2), path_head.search(msg).group(1), unique_id))
            else:
                c_sql.execute(sql, (
                session['Session'], path_head.search(msg).group(2), path_head.search(msg).group(1), 'null'))
            conn.commit()

        # fake API change (if Fuck Data is in)
        if api_head.search(msg):
            msg = re.sub('/api', '/fake/api', msg)

    msglen = msg.__len__()
    total_sent = 0

    # http connect
    ss.connect((socket.gethostname(), session['Port']))
    while total_sent < msglen:
        sent = ss.send(msg[total_sent:])
        if sent == 0:
            raise RuntimeError("Error")
        total_sent = total_sent + sent
    chunks = []
    total_received = 0

    responseMessage = ""
    responseMessage = responseMessage.encode("utf-8")

    while True:
        try:
            data = ss.recv(1024)
        except socket.timeout:
            break
        r = response_code.search(data)
        if r != None:
            if check_response(r.group(1)):
                print r.group(1)
                # count_up = "update session set API_mode = API_mode + 1  where SESSION_id = %s"
                # c_sql.execute(count_up, (session['Session'],))
                # conn.commit()
                count_up = "update attack_label set BADREQUEST_num = BADREQUEST_num + 1 where SESSION_id = %s"
                c_sql.execute(count_up, (session['Session'],))
                conn.commit()
        if re.search(r':' + str(session['Port']), data):
            data = re.sub(':' + str(session['Port']), ':' + str(L_PORT), data)
        if len(data) == 0:
            break
        cs.send(data)

    ss.close()

# multi Processing Preparation
def start(handler, socket):
     for i in range(PROCESSES):
        p = multiprocessing.Process(target=handler,
                                    args=(socket,))
        p.daemon = True
        p.start()

# socket connection Preparation
def socket_connection(s):
    while True:
        cs, client_address = s.accept()
        accept_req(cs)
        cs.close()

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', L_PORT))
    s.listen(0.3)

    start(socket_connection, s)

    # Hostname
    print socket.gethostname()

    while True:
        time.sleep(1)

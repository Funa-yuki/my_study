# -*- coding: utf-8 -*-
# python Forwarding Service
# Created by clom.
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

# phpmyadmin pattarn
PMA_PATTARN = r'/pma'
PHPMYADMIN_PATTARN = r'/phpMyAdmin'
VERSON_PATTARN = r'v=4.8.3'
GET_PMA_PATTARN = r'GET /phpMyAdmin'
POST_PATTARN = r'POST '
DOT_PATTARN = r'/themes/dot.gif'
DB_PATTARN = r'db'
AJAX_PATTARN = r'ajax'
AJAX_PARAM_PATTARN = r'server=(.*)'
AJAX2_PARAM_PATTARN = r'key=(.*)'
PMA_PARAM_PATTARN = r'set_session=(.*)'
TOKEN_PARAM_PATTARN = r'token=(.*)'

# config Data for core system
L_PORT = int(conf.get('core', 'listen_port'))
D_PORT = conf.get('core', 'forward_port')
EXPIRE_TIME = int(conf.get('core', 'session_expire'))
APIMODE_LIMIT = int(conf.get('core', 'api_limit'))

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

# phpmyadmin head
pma_head = re.compile(PMA_PATTARN)
phpmyadmin_head = re.compile(PHPMYADMIN_PATTARN)
version_head = re.compile(VERSON_PATTARN)
get_pma_head = re.compile(GET_PMA_PATTARN)
post_head = re.compile(POST_PATTARN)
dot_head = re.compile(DOT_PATTARN)
db_head = re.compile(DB_PATTARN)
ajax_head = re.compile(AJAX_PATTARN)
ajax_param_head = re.compile(AJAX_PARAM_PATTARN)
ajax2_param_head = re.compile(AJAX2_PARAM_PATTARN)
pma_param_head = re.compile(PMA_PARAM_PATTARN)
token_param_head = re.compile(TOKEN_PARAM_PATTARN)

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

def create_session(ip_addr, fow_port):
    # Redis
    ip_port = ip_addr + ':' + str(fow_port)
    if p_sql.exists(ip_port):
        json_data = p_sql.get(ip_port)
        return json.loads(json_data)
    else:
        session_id = uuid.uuid4().hex

        # json
        ret = {"Port": fow_port, "Session": session_id}
        p_sql.set(ip_port, json.dumps(ret, ensure_ascii=False))
        p_sql.expire(ip_port, EXPIRE_TIME)

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

# translate localhost/phpmyadmin->localhost:8080
def pma_trans(head):
    if pma_head.search(head) or version_head.search(head) or dot_head.search(head) or db_head.search(head):
        return 8880, head
    elif re.search('ajax_request=', head):
        return 8880, head
    elif re.search('GET /phpmyadmin.css.php', head):
        return 8880, head
    elif phpmyadmin_head.search(head):
        if re.search('GET /phpMyAdmin/', head):
            head = re.sub('GET /phpMyAdmin/', 'GET /', head)
        elif get_pma_head.search(head):
            head = re.sub('GET /phpMyAdmin', 'GET /', head)
            return 8880, head
        elif ajax_param_head.search(head):
            param = ajax_param_head.match(head)
            param_group = param.group()
            param_line = param_group.splitlines()
            head = re.sub('POST /phpMyAdmin', 'GET /ajax.php/?'+param_line, head)

        return 8880, head

    elif re.search('/phpmyadmin', head):
        if re.search('GET /phpmyadmin/', head):
            head = re.sub('GET /phpmyadmin/', 'GET /', head)
        elif re.search('GET /phpmyadmin', head):
            head = re.sub('GET /phpmyadmin', 'GET /', head)
        elif ajax_param_head.search(head):
            param = ajax_param_head.match(head)
            param_group = param.group()
            param_line = param_group.splitlines()
            head = re.sub('POST /phpmyadmin', 'GET /ajax.php/?'+param_line, head)

        return 8880, head


    elif path_head.search(head) and re.search('doc/html/index.html', head):
        return 8880, head

    elif post_head.match(head):
        if ajax2_param_head.search(head):
            a_param = re.match(r'key=(.*)', head)
            if a_param != None:
                a_param_group = a_param.group()
                a_param_line = a_param_group.splitlines()
                head = re.sub('POST /phpMyAdmin', 'GET /ajax.php/?'+a_param_line, head)
            else:
                head = re.sub('POST /phpMyAdmin', 'GET /ajax.php', head)
                return 8880, head

        elif re.search('version_check.php', head):
            c_param = re.match(r'server=(.*)', head)
            if c_param != None:
                c_param_group = c_param.group()
                c_param_line = c_param_group.splitlines()
                head = re.sub('POST /version_check.php', 'GET /version_check.php/?'+c_param_line, head)
            else:
                return 8880, head

        elif re.match('logout.php', head):
            token_param = re.match('token=', head)
            token_param_group = token_param.group()
            token_param_line = token_param_group.splitlines()
            head = re.sub('POST /logout.php', 'GET /logout.php/?'+token_param_line, head)

        elif re.match('set_session=', head):
            p_param = re.match('set_session=', head)
            p_param_group = p_param.group()
            p_param_line = p_param.splitlines()
            head = re.sub('POST /index.php', 'GET /index.php/?'+p_param_line, head)
            return 8880, head

        elif re.match('logout.php', head):
            token_param = re.match('token=', head)
            token_param_group = token_param.group()
            token_param_line = token_param_group.splitlines()
            head = re.sub('POST /version_check.php', 'GET /logout.php/?'+token_param_line, head)

        return 8880, head

    else:
        return int(random.choice(ast.literal_eval(D_PORT))), head

# accept socket
def accept_req(cs):
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.settimeout(2)

    unique_id = uuid.uuid4().hex
    ip_addr = cs.getpeername()[0]
    head = cs.recv(4096)
    head_alt = head

    # translate /phpmyadmin->:8080/
    fow_port, head = pma_trans(head)
    # session_create
    session = create_session(ip_addr, fow_port)

    # print session

    # Request Header Create
    s_sql = 'select API_mode from session where IP_address = %s and SESSION_id = %s'
    c_sql.execute(s_sql, (ip_addr, session['Session']))
    log = c_sql.fetchone()
    if log == None:
        sql = 'insert into session (IP_address, SESSION_id, API_mode) values (%s, %s, %s)'
        try:
            c_sql.execute(sql, (ip_addr, session['Session'], 0))
            conn.commit()
            c_sql.execute(s_sql, (ip_addr, session['Session']))
            log = c_sql.fetchone()
        except:
            print("")

    msg = ''
    for header in head:
        msg = msg + header
    msg_alt = ''
    for header_alt in head_alt:
        msg_alt = msg_alt + header_alt
    # Forward Port Translate
    if host_head.search(msg):
        msg = re.sub(str(L_PORT), str(session['Port']), msg)
    #print(msg)

    if log[0] > APIMODE_LIMIT or fow_port == 8880:

        if msg.__len__() > 0:
            request_line, headers_alone = msg.split('\r\n', 1)
            #print(headers_alone)
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
                session['Session'], path_head.search(msg_alt).group(2), path_head.search(msg_alt).group(1), unique_id))
            else:
                c_sql.execute(sql, (
                session['Session'], path_head.search(msg_alt).group(2), path_head.search(msg_alt).group(1), 'null'))
            conn.commit()

        # fake API change (if Fuck Data is in)
        if api_head.search(msg) and fow_port != 8880:
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

            #data is response header
            print("test response header")
            print(data)
        except socket.timeout:
            break
        r = response_code.search(data)
        if r != None:
            if session['Port'] == 8880 and log[0] <= 10:
                try:
                    count_up = "update session set API_mode = %s  where SESSION_id = %s"
                    c_sql.execute(count_up, (11, session['Session'],))
                    conn.commit()
                except:
                    print("")
            elif check_response(r.group(1)):
                print(r.group(1))
                count_up = "update session set API_mode = API_mode + 1  where SESSION_id = %s"
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

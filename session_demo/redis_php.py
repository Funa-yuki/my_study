import socket
import re
import redis
import time


RESPONSECODE_PATTARN = r'HTTP/1.1 ([0-9]{3}) (.*)'
HTTP_PATTARN = r'Host: (.*):'
response_code = re.compile(RESPONSECODE_PATTARN)
host_head = re.compile(HTTP_PATTARN)

p_sql = redis.Redis('localhost', 6379, 0)
lport = 8080
fport = 8000

def fake_session():
    print("1")

def check_response(response_code):
    if response_code == '404':
        return True
    elif response_code == '403':
        return True
    elif response_code == '401':
        return True
    else:
        return False

def accept_req(cs):
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.settimeout(2)
    head = cs.recv(4096)
    msg = ''
    for header in head:
        msg = msg + header

    if host_head.search(msg):
        msg = re.sub(str(lport), str(fport), msg)

    msglen = msg.__len__()
    total_sent = 0
    # http connect
    ss.connect((socket.gethostname(), fport))
    while total_sent < msglen:
        sent = ss.send(msg[total_sent:])
        if sent == 0:
            raise RuntimeError("Error")
        total_sent = total_sent + sent
    chunks = []
    total_received = 0

    responseMessage = ""
    responseMessage = responseMessage.encode("utf-8")

    # response
    while True:
        try:
            data = ss.recv(32768)
        except socket.timeout:
            break
        r = response_code.search(data)
        if r != None:
            if check_response(r.group(1)):
                # redis change
                
                res_data = data
                r_data = res_data.split("\r\n\r\n")
                r_header = r_data[0] +'\r\n\r\n'
                r_header = re.sub("HTTP/1.1 404 Not Found", "HTTP/1.1 200 OK", r_header)
                fake_body = p_sql.get("fake_def")
                fake_response = r_header + fake_body
                print fake_response

                print data
                cs.send(data)
            else:
                print data
                cs.send(data)
    ss.close()


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', lport))
    s.listen(1)
    while True:
        cs, client_address = s.accept()
        accept_req(cs)
        cs.close()

    print socket.gethostname()

    while True:
        time.sleep(0.1)

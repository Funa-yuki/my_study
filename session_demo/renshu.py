# Forwarding Service
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

print(api_head)

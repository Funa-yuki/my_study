import cgi
import json
from http.cookies import SimpleCookie, Morsel, CookieError
from urllib.parse import parse_qs, urljoin

class Request:
    def __init__(self, environ=None, charset='utf-8'):
        self.environ = None if environ is None else environ
        self._body = None
        self.charset = charset

    @property
    def path(self):
        return self.environ['PATH_INFO'] or '/'

    @property
    def client_ip_addr(self):
        return self.environ['REMOTE_ADDR']

    @property
    def method(self):
        return self.environ['REQUEST_METHOD'].upper()

    @property
    def forms(self):
        params = {}
        if self.body:
            body = self.body.decode()
            if '&' in body:
                form = body.split('&')
            else:
                form = [body]
            for param in form:
                elements = param.split("=")
                params[elements[0]] = elements[1]
        return params

    @property
    def query(self):
        return parse_qs(self.environ['QUERY_STRING'])

    @property
    def body(self):
        if not self._body and self.environ['REQUEST_METHOD'].upper() == "POST":
            content_length = int(self.environ.get('CONTENT_LENGTH', 0))
            self._body = self.environ['wsgi.input'].read(content_length)
        return self._body

    @property
    def text(self):
        return self.body.decode(self.charset)

    @property
    def json(self):
        return json.loads(self.body)

    @property
    def cookies(self):
        # return Set-Cookie: key=value
        cookies = SimpleCookie(self.environ.get('HTTP_COOKIE', ''))
        return cookies

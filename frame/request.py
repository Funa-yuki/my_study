import cgi
import json
from http.cookies import SimpleCookie, Morsel, CookieError
from urllib.parse import parse_qs, urljoin, unquote as urlunquote
from io import BytesIO
from tempfile import TemporaryFile

class Request:
    MEMFILE_MAX = 102400
    def __init__(self, environ=None, charset='utf-8'):
        self.environ = None if environ is None else environ
        #self._body = None
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
        query = self.environ.get('QUERY_STRING', '')
        print(self.environ)
        params = {}
        if self.body:
            print(self.body)
            body = self.body.decode()
            body = urlunquote(body)
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
        return parse_qs(urlunquote(self.environ['QUERY_STRING']))

    '''
    @property
    def _body(self):
        try:
            read_func = self.environ['wsgi.input'].read
        except KeyError:
            self.environ['wsgi.input'] = BytesIO()
            return self.environ['wsgi.input']
        body_iter = self._iter_chunked if self.chunked else self._iter_body
        body, body_size, is_temp_file = BytesIO(), 0, False
        for part in body_iter(read_func, self.MEMFILE_MAX):
            body.write(part)
            body_size += len(part)
            if not is_temp_file and body_size > self.MEMFILE_MAX:
                body, tmp = TemporaryFile(mode='w+b'), body
                body.write(tmp.getvalue())
                del tmp
                is_temp_file = True
        self.environ['wsgi.input'] = body
        body.seek(0)
        return body
        '''

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

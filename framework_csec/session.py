from http.cookies import SimpleCookie, Morsel, CookieError
from urllib.parse import parse_qs, urljoin

'''
def set_cookie(self, name, value, secret=None, digestmod=hashlib.sha256, **options):
        if not self._cookies:
            self._cookies = SimpleCookie()

        self._cookies[name] = value
        options = {}
        for key, value in options.items():
            if key in ('max_age', 'maxage'): # 'maxage' variant added in 0.13
                key = 'max-age'
                if isinstance(value, timedelta):
                    value = value.seconds + value.days * 24 * 3600
            if key == 'expires':
                value = http_date(value)
            if key in ('same_site', 'samesite'): # 'samesite' variant added in 0.13
                key, value = 'samesite', (value or "none").lower()
                if value not in ('lax', 'strict', 'none'):
                    raise CookieError("Invalid value for SameSite")
            if key in ('secure', 'httponly') and not value:
                continue
            self._cookies[name][key] = value

            #_cookies[name] = value
            #_cookies[name][key] = option_value
            #{name: {key:value, key2, value2}, ..., ..., }
'''

if __name__=="__main__":
    cookies = SimpleCookie()
    cookies['name'] = 'value'
    print(cookies)
    

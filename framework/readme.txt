ルーティング関数内のローカル変数を外部で監視できるWebアプリケーションフレームワークを作りました。
ルーティング関数の戻り値に修正を加えることで、全てのルーティング関数で使われた変数を一つの監視用関数で確認することができるようになります。
wsgiの仕様に基づいたBottle風のPython製のWebアプリケーションフレームワークです。

test.pyを実行するとlocalhost:8080にWebアプリケーションを立てます。

importは以下のようになります。
テンプレートはbottleのjinja2templateを使っています。
したがってテンプレートを利用する際はbottleのインストールが必要です。
-----------------------------------------------------
例)
from app import *
from app import response
from check import *

from wsgiref.simple_server import make_server
from bottle import jinja2_template as template

app = App()
-----------------------------------------------------


パス、メソッド、ルーティング関数を記述すると、それに基づいたルーティングを行います。
下はパスが/index、メソッドがGET、"Hello"という文字列をレスポンスボディとして返却するルーティング関数です。
-----------------------------------------------------
例)
@app.route("^/index$", "GET")
def index(request):
    name = "user"
    return "Hello {}".format(name)
-----------------------------------------------------


変数の監視はapp.addCheckデコレータを利用します。
-----------------------------------------------------
例)
@app.addCheck
def check1(user):
    print(user.locals.get('^/index$'))
-----------------------------------------------------


以下で実行します。localhost:8080で立ち上げる例です。
-----------------------------------------------------
例)
if __name__=="__main__":
    port = 8080
    with make_server('', port, app) as httpd:
        print('Serving HTTP on port {}'.format(port))
        httpd.serve_forever()
-----------------------------------------------------


参考として以下のサイトを利用して作りました。
参考url:
https://c-bata.link/webframework-in-python/#
https://github.com/bottlepy/bottle/blob/master/bottle.py
https://taisablog.com/archives/30

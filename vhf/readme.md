# このフレームワークの使い方
このフレームワーク(vhf)は，アプリケーション開発者が実装したソースコードを自動で解析して修正するWebアプリケーションフレームワークです．

このマークダウンに記述されていることは以下です．
- vhfをダウンロードする
- ローカル上でアプリケーションを実行する
- アプリケーション開発者が実装したソースコードを修正する

## ソースコードをダウンロードする
ソースコードをgitlabから手元のPCにダウンロードします。
gitを利用するので，インストールしていない人はgitをインストールしてください．

ソースコードがあるリポジトリには，ソースコード以外のものも入っているのでソースコードだけをPCにダウンロードします。

下をターミナルで実行してください。（下のコマンドはmacとlinuxを前提としているので，windowsのPCを使っている人は適宜読み替えてください）

```sh:ソースコードのクローン
# 空ディレクトリを作る
mkdir vhf_dir

# 作ったディレクトリに移動する
cd vhf_dir

# 空リポジトリを作って初期化
git init

# 一部だけを取得できるようにsparsecheckoutを設定する．
git config core.sparsecheckout true
cat .git/config

# 下のように出力されていたらOK
# [core]
#       ...
#       ...
#       sparsecheckout = true

# 取得元のリポジトリを設定する
git remote add origin https://gitlab.koidelab.net/kubota/study.git

# 取得したいディレクトリをsparse-sparsecheckoutに設定する
echo vhf > .git/info/sparse-checkout

# pullする
git pull origin master

# ダウンロードできているか確認する
ls
```

## vhfでwebアプリケーションを作って，ローカルで実行する
webアプリケーションをvhfで作成してローカルで実行します．

```sh:
#vhf-dirで
cd vhf

# アプリケーションを作成する
touch my_server.py

# 好きなエディタでmy_server.pyを編集する
vi my_server.py
```

my_server.pyを記述します．
実行環境はPython3.7です．

リクエストパスとメソッド，コールバック関数を対応づけます．

下の例ではリクエストパスが/helloでリクエストメソッドがGETの時，helloという関数が呼び出されます．

このリクエストパスとリクエストメソッドに応じて呼び出される関数をコールバック関数と言います．

vhfの仕様でコールバック関数の引数にはrequestが必要です．

```py:my_server.py
# vhfをimportする
from app import *

# @app.route("パスの正規表現",  "リクエストメソッド")
# def コールバック関数(request):
#   コールバック関数内の処理
#   return "webブラウザに返却するページ"
@app.route("^/hello$", "GET")
def hello(request):
  return "Hello"

if __name__=="__main__":
  app.run(port=8000)
```

```sh: ローカルで実行
python3 my_server.py
```
webブラウザで'localhost:8000/hello'を実行
ブラウザにHelloと表示されていたらOK

## アプリケーションを修正する
vhfはnode_fixer.py内でコールバック関数を修正します．

node_fixer.pyの21行目以降にコールバック関数を修正する関数を追加します．

記述例は下です．

```py:node_fixer.py
@node_fixer.add
def fix_hoge(ast_callbacks):
  new_ast_callbacks = ...
  ...
  ...
  return new_ast_callbacks
```
node_fixer.addデコレータがコールバック関数を修正する関数をvhfに追加します．

node_fixer.addの下の関数がコールバック関数を修正する関数（今回の場合，fix_hoge関数）です．

この関数の引数はast_callbacksというリストを持っています．

この引数はリストで，要素はそれぞれコールバック関数とリクエストパス，リクエストメソッドです．
引数ast_callbacksは以下のようになっています．
```py:
ast_callbacks = [{"path": "^/hello$", "method": "GET", "ast": ast状態のコールバック関数}, ..., {"path": ..., ..., "ast": ast状態のコールバック関数}]
```

astとは抽象構文木（Abstract Syntax Tree）の略です．

このastを修正することで，コールバック関数を修正します．
今回は修正の例としてrewrite_print_to_reverse_print()関数を参考にします．

この関数はコールバック関数内のprint()関数をreverse_print()関数に変更します．
reverse_print()関数はprint関数の文字列を逆から出力する関数で，inserted_functions.pyに記述されています．
reverse_print()関数の具体的なソースコードは以下のようになっています．
```py:inserted_functions.py
def reverse_print(s, *args, **kwargs):
    if isinstance(s, str):
        print(s[::-1], *args, **kwargs)
    else:
        print("Not Str")
        print(s, *args, **kwargs)
```
 rewrite_print_to_reverse_print()関数は，コールバック関数内部でprint()関数を見つけるとreverse_print()に変更します．

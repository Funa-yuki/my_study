# このフレームワークの使い方
このフレームワーク(vhf)は，アプリケーション開発者が実装したソースコードを自動で解析して修正するWebアプリケーションフレームワークです．
このマークダウンはvhfをダウンロードしてローカル上で実行する方法と，アプリケーション開発者が実装したソースコードを修正する部分の記述方法が記述されています．

## ソースコードのダウンロード
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

```sh: vhfディレクトリに移動
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

```Python3.7:my_server.py
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

## アプリケーションを修正する
vhfはnode_fixer.py内部で

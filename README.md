<!-- omit in toc -->
# nature-remo-controller

NatureRemoクラウドサービスに接続して家電を操作する

<!-- omit in toc -->
## 目次

- [1. インストール](#1-インストール)
  - [1.1. Pythonのインストール](#11-pythonのインストール)
  - [1.2. ライブラリのインストール](#12-ライブラリのインストール)
- [2. Nature Remoの準備](#2-nature-remoの準備)
  - [アクセストークンの取得](#アクセストークンの取得)
  - [環境変数設定ファイルの作成](#環境変数設定ファイルの作成)

## 1. インストール

### 1.1. Pythonのインストール

以下のページを参考にPythonをインストールする。(Windowsの事例)
<https://www.python.jp/install/windows/install.html>

### 1.2. ライブラリのインストール

~~~bash
pip install -r requirements.txt
~~~

## 2. Nature Remoの準備

NarureRemoのWebAPIを利用するために以下の設定を行う

### アクセストークンの取得

以下のURLを参考にNature Remoのアクセストークンを入手する
<https://qiita.com/morinokami/items/6eb2ac6bed48d2c7534b>

### 環境変数設定ファイルの作成

環境変数ファイルを作成する

1. `.env.example`をコピーして`.env`ファイルに名称変更する
1. アクセストークンとデバイス名や照明の名前を設定する

    ~~~env
    # Nature Remo トークン
    NATURE_REMO_TOKEN = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    # 照明の名前
    ROOM_LIGHT_NAME="XXXXXXXX"
    ~~~

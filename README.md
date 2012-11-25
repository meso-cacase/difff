difff《ﾃﾞｭﾌﾌ》
======================

Webベースのテキスト比較ツールです。2つのテキストの差分をハイライト表示します。

+ http://altair.dbcls.jp/difff/  
  テキスト比較ツール difff《ﾃﾞｭﾌﾌ》  
  本レポジトリにあるCGIが実際に稼働しています。

+ http://gigazine.net/news/20120416-difff/  
  GIGAZINEで difff《ﾃﾞｭﾌﾌ》が紹介されました：  
  “名前はちょっとネタっぽいですが、実用性は高く、日本語のテキストでもOK”

著者が管理している
[difff《ﾃﾞｭﾌﾌ》のウェブサイト](http://altair.dbcls.jp/difff/)
はどなたでも無償で利用でき、入力テキストも一切サーバに残りませんが、
部外秘の文書をどうしても社内のサーバで ﾃﾞｭﾌﾌ したいというような要望が
多かったため、ソースを公開することにしました。どうぞご利用ください。

difff《ﾃﾞｭﾌﾌ》は差分検出にUNIXのdiffコマンドを利用しています。
diffコマンドは2つのファイルの差分を行単位で検出するプログラムです。
しかし、比較する文書をいったんファイルに書き出すのは秘匿性の点から
好ましくないので、difff《ﾃﾞｭﾌﾌ》ではファイルを書き出すのではなく
FIFO（名前付きパイプ）を作成してdiffコマンドに文書を渡しています。


サンプル画像
-----

![スクリーンショット]
(http://g86.dbcls.jp/~meso/meme/wp-content/uploads/2012/06/GGRNA_FA.png
"difff《ﾃﾞｭﾌﾌ》スクリーンショット")


動作環境
------

+ PerlのCGIが動作すること
+ UNIXのdiffコマンドが実行可能であること
+ FIFOを作成可能な、apacheからの書き込み権限のあるディレクトリがあること  
  ※ diffコマンドで文書を比較する際にFIFO（名前付きパイプ）を作成します。


インストール
------

index.html と difff.cgi をウェブ公開用のディレクトリに置きます。

difff.cgi の下記の部分を、環境にあわせて書き換えてください。

```perl
#!/usr/bin/perl
```

↑ Perlのパスを調べて記載してください。

```perl
my $diffcmd = '/usr/bin/diff' ;  # diffコマンドのパスを指定する
```

↑ diffコマンドのパスを調べて記載してください。

```perl
my $fifodir = '/tmp' ;  # FIFOを作成するディレクトリを指定する
```

↑ FIFOを作成可能な、apacheからの書き込み権限のあるディレクトリを指定。

以上で difff《ﾃﾞｭﾌﾌ》をウェブブラウザから利用できるようになります。

動かない場合、コマンドラインから下記を実行すると動作確認ができます。

```bash
% export QUERY_STRING="sequenceA=hogehoge&sequenceB=hagehage"
% ./difff.cgi
```

出力の1行目が `Content-type: text/html; charset=EUC-JP`
となっており、2行目が空白行、3行目以降にHTMLが出力されれば成功です。
3行目以降のHTMLをファイルに書き出し、ブラウザで開いて内容を確認してください。

エラーが出る場合は、エラーメッセージを参照し対処してください。

ライセンス
--------

Copyright &copy; 2004-2012 Yuki Naito
 ([@meso_cacase](http://twitter.com/meso_cacase))  
This software is distributed under modified BSD license
 (http://www.opensource.org/licenses/bsd-license.php)

#!/usr/bin/perl

# テキスト比較ツール difff《ﾃﾞｭﾌﾌ》： 2つのテキストの差分をハイライト表示するCGI
#
# 比較するテキストとして、HTTPリクエストから sequenceA および sequenceB を取得し、
# diffコマンドを用いて文字ごと（英単語は単語ごと）に比較し差分をハイライト表示する
#
# 2015-06-11 Yuki Naito (@meso_cacase) difff.plをもとにdelete.cgiを作成

use warnings ;
use strict ;
use Digest::MD5 qw(md5_hex) ;

my $url = './' ;

# HTTPリクエストを取得
my %query = get_query_parameters() ;

# 削除パスワードのhashを取得。ファイル名の一部となっている
my $md5 = md5_hex($query{'passwd'}) ;
(my $filename = $ENV{'HTTP_REFERER'}) =~ s{.*/}{} ;

# 削除を実行
(-f "data/${md5}_${filename}") and unlink "data/${md5}_${filename}"
	or print_html("ページを削除できませんでした。パスワードをご確認ください (1)") ;
(-l "data/$filename") and unlink "data/$filename"
	or print_html("ページを削除できませんでした。パスワードをご確認ください (2)") ;

# 結果を表示
print_html("ページを削除しました") ;

exit ;

# ====================
sub get_query_parameters {  # CGIが受け取ったパラメータの処理
my $buffer = '' ;
if (defined $ENV{'REQUEST_METHOD'} and
	$ENV{'REQUEST_METHOD'} eq 'POST' and
	defined $ENV{'CONTENT_LENGTH'}
){
	eval 'read(STDIN, $buffer, $ENV{"CONTENT_LENGTH"})' or
	print_html('ERROR : get_query_parameters() : read failed') ;
} elsif (defined $ENV{'QUERY_STRING'}){
	$buffer = $ENV{'QUERY_STRING'} ;
}
length $buffer > 1000000 and print_html('ERROR : input too large') ;
my %query ;
my @query = split /&/, $buffer ;
foreach (@query){
	my ($name, $value) = split /=/ ;
	if (defined $name and defined $value){
		$value =~ tr/+/ / ;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack('C', hex($1))/eg ;
		$name  =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack('C', hex($1))/eg ;
		$query{$name} = $value ;
	}
}
return %query ;
} ;
# ====================
sub print_html {  # HTMLを出力
my $message = $_[0] // '' ;

#- ▼ HTML出力
my $html = <<"--EOS--" ;
<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN'>
<html lang=ja>

<head>
<meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
<meta http-equiv='Content-Style-Type' content='text/css'>
<meta name='author' content='Yuki Naito'>
<title>difff《ﾃﾞｭﾌﾌ》</title>
<style type='text/css'>
<!--
	* { font-family:verdana,arial,helvetica,sans-serif }
	p { font-size:10pt }
	.message {
		width:500px;
		padding:10pt;
		border:dotted 1px #8c93ba;
	}
	a  { color:#3366CC }
	.k { color:black; text-decoration:none }
-->
</style>
</head>

<body>

<div id=top style='border-top:5px solid #00BBFF; padding-top:10px'>
<font size=5>
	<a class=k href='$url'>
	テキスト比較ツール difff《ﾃﾞｭﾌﾌ》</a></font><!--
--><font size=3>ver.6.1</font>
&emsp;
<font size=1 style='vertical-align:top'>
	<a style='vertical-align:top' href='${url}en/'>English</a> |
	Japanese
</font>
&emsp;
<font size=1 style='vertical-align:top'>
<a style='vertical-align:top' href='${url}v5/'>旧バージョン</a>
</font>
<hr><!-- ________________________________________ -->
</div>

<p class=message><b>メッセージ：</b><br>$message</p>

<p><a href='$url'>difff《ﾃﾞｭﾌﾌ》トップへ</a></p>

</body>
</html>
--EOS--

print "Content-type: text/html; charset=utf-8\n\n$html" ;
#- ▲ HTML出力

exit ;
} ;
# ====================

#!/usr/bin/perl

# テキスト比較ツール difff《ﾃﾞｭﾌﾌ》： 2つのテキストの差分をハイライト表示するCGI
#
# 比較するテキストとして、HTTPリクエストから sequenceA および sequenceB を取得し、
# diffコマンドを用いて文字ごと（英単語は単語ごと）に比較し差分をハイライト表示する
#
# 2012-10-22.@meso_cacase

use warnings ;
use strict ;
use POSIX ;

my $diffcmd = '/usr/bin/diff' ;  # diffコマンドのパスを指定する
my $fifodir = '/tmp' ;  # FIFOを作成するディレクトリを指定する

# ▼ EUC-JPの1文字にマッチする正規表現を定義しておく
my $ascii = '[\x00-\x7F]' ;  # ASCII文字の集合
my $twobyte = '(?:[\x8E\xA1-\xFE][\xA1-\xFE])' ;  # 2バイトEUC-JP文字の集合
my $threebyte = '(?:\x8F[\xA1-\xFE][\xA1-\xFE])' ;  # 3バイトEUC-JP文字の集合
my $eucjp = "(?:$ascii|$twobyte|$threebyte)" ;  # EUC-JP文字全体の集合
# ▲ EUC-JPの1文字にマッチする正規表現を定義しておく

# ▼ HTTPリクエストからクエリを取得し整形してFIFOに送る
my %query = get_query_parameters() ;

my $fifopath_a = "$fifodir/difff.$$.A" ;  # $$はプロセスID
my @a_split = split_text( escape_char($query{'sequenceA'}) ) ;
my $a_split = join("\n", @a_split) . "\n" ;
fifo_send($a_split, $fifopath_a) ;

my $fifopath_b = "$fifodir/difff.$$.B" ;  # $$はプロセスID
my @b_split = split_text( escape_char($query{'sequenceB'}) ) ;
my $b_split = join("\n", @b_split) . "\n" ;
fifo_send($b_split, $fifopath_b) ;
# ▲ HTTPリクエストからクエリを取得し整形してFIFOに送る

# ▼ diffコマンドの実行
(-e $diffcmd) or print_error_html("ERROR : $diffcmd : not found") ;
(-x $diffcmd) or print_error_html("ERROR : $diffcmd : not executable") ;
my @diffout = `$diffcmd -d $fifopath_a $fifopath_b` ;
my @diffsummary = grep /(^[^<>-]|<\$>)/, @diffout ;
# ▲ diffコマンドの実行

# ▼ 差分の検出とHTMLタグの埋め込み
my ($a_start, $a_end, $b_start, $b_end) = (0,0,0,0) ;
foreach (@diffsummary){  # 異なる部分をハイライト表示する
	if ($_ =~ /^((\d+),)?(\d+)c(\d+)(,(\d+))?$/){  # 置換している場合
		$a_end = $3 || 0 ;
		$a_start = $2 || $a_end ;
		$b_start = $4 || 0 ;
		$b_end = $6 || $b_start ;
		$a_split[$a_start - 1] = '<em>' . ($a_split[$a_start - 1] // '') ;
		$a_split[$a_end - 1] .= '</em>' ;
		$b_split[$b_start - 1] = '<em>' . ($b_split[$b_start - 1] // '') ;
		$b_split[$b_end - 1] .= '</em>' ;
	} elsif ($_ =~ /^((\d+),)?(\d+)d(\d+)(,(\d+))?$/){  # 欠失している場合
		$a_end = $3 || 0 ;
		$a_start = $2 || $a_end ;
		$b_start = $4 || 0 ;
		$b_end = $6 || $b_start ;
		$a_split[$a_start - 1] = '<em>' . ($a_split[$a_start - 1] // '') ;
		$a_split[$a_end - 1] .= '</em>' ;
	} elsif ($_ =~ /^((\d+),)?(\d+)a(\d+)(,(\d+))?$/){  # 挿入している場合
		$a_end = $3 || 0 ;
		$a_start = $2 || $a_end ;
		$b_start = $4 || 0 ;
		$b_end = $6 || $b_start ;
		$b_split[$b_start - 1] = '<em>' . ($b_split[$b_start - 1] // '') ;
		$b_split[$b_end - 1] .= '</em>' ;
	} elsif ($_ =~ /> <\$>/){  # 改行の数をあわせる処理
		my $i = ($a_start > 1) ? $a_start - 2 : 0 ;
		while ($i < scalar(@a_split) and not $a_split[$i] =~ s/<\$>/<\$><\$>/){ $i ++ }
	} elsif ($_ =~ /< <\$>/){  # 改行の数をあわせる処理
		my $i = ($b_start > 1) ? $b_start - 2 : 0 ;
		while ($i < scalar(@b_split) and not $b_split[$i] =~ s/<\$>/<\$><\$>/){ $i ++ }
	}
}
# ▲ 差分の検出とHTMLタグの埋め込み

my $a_final = join '', @a_split ;
my $b_final = join '', @b_split ;

# 変更箇所が<td>をまたぐ場合の処理
while ( $a_final =~ s{(<em>[^<>]*)<\$>(([^<>]|<\$>)*</em>)}{$1</em><\$><em>$2}g ){}
while ( $b_final =~ s{(<em>[^<>]*)<\$>(([^<>]|<\$>)*</em>)}{$1</em><\$><em>$2}g ){}

my @a_final = split /<\$>/, $a_final ;
my @b_final = split /<\$>/, $b_final ;

my $par = ((scalar @a_final) > (scalar @b_final)) ? scalar @a_final : scalar @b_final ;

my $table = '' ;
foreach (0..$par-1){
	defined $a_final[$_] or $a_final[$_] = '' ;
	defined $b_final[$_] or $b_final[$_] = '' ;
	$a_final[$_] =~ s{(\ +</em>)}{escape_space($1)}ge ;
	$b_final[$_] =~ s{(\ +</em>)}{escape_space($1)}ge ;
	$a_final[$_] =~ s{<em>\s*</em>}{}g ;
	$b_final[$_] =~ s{<em>\s*</em>}{}g ;
	$table .=
"<tr>
	<td>$a_final[$_]</td>
	<td>$b_final[$_]</td>
</tr>
" ;
}

print_html($table) ;

exit ;

# ====================
sub get_query_parameters {  # CGIが受け取ったパラメータの処理
my $buffer = '' ;
if (defined $ENV{'REQUEST_METHOD'} and $ENV{'REQUEST_METHOD'} eq 'POST' and defined $ENV{'CONTENT_LENGTH'}){
	eval 'read(STDIN, $buffer, $ENV{"CONTENT_LENGTH"})' or
	print_error_html('ERROR : get_query_parameters() : read failed') ;  # readに失敗した場合のエラー表示
} elsif (defined $ENV{'QUERY_STRING'}){
	$buffer = $ENV{'QUERY_STRING'} ;
}
length $buffer > 1000000 and print_error_html('ERROR : input too large') ;  # サイズが大きすぎ
my %query ;
my @query = split /&/, $buffer ;
foreach (@query){
	my ($name,$value) = split /=/ ;
	if (defined $name and defined $value){
		$value =~ tr/+/ / ;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack('C', hex($1))/eg ;
		$name =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack('C', hex($1))/eg ;
		$query{$name} = $value ;
	}
}
return %query ;
} ;
# ====================
sub split_text {
my $text = join('', @_) // '' ;
$text =~ s/\n/<\$>/g ;  # もともとの改行を <$> に変換して処理する
my @text ;
while ($text =~ s/^([a-z]+|<\$>|$eucjp|.)//){
	push @text, $1 ;
}
return @text ;
} ;
# ====================
sub fifo_send {  # usage: fifo_send($text, $path) ;
my $text = $_[0] // '' ;
my $path = $_[1] or print_error_html('ERROR : open failed') ;
mkfifo($path, 0600) or print_error_html('ERROR : open failed') ;
my $pid = fork ;
if ($pid == 0){
	open(FIFO, ">$path") or print_error_html('ERROR : open failed') ;
	print FIFO $text ;
	close FIFO ;
	unlink $path ;
	exit ;
}
} ;
# ====================
sub escape_char {  # < > & ' " の5文字を実態参照に変換する
my $string = $_[0] // '' ;
$string =~ s/\&/&amp;/g ;
$string =~ s/</&lt;/g ;
$string =~ s/>/&gt;/g ;
$string =~ s/\'/&apos;/g ;  # '
$string =~ s/\"/&quot;/g ;  # "
return $string ;
} ;
# ====================
sub escape_space {  # 空白文字を実態参照に変換
my $string = $_[0] // '' ;
$string =~ s/\s/&nbsp;/g ;  # 空白文字（スペース、タブ等含む）はスペースとみなす
return $string ;
} ;
# ====================
sub print_html {
my $table = $_[0] // '' ;
print 'Content-type: text/html; charset=EUC-JP

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang=ja>

<head>
<meta http-equiv="Content-Type" content="text/html; charset=EUC-JP">
<meta http-equiv="Content-Style-Type" content="text/css">
<meta name="author" content="Yuki Naito">
<title>difff output</title>
<style type="text/css">
<!--
	* { font-family:verdana,arial,helvetica,sans-serif; font-size:10pt }
	em { font-weight:bold;
		font-style:normal;
		background-color:#99FF99 }
	table { width:90%;
		table-layout:fixed;
		word-wrap:break-word;
		border-collapse:collapse;
		border-top:solid 10px #e0e0f0;
		border-bottom:solid 10px #e0e0f0 }
	td { padding:4px 15px;
		border-left:solid 15px #e0e0f0;
		border-right:solid 15px #e0e0f0 }
-->
</style>
</head>

<body>

<table cellspacing=0>
' . $table . 
'</table>

</body>
</html>
' ;
exit ;
} ;
# ====================
sub print_error_html {
my $error_text = $_[0] // '' ;
print 'Content-type: text/html; charset=EUC-JP

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>

<head>
<meta http-equiv="Content-Type" content="text/html; charset=EUC-JP">
<meta http-equiv="Content-Style-Type" content="text/css">
<meta name="author" content="Yuki Naito">
<title>difff output</title>
<style type="text/css">
<!--
	* { font-family:verdana,arial,helvetica,sans-serif; font-size:10pt }
	em { font-weight:bold;
		font-style:normal;
		background-color:#99FF99 }
-->
</style>
</head>

<body>

<p><em>
' . $error_text . 
'</em></p>

</body>
</html>
' ;
exit ;
} ;
# ====================

#!/usr/local/bin/perl -w

use strict;

use Net::FTP;
use Data::Dumper;

my $URL  = 'http://monastyrskiy.ru';
my $host = 'monastyrskiy.ru';
my $user = '';
my $pass = '';
my $pwd  = shift;
my $ftp  = Net::FTP->new($host) || die "Cannot connect to $host\n";

my $COUNTER = 1;

$ftp->login($user, $pass) or die "Cannot login ", $ftp->message;
$ftp->cwd($pwd);
my @files = $ftp->ls();

shift @files;
shift @files;

print '<div style="text-align: center;">' . "\n";
print $COUNTER . '. <img src="' . $URL . $pwd . $files[0] . '"></div>' . "\n";

$COUNTER++;
shift @files;

print "\n\n" . '<lj-cut text="Еще фото"><div style="text-align: center;">' . "\n";

foreach my $f (@files) {
  print  $COUNTER . '. <img src="' . $URL . $pwd . $f . '">' . "\n\n\n";
  ++$COUNTER;
}

print '</div><lj-like buttons="vkontakte, facebook" />' . "\n";
print '<lj-repost button="Показать друзьям"></lj-repost>' . "\n";
print '</lj-cut>' . "\n";

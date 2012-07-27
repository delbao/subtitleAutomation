#enforce declaration of every variable
#use strict;

# Language Identify
use Lingua::Identify qw(:language_identification);
# Chinese Encoding Guesses
require "codelib.pl";

# Chinese Encoding conversion
use Encode::HanConvert;

use Encode;

use Getopt::Std qw(getopts);

getopts('d');

if($opt_d){
    $debug = 1;
}

#time scale
my %scales =  ( 'h' => 3600000,
                'm' => 60000,
                's' => 1000,
                'u' => 0,
              );

# store names of a list of all files in a variable
#my $sub_dir = shift @ARGV;

my $sub_dir = "d:/complete";
#my $sub_dir ="e:/subtest/out";
#my $sub_dir = "e:/TV";

# rename directory name if special char in it, glob will fail on these chars
#if($sub_dir =~ /[\[\]]/){
#   $old_dir = $sub_dir;
#    $sub_dir =~ s/[\[\]]//g;
    #$sub_dir =~ s/[]+$//g;
#    rename $old_dir, $sub_dir or die "can not rename $old_dir to $sub_dir";
#}

unless($sub_dir =~ /\/$/){
   $sub_dir .= "\/";
}

#glob all files in the sub_dir and rename it if special chars ([, ] and space) in it.
my @all_files=<$sub_dir*>;
foreach $all_file (@all_files){
	if($all_file =~ /[ \[\]]/){
	    $old_file = $all_file;
	    $all_file =~ s/[\[\]]//g;
	    $all_file =~ s/ /./g;
	    rename $old_file, $all_file or die "can not rename $old_file to $all_file";
	}
}

print "The sub dir is $sub_dir!\n" if ($debug);

#glob files with *.dalay.* in a list]
#if having space in file name/path, shell will take it as two separate files
#so need to single quote file name

#my $cmd ='\''.$sub_dir."*.delay".'\'';
#my $cmd ="$sub_dir.delay"
#my @delay_files=glob '\''.$sub_dir."*.delay".'\'';
#my @delay_files=glob $sub_dir."*.delay";
my @delay_files=<$sub_dir*.delay>;

print "glob pattern is $sub_dir*.delay\n" if ($debug);

# empty array have false boolean value
unless(@delay_sub){
    print "no delay files exists!\n" if ($debug);
}
   
foreach $delay_sub (@delay_files) {
        open DELAY, $delay_sub or die "no delay file of specific name ($!)";
	
	my $time=<DELAY>;

	#chop off ACSII null characters in delay files, do it globally (as many as possible) with /g
	#remember to use =~ not = for matching purpose
	$time=~s/\x0//g;
	
	close DELAY;

	if($time < 360000 && $time > - 360000) {
		$delay_sub =~/(.+)\.delay/;

		subsync($1, $time);
	}
}

unlink @delay_files;

#glob files with *.eng.* in a list
$cmd='\''.$sub_dir."*.eng.srt".'\'';

print "will glob $cmd!\n" if($debug);

#my @eng_sub_files=glob $sub_dir."*.eng.srt";
my @eng_sub_files=<$sub_dir*.eng.srt>;

unless(@eng_sub_files){
    print "no english sub files exists!, this is impossible\n" if ($debug);
}

#glob files with *.chn.* in a list
#$cmd='\''.$sub_dir."*.chn.srt".'\'';
#my @chn_sub_files=glob $sub_dir."*.chn*.srt";
my @chn_sub_files=<$sub_dir*.chn.srt>;

unless(@chn_sub_files){
    print "no Chinese sub files exists!, this is possible but rare\n" if ($debug);
}

opendir DH, $sub_dir or die "Cannot open $sub_dir: $!"; #DH=dirhandle

my @file_list = readdir DH;

foreach $eng_sub (@eng_sub_files) {
    $eng_sub =~ /(.+)\.eng/;
    my $subname = $1;

    # locate the first valid english sub
    # condition: the sub lang is english
    # glob files with the same name in a list
    #$cmd='\''..'\'';
    #my @this_eng_subs=glob $subname.".eng*.srt";
    my @this_eng_subs=<$subname*.eng*.srt>;

    unless(@this_eng_subs){
	print "no other english sub exists!, this is possible but rare\n" if ($debug);
    }

    foreach $this_eng (@this_eng_subs)
    {
	# set delimiter for reading text from file
	local $/=undef;

	open SUBFILE, $this_eng;
	$text_e=<SUBFILE>;

	if(langof($text_e) eq "en"){
	    close SUBFILE;
	    print "I am finding an english sub $this_eng!\n" if ($debug);
	    
	    # reopen file for write to convert to ANSI
	    #$text1 = Encode::decode("windows-1250", $text);
	    #open SUBFILEOUT, ">$this_eng";
	    #print SUBFILEOUT "$text1";
	    #close SUBFILEOUT;
	    
	    #convert to unicode
	    #$text1 = Encode::decode_utf8($text);
	    #open SUBFILEOUT, ">$subname.uni.eng.srt";
	    #print SUBFILEOUT "$text1";
	    #close SUBFILEOUT;

    	    # rename the sub file 
	    unless($this_eng =~ /eng.srt/){
		unlink $subname.".eng.srt";
		rename $this_eng, $subname.".eng.srt" or die "can not rename $this_eng";
	    }

	    $/="\n";
	    
            # reopen to convert to lrc
	    open SUBFILE, $subname.".eng.srt";
	    conv_lrc($subname.".srt");
    	    close SUBFILE;
	    
    	    # perl's break keyword is last, not break;
	    last;
	}	
	close SUBFILE;
    }
    
    # remove all other eng subs with the same name
    foreach $this_eng (@this_eng_subs){
	# =~ return list: empty or not
	unless($this_eng =~ /eng.srt/){
	    unlink $this_eng;
        }
    }

    # locate the first valid Chinese sub
    # condition priority 1: not en
    # condition priority 2: if en, prefer big5 over gb
    # three run: first run, if not en; second run, if all en, find a big5 precedes gb
    # if both runs fail, pick the first one
    
    # grep returns a list of 
    # each corresponding chinese subtitles
    # my @chn_sub=grep {/$subname/}@chn_sub_files;
    
    # no simple solution for grep with space list, have to use glob
    # my @chn_sub=glob $subname.".chn*.srt";
    # $cmd='\''.$subname.".chn*.srt".'\'';

    my @chn_sub=<$subname.chn*.srt>;

    my $flag = 0;
    my $thrshld= 30000;
    my $sample;
    # first run
    print "first run start ................\n" if ($debug);

    foreach $this_chn(@chn_sub){
	
	local $/=undef;

	open SUBFILE, "<".$this_chn;
	$text_c=<SUBFILE>;
	close SUBFILE;

	# a large $text will render codelib::codeguess intractable
	# have to take a sample

	if(length($text_c)>thrshld){
	    $sample=substr($text_c, 0, $thrshld);
	}
	else{
	    $sample=$text_c;
	}

	if(langof($text_c) ne "tr" && langof($text_c) ne "es"){
	    $flag=1;

	    print "I find a Chinese sub detected as not turkey or spanish! $this_chn\n" if($debug);

	    # check if big5 precedes gb
	    if(isBig5($sample)){
		$text_c = big5_to_gb($text_c);		
		
		print "but it is big5 need to convert\n" if ($debug);

		unlink $subname.".chn.srt";
		open SUBCHNOUT, ">$subname".".chn.srt";

		print SUBCHNOUT "$text_c";
		close SUBCHNOUT;
	    }
	    
	    # some encodings has abnormal behaviors after reading for unknown reason
	    # so need to use the original file

       	    # rename the sub file 
	    unless($this_chn =~ /chn.srt/){
		unlink $subname.".chn.srt";
	    	rename $this_chn, $subname.".chn.srt" or die "can not rename $this_chn";
	    }

	    last;
	}	
    }

    # second run

    if($flag == 0){
	print "second run start ................\n" if ($debug);

	foreach $this_chn(@chn_sub){
	    local $/=undef;

	    open SUBFILE, "<$this_chn";
	    $text_c=<SUBFILE>;
	    close SUBFILE;

	    if(length($text_c)>thrshld){
		$sample=substr($text_c, 0, $thrshld);
	    }
	    else{
		$sample=$text_c;
	    }

	    if(isBig5($sample)){
		$text_c = big5_to_gb($text_cc);
		
		print "I find a big5 sub identified as english $this_chn !" if ($debug);
		unlink $subname.".chn.srt";
		#
		open SUBCHNOUT, ">$subname".".chn.srt";

		print SUBCHNOUT "$text_c";
		close SUBCHNOUT;

		$flag=1;
		last;
	    }
	}
    }

    # third run, just use chn_sub[0] mostly .chn.srt

    if($flag == 0){
	print "third run start ................\n" if ($debug);
       	
	local $/=undef;
	    
	open SUBFILE, "<$chn_sub[0]";
	$text_c=<SUBFILE>;
	close SUBFILE;
	
	# no need for big5 check...
       	# rename the sub file 
	unless($chn_sub[0] =~ /chn.srt/){
	    unlink $subname.".chn.srt";
	    rename $chn_sub[0], $subname.".chn.srt"
	}
    }

    # remove all other chinese sub files
    foreach $this_chn (@chn_sub){
	unless($this_chn =~ /chn.srt/){
	    unlink $this_chn;
        }
    }

    #combine bilingural subtitles
    $subname =~ s/\//\\/g;
    
    # for ansi case
    # blindly convert english sub to ANSI
    $text_e1 = Encode::encode("windows-1250", $text_e);
    open SUBFILEOUT, ">$subname.srt";
    print SUBFILEOUT $text_e1, $text_c;
    close SUBFILEOUT;
    
    #handle different chinese encoding
    #chinese is unicode  
    $text_c = decode( "UTF-16LE", $text_c );
    $text_c = encode("utf8", $text_c);
    
    open SUBFILEOUT, ">$subname.uni.srt";
    print SUBFILEOUT $text_e, $text_c;
    close SUBFILEOUT;
    
    #ansi version
    #my $cmd='copy "'.$subname.".eng.srt".'"+"'.$subname.".chn.srt".'"'.' "'.$subname.'.srt"'; 
    #system $cmd;    
    #unicode version
    #$cmd='copy "'.$subname.".uni.eng.srt".'"+"'.$subname.".chn.srt".'"'.' "'.$subname.'.uni.srt"'; 
    #system $cmd;
}

closedir DH;

#if the sub is Big5 encoded?
sub isBig5{
    my @guesses = codeguess($_[0]);
    my $flag =0;
    foreach $guess(@guesses){
	# guess on big5 precedes gb, it might be big5
	if($guess eq big5){
	    $flag =1;
	}
	elsif($guess eq gb){
	    if($flag==0){
		return 0;
	    }
	    else {
		return 1;
	    }
	}
	elsif($flag==1){
	    $flag=0;
	}
    }
}

#sub resync subroutine
# @param the sub file to be delayed
# @param the delay in ms

sub subsync{
  if(open DELAY_SUB, $_[0]){
  open TEMP, ">$_[0]".'.temp';

  while (<DELAY_SUB>){
      
    # 00:01:09,040 --> 00:01:11,713
    if ( /(\d\d):(\d\d):(\d\d),(\d+)\s+-->\s+(\d\d):(\d\d):(\d\d),(\d+)/ )
    {
      my ($sh,$sm,$ss,$su,$eh,$em,$es,$eu) = ($1,$2,$3,$4,$5,$6,$7,$8);
 
      #modify start and end time
      my $s = ($su + ($ss * $scales{'s'}) + ($sm * $scales{'m'}) + ($sh * $scales{'h'})) + $_[1];
      my $e = ($eu + ($es * $scales{'s'}) + ($em * $scales{'m'}) + ($eh * $scales{'h'})) + $_[1];
 
      my $rt = 0;
      $sh    = int($s/$scales{'h'});
      $rt   += ($sh * $scales{'h'});
 
      $sm    = int(($s - $rt) / $scales{'m'});
      $rt   += ($sm * $scales{'m'});
 
      $ss    = int(($s - $rt) / $scales{'s'});
      $rt   += ($ss * $scales{'s'});
 
      $su    = ($s - $rt);
 
      $rt    = 0;
      $eh    = int($e/$scales{'h'});
      $rt   += ($eh * $scales{'h'});
 
      $em    = int(($e - $rt) / $scales{'m'});
      $rt   += ($em * $scales{'m'});
 
      $es    = int(($e - $rt) / $scales{'s'});
      $rt   += ($es * $scales{'s'});
 
      $eu    = ($e - $rt);
 
      printf TEMP "%02d:%02d:%02d,%03d --> %02d:%02d:%02d,%03d\n", $sh,$sm,$ss,$su,$eh,$em,$es,$eu;
    }
    else
    {
      print TEMP $_;
    }
  }
  close DELAY_SUB;
  close TEMP;

  my $sucessful=unlink "$_[0]";
 
#  print "I deleted $successful file(s) just now\n";

  rename "$_[0]".'.temp', $_[0];
  }
}

#for each file in the eng list, 
#------if it has a file named .delay, call subsync subrountine
#------if it has a par file name *.chn.*, call windows batch merge, the output has neither eng nor chn

#convert the eng subtitle file to lrc
sub conv_lrc{

    my $srt=shift;

    my $lrc=$srt;

    $lrc=~s/srt/lrc/;
    open OUTFILE,">$lrc" or die "Unable to open $lrc for writing\n";

    my $converted = 0;
    my $failed = 0; 
    # previous start time
    my $previous = 0;
    
    while (my $line1 = <SUBFILE>) { #number
      $line1 =~ s/[\n\r]*$//;
      if ($line1 =~ m/^\d{1,4}$/) {
         $line1 = <SUBFILE> ; #time
      }
      $line1 =~ s/[\n\r]*$//;
      if ($line1 =~ m/(\d\d):(\d\d):(\d\d),(\d\d)\d\s+-->\s+(\d\d):(\d\d):(\d\d),(\d\d)\d/) {
	 my ($hour, $min, $sec, $msec) = ($1, $2, $3, $4);
	 if($hour != "00"){
		$min = $hour * "60" + $min;
	}
	
	my $starttime  = "$min:$sec.$msec";
		
         #my $endtime = $2;
         #$starttime =~ s/\,/:/;
         #$endtime =~ s/\,/:/;
	my $text = <SUBFILE>; #text
	$text =~ s/[\n\r]*$//;
	while (my $empty = <SUBFILE>) {
            $empty =~ s/[\n\r]*$//;
            if ($empty =~ m/^$/) {
               last;
            }
            $text = "$text $empty";
	}

	$converted++;

         #print "  Subtitle #$converted: start: $starttime, Text: $text\n";

         # convert line-ends
	 # in WIN32, the line end is \r\n
	$text =~ s/\[br\]/"\r\n"/g;
	 
	
	# 5 sec subtitle merge
	if($previous == 0 || ($min * "60" + $sec) - $previous > 3) {
		$previous = $min * "60" + $sec;
		print OUTFILE "[$starttime]$text\r\n";
	}
	else {
		print OUTFILE "$text\r\n";
	}
      } else {
         if (!$converted) {
            print "  Header line: $line1 ignored\n";
         } else {
            $failed++;
            print "  failed to convert: $line1\n";
         }
      }
   }

    close OUTFILE;
}

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

getopts('dvs');

if($opt_d){
    $debug = 1;
}

if($opt_v){
    $delete = 1;
}

if($opt_s){
    $doSubtitle = 1;
}
#time scale
my %scales =  ( 'h' => 3600000,
		'm' => 60000,
		's' => 1000,
		'u' => 0,
    );

# store names of a list of all files in a variable
#my $sub_dir = shift @ARGV;

#my $sub_dir = "d:/complete";
#my $sub_dir ="e:/subtest/out";
my $sub_dir = "z:/TV";

# rename directory name if special char in it, glob will fail on these chars
unless($sub_dir =~ /\/$/){
    $sub_dir .= "\/";
}
if($doSubtitle){
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
    unless(@delay_files){
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
    }
}

# delete all files without enough subtitles
if($delete){
    my @video_files=<$sub_dir*.mp4 $sub_dir*.mkv>;

    foreach $video_file (@video_files){
	# remove the extension
	$v_name =substr($video_file, 0, -4);
	my @eng_sub=<$v_name*.eng*>;
	my @chn_sub=<$v_name*.chn*>;
	my @lrc_sub=<$v_name*.lrc*>;

	unless(@eng_sub && @chn_sub && @lrc_sub){
	    unlink <$v_name*>;
	    print "video $v_name deleted!\n" if($debug);
	}
    }
}

closedir DH;



# sub resync subroutine
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

package SubtitlesLibs;

use strict;
use warning;

our @EXPORT_OK={};

require Encode;
require Encode::Guess;

# done
# convert the input string to utf-8
# @param $octets input string in any encoding
# return $string output string in UTF8 format
sub convToUTF8{
    $octets = shift;
    my $enc = Encode::Guess::guess_encoding($octets);
    my $string = Encode::decode($enc, $octets);
    return $string;
}

# done
# read in sub files either in srt or ass and convert the startTime/stopTime/content
# to a hash list
# @param input file name
# @return subList hash list {startTime => "$min:$sec.$msec", title => content}
# stopTIme is not needed
sub readInSubFile{
    my $subFile=shift;
    my $isSrt=($subFile ~= /srt$/)? 1, 0;
    my @subLines;
    my @subList;
    my
    open SUBFILE, $subFile or die "file $subFile does not exist";
    while (<SUBFILE>){
        push @subLines, $_;
    }

    if($isSrt){
        @subList = buildFromSrt(@subLines);
    } else {
        @subList = buildFromAss(@subLines);
    }
}

# done
# build the uniform subtitle hash list from srt file
# @param[in] input srt subtitle lines
# @return output hash
sub buildFromSrt{
    my @subLines = @_;
    my $lineNum=0; # processed lineNum for each (time,content) pair, we need this b/c there might be header
    my %subLine; # sub line hash
    my @subList; # returned hash list
    foreach my $srtLine in @subLines{
        chomp;
        # match time
        if ($srtLine =~ m/(\d\d):(\d\d):(\d\d),(\d\d)\d\s+-->\s+(\d\d):(\d\d):(\d\d),(\d\d)\d/){
            push @subList, %subLine if ($lineNum);

            $lineNum++;
            %subLine=( time => '', subtitle => ''); # reset subline hash
	    my ($hour, $min, $sec, $msec) = ($1, $2, $3, $4);
	    if($hour != "00"){
		$min = $hour * "60" + $min;
	    }
	    
	    $subLine{time} = "$min:$sec.$msec";
	} elsif (lineNum){ # content
            $srtLine =~ s/<.*>.*<\/.*>//g; # remove any tag
            $srtLine =~ s/[.*]//g; # remove []

            $subLine{subtitle}="$subLine{subtitle} $srtLine";

	    # convert line-ends
	    # in WIN32, the line end is \r\n
	    # $text =~ s/\[br\]/"\r\n"/g;
        } else {
            # just ignore error or headers
        }
    }
    
    push @subList, %subLine if ($lineNum); # push last line hash
    return @subList;    
}

# undone
# sub resync subroutine
# @param the sub file to be delayed
# @param the delay in ms
sub syncDelayedSrt{
    my ($subfile, $delay)=@_;
    if(open DELAY_SUB, $subfile){
	open TEMP, ">$subfile.temp";
        
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

	my $sucessful=unlink $subfile;
        # print "I deleted $successful file(s) just now\n";

	rename "$subfile.temp", $subfile;
    }
}

# undone
#convert the eng and chinese subtitle file to lrc
sub convSrtToLrc{

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
	    
	    # remove <i> and </i>
	    $text =~ s/<(i|\/i)>//g;
	    
	    # $sub_interval sec subtitle merge
	    if($previous == 0 || ($min * "60" + $sec) - $previous > $sub_interval) {
		$previous = $min * "60" + $sec;
		print OUTFILE "[$starttime]$text\r\n";
	    }
	    else { # merge those less than $sub_interval 
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

# done
# convert ass lines to srt
# @param[in] @assLines line string list
# return @srtLines output line list, each line is a hash (begin =>, end =>, subtitle =>)
sub convAssToSrt{
    # input line arrays
    my @assLines = @_;
    my @srtLines;
    my $lineNum = 0;

    foreach my $assLine (@assLines){
        # If a line begin with 'Dialougue', extract this line's parameters
        if (@assLine ~=/^Dialogue:/) {
            convAssToSrtLine(@srtLines, $lineNum, $assLine);
        }
        elsif (@assLine ~=/^(Title:|Original)/) {
            # If a line begins with 'Title' or 'Original', it is the source for the subtitles
            print $assLine . "\n";
        }
        $lineNum++;
    }

    # post-process lines to remove errors.
    for (my $i = 0; $i < scalar @srtLines; $i++)
    {
        my $srtLine = $srtLines[$i];
        my $prevLine = undef;
        $prevLine = $srtLines[$i-1] if $i > 0;

        # if the begin of the previous line is the same as the begin of this line,
        # merge the two lines.
        if ($prevLine && $prevLine->{begin} eq $srtLine->{begin})
        {
            # merge subtitles
            $prevLine->{subtitle} .= "\n" . $srtLine->{subtitle};

            # remove line $i from the list
            @srtLines = (@srtLines[0..$i-1], @srtLines[$i+1..$#srtLines]);

            # resync things for next test
            $i--;
            $prevLine = undef;
            $prevLine = $srtLines[$i-1] if $i > 0;
        }

        # if the end of the previous line is smaller than the begin of this line,
        # change the end of the previous line to be the begin of this line.
        if ($prevLine && $prevLine->{end} gt $srtLine->{begin})
        {
            $prevLine->{end} = $srtLine->{begin};
        }
    }
    return @srtLines;
}

# undone pending: convert to universal time format
# Extract data for one line of the .ass sub
# @param[out] \@srtLines output srt string list
# @param[in] $lineNumber the current line number
# @param[in] $content input ass line string
# @param[in] $DEBUG show debug info if true
# return @srtLines output line list, each line is a hash (begin =>, end =>, subtitle 
sub convAssToSrtLine(\@$$$) {
    # Deal with the number of rows
    # From. ass of the original content
    my ($srtLines, $lineNumber, $content, $DEBUG) = @_;

    my $begin;
    my $end;
    my $subtitle;
    my $currentTime;

    # Solved starting time, ending time, subtitle format, subtitles content
    if ($content =~ m/Dialogue: [^,]*,([^,]*),([^,]*),([^,]*),[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,(.*)$/)
    {
        $begin    = $1;
        $end      = $2;
        $subtitle = $4;

        my $isComment = $3;

        print "\nLine: $lineNumber\n  Begin: [$begin]  End: [$end]  isComment: [$isComment]\n  Subtitle: [$subtitle]\n" if $DEBUG;

        # the separator between seconds and ms is "," -- not ".", so we change it !
        $begin =~ s/\./,/g;
        $end   =~ s/\./,/g;

        # If the time format will not be part of the hour when the two chars, make up two chars.
        if ( $begin =~ m/^\d{1}:/ ) {
            $begin = "0" . $begin;
        }

        if ( $end =~ m/^\d{1}:/ ) {
            $end = "0" . $end;
        }

        # First filter out the end of every title to the digital sign in order to follow-up to the output under a variety of formats on different platforms
        $subtitle =~ s/\r$//g;

        # If there is no such setting .ass control commands, then filter out the
        $subtitle =~ s/{[^}]*}//g;

        # Comment if the subtitle format, then in the before and after the add ()
        if ( $isComment eq 'comment' ) {
            $subtitle = '(' . $subtitle . ')';
        }

        print "\nAfter:\n  Begin: [$begin]  End: [$end]  isComment: [$isComment]\n  Subtitle: [$subtitle]\n"
            if $DEBUG;

        my %line = ( begin => $begin, end => $end, isComment => $isComment, subtitle => $subtitle );
        push @$srtLines, %line;
    }
}

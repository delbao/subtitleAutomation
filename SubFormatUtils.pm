package SubFormatUtils;

use strict;
use warning;

use Params::Validate qw(:all);
use Log::Log4perl qw(:easy);

require Encode::Guess;

Log::Log4perl->easy_init($ERROR);

our @EXPORT_OK={};

=head1

=cut
sub new{
    my $self = shift;
    my $class = ref($self) || $self;

    my %options = validate(
                           @_, {
                                filename => { type => SCALAR }
                                subHash => { type => HASHREF}
                                dryrun => { default => 0 }
                               }
                          );
    my $object = {@_};
    return bless $object, $class;
}

=head1 read in sub files and convert to hash input files are either ass or srt
startTime/stopTime/content to a hash list

@param input file name

@return subList hash list {'$filename' => {'origin' =>@sublines, 'hashed' => @{time => "$min:$sec.$msec", subtitle => content}}}

=cut

sub _readInSubFiles{ 
    my $self=shift; # read in
    my $subFile=$self->filename;

    # get all ext files of the filename
    foreach (@subFileList){
        my $isSrt=($_ ~= /srt$/)? 1, 0;
        my $subfilename=$_;

        open SUBFILE, $_ or die "file $_ does not exist";
        my @subLines;
        while (<SUBFILE>){
            push @subLines, $_;
        }

        # check delay file

        _syncDelaySrt(\@subLines, $delay_ms);
        $self->subHash->[$subfilename]['origin']=@subLines;

        if($isSrt){
            $self->subHash->[$subfilename]['hashed'] = _srtToHash(@subLines);
        } else {
            $self->subHash->[$subfilename]['hashed'] = _assToHash(@subLines);
        }
    }
}

=head2 build subtitle hash structure from srt string

@param @subLines
@return @subHashList for each line

=cut

sub _srtToHash{
    my @subLines=@_;
    my $lineNum=0; # processed lineNum for each (time,content) pair, we need this b/c there might be header
    my @subList; # returned hash list
    my %subLine; # sub line hash, shared by time and content

    foreach my $srtLine in @subLines{
        chomp;
        if ($srtLine =~ m/(\d\d):(\d\d):(\d\d),(\d\d)\d\s+-->\s+(\d\d):(\d\d):(\d\d),(\d\d)\d/){
            # match time
            # push previous line
            push @subList,%subLine if ($lineNum++);

            %subLine=( time => '', subtitle => ''); # reset subline hash
            my ($hour, $min, $sec, $msec) = ($1, $2, $3, $4);
            if($hour != "00"){
                $min = $hour * "60" + $min;
            }

            $subLine{time} = "$min:$sec.$msec";
        } elsif ($lineNum)
        { # content
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

    # push last line hash
    push @subList, %subLine if ($lineNum);
    return @subList;

    push @subList, %subLine if ($lineNum);
    return @subList;
}

=head2 build subtitle hash structure from ass string

@param @subLines
@return @subHashList for each line

=cut

sub _assToHash{
    my @subLines=@_;
    my $lineNum=0; # processed lineNum for each (time,content) pair, we need this b/c there might be header
    my @subList;   # returned hash list
    my %subLine;   # sub line hash, shared by time and content

    foreach my $assLine in @subLines{
        chomp;
        if ($assLine =~ m/Dialogue: 0,([^,]*),([^,]*),([^,]*),[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,(.*)$/) {
            my $begin = $1;
            my $end = $2;
            my $text = $4;
            my $isComment = $3;

            print "\nLine: $lineNumber\n  Begin: [$begin]  End: [$end]  isComment: [$isComment]\n  text: [$text]\n"
            if $debug;

            if (!$isComment) {
                # match time
                %subLine=( time => '', subtitle => ''); # reset subline hash
                $begin=~m/(\d\d):(\d\d):(\d\d)\.(\d\d)/;
                my ($hour, $min, $sec, $msec) = ($1, $2, $3, $4);
                if ($hour != "00") {
                    $min = $hour * "60" + $min;
                }
                $text=s/{.*}//g;

                $subLine{time} = "$min:$sec.$msec";
                $subLine{subtitle}=$text
                push @subList,%subLine;
            }
        } else {
            # just ignore error or headers
        }
        return @subList;
    }

=head2 sync delayed subtitles

@param subLines subtitle list ref, only apply to srt
@param delay_ms delayed time in ms
@return none

=cut
sub _syncDelaySrt(\@$){
    my ($subLines, $delay_ms) = @_;

    #time scale
    my %scales =  ( 'h' => 3600000,
                    'm' => 60000,
                    's' => 1000,
                    'u' => 0,
                );

    foreach my $subline (@{$subLines}){
        # 00:01:09,040 --> 00:01:11,713
	    if ( /(\d\d):(\d\d):(\d\d),(\d+)\s+-->\s+(\d\d):(\d\d):(\d\d),(\d+)/ ){
            my ($sh,$sm,$ss,$su,$eh,$em,$es,$eu) = ($1,$2,$3,$4,$5,$6,$7,$8);

            #modify start and end time
            my $s = ($su + ($ss * $scales{'s'}) + ($sm * $scales{'m'}) + ($sh * $scales{'h'})) + $delay_ms;
            my $e = ($eu + ($es * $scales{'s'}) + ($em * $scales{'m'}) + ($eh * $scales{'h'})) + $delay_ms;

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

            $subline="%02d:%02d:%02d,%03d --> %02d:%02d:%02d,%03d\n", $sh,$sm,$ss,$su,$eh,$em,$es,$eu;
        }
    }
}

sub _mergeSubTime{

}

=head1 pick subtitles for output

needed: 
1. dual language hash for rtf
2. ass/srt origin dual language for video subs

current: assume input only has ass subs
TODO: srt

=cut

sub _pickOutputSubs{
    my $self=shift;
    foreach $filename (%{$self->subHash})
    if($filename=~'ass'){
        # dual language check
        # 
    }
    else {
        #TODO for srt
        # current remove
    }
}

=head1 generate rtf from sub Hash

@param sublines hash: time:eng:chn 

@return rtf string
=cut

sub genRtfSub{

    @sublines =shift;

    # prolog
    $rtf= q[{\rtf1\ansi\deff0
{\fonttbl
{\f0\froman Times New Roman;}
{\f1\fswiss Arial;}
{\f2\fmodern Courier New;}
}}];

foreach my %subline @sublines {
    # TODO: formatted string
    $rtf .="[$subline{'time'}]";
    $rtf .=$subline{'eng'};
    $rtf .="|".$subline{'chn'};
    $rtf .=" \par\n";
}

# end file
$rtf .= "\n\\par}\n\n";
    return $rtf;
}

sub genLrcSub{

}

sub genSubs{

}

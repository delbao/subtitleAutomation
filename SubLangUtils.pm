package SubLangUtils;

use strict;
use warning;

=head2 detect input string languages

eng, chn, eng+chn, unknown 

=cut

sub _detectLang{

}

=head1 convert the input string to utf-8
@param octets input string in any encoding
@return string output string in UTF8 format

=cut
sub _convToUTF8{
    $octets = shift;
    my $encode = Encode::Guess::guess_encoding($octets);
    return Encode::decode($encode, $octets);
}

sub genDualLangSub{

}

sub gen{

}

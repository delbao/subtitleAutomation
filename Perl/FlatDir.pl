# store names of a list of all files in a variable
my $sub_dir = shift @ARGV;

# flat the directory

# glob all files

my @all_files=glob $sub_dir.'\*';
foreach $file(@all_files){
    if( -d $file){
	my $cmd='move "'."$file\\*".'" '."$sub_dir";
	system $cmd;

	#delete folder and its file
	$cmd='rmdir "'."$file".'" '."/s /q";	
	system $cmd;
    }
}

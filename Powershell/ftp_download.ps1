##############
#PS Script to FTP Download files from FTP Server
#Date:22-Feb-2014
##############
Param(
[string]$ftpDir="",
 [Parameter(Mandatory=$FALSE,ValueFromPipeline=$FALSE)]
		[ValidateRange(1,10000)]
        [Int] $limit=-1 #unlimited videos download
)

$Username = "pi" 
$Password = "raspberry"
$DownloadFolder = "C:/Users/baodepei/Videos/TV_new" #Local folder
$ftpServer ="ftp://10.0.0.4" #ftp folder path
$message="failed"

if($ftpServer.endsWith("/") -eq $False)  
{
	$ftpServer=$ftpServer + "/"
}
if($ftpdir.startsWith("/") -eq $True)
{
	if ($ftpdir.Length -gt 1)
	{
		$ftpdir=$ftpdir.substring(1);
	}
	else
	{
		$ftpdir=""
	}
	
}
 if($ftpdir.Length -gt 1 -and $ftpdir.endsWith("/") -eq $False)  
{
	$ftpdir=$ftpdir + "/"
} 
if($DownloadFolder.Length -gt 1 -and $DownloadFolder.endsWith("/") -eq $False)  
{
	$DownloadFolder=$DownloadFolder + "/"
}

$RemotePath=$("$ftpServer$ftpDir")


$err=$FALSE
$Debug=$FALSE  # if the variable is set to TRUE ,Debugmode is on 
 
if ($ftpdir -eq "")
 {
 write-host "No ftp directory"
 }
 else
 {write-host "ftp directory : $ftpDir"
 }
if($limit -gt -1)
{
	write-host "No of videos to download : $limit"
}
else
{	
	write-host "No Download Limit Set"
}


 
function DebugToggle ($Debug) {
   
   if($Debug -eq $True) { 
   $DebugPreference = 'Continue' 
   write-host "script is running in debug mode"
   }
    #Write-Debug "Debug message about something"
    # Generate output
   
}

DebugToggle $Debug 


write-host --------------------------------------------------------------------------------------------
write-host "connecting to $RemotePath"
write-host --------------------------------------------------------------------------------------------
$cred=New-Object System.Net.NetworkCredential($Username,$Password)  
[System.Net.FtpWebRequest]$ftp = [System.Net.WebRequest]::Create($RemotePath) 
#To get the file details from the ftp server
$ftp.Method = [System.Net.WebRequestMethods+FTP]::ListDirectory 
$ftp.credentials=$cred
try 
{
$response = $ftp.getresponse() 
}
catch
{	#incase  ftp folder path is invalid
	write-host $_.Exception.Message
	write-host "Please verify the ftp path"
	break
}
$stream = $response.getresponsestream() 

$buffer = new-object System.Byte[] 1024 
$encoding = new-object System.Text.AsciiEncoding 

$outputBuffer = "" 
$foundMore = $FALSE 


## Read all the data available from the stream, writing it to the 
## buffer when done. 
do 
{ 
    ## Allow data to buffer for a bit 
    start-sleep -m 1000 

    ## Read what data is available 
    $foundmore = $FALSE 
    $stream.ReadTimeout = 1000

    do 
    { 
        try 
        { 
            $read = $stream.Read($buffer, 0, 1024) 

            if($read -gt 0) 
            { 
                $foundmore = $TRUE 
                $outputBuffer += ($encoding.GetString($buffer, 0, $read)) 
				#$outputBuffer = $("$outputBuffer$(",")($encoding.GetString($buffer, 0, $read)) ")
            } 
        } catch { $foundMore = $FALSE; $read = 0 } 
    } while($read -gt 0) 
} while($foundmore)

#$outputBuffer
#split the output buffer by NewLine
$seperator="`r`n"

$videoFiles = $outputBuffer.Split($seperator)

write-debug  "$RemotePath" #-debug
write-debug " $videoFiles" #-debug
$bFiles=$FALSE
$webclient = New-Object System.Net.WebClient 	
$webclient.Credentials = $cred
$i=0;

 foreach($item in ($videoFiles)){ 
        
		#$temp="$RemotePath$item"		
		#$uri = New-Object System.Uri($temp) 		
        #"Downloading FileName $item"
		#ignore the files other than allowed video files
		if (($item -like "*.mp4") -or ($item -like "*.avi"))
		{	
			$sfile=$item.SubString(0,$item.lastIndexOf("."))
			
			if($limit -ne -1)
			{
				if($i -ge $limit)
				{
					write-host "No of Downloads reached. Exiting ..."
					break;
				}
			}
			$lrcFile=""
			$srtFile=""
			if(($videoFiles -contains $("$sfile$(".lrc")")) -and ($videoFiles -contains $("$sfile$(".srt")")))
			{
				$lrcFile=$("$sfile$(".lrc")")
				$srtFile=$("$sfile$(".srt")")
				#download lrc file and delete the file on server
				$files=$item,$lrcFile,$srtFile
				#incase error happens while downloading files don't delete files on server
				$bFiles=$TRUE
				try
				{
				foreach($file in $files)
					{
					$temp="$RemotePath$file"
					$uri = New-Object System.Uri($temp) 
					$localFile=$("$DownloadFolder$file")
					write-debug "local File path : $localFile" 
					write-host "Downloading $file"
					$webclient.DownloadFile($uri,$localFile)
					
					}
				}
				catch
				{
					$err=$TRUE
					$ErrorMessage = $_.Exception.Message
					$FailedItem = $_.Exception.ItemName
					write-host "---------------------ERROR-------------------------" 
					write-host $ErrorMessage	
					write-debug $error[0].Exception.ToString() #-debug
					
					write-host "----------------------------------------------------" 
					
					
					break
				}				
				#deleting part of the project
				if($err -eq $FALSE)
				{
				foreach($file in $files)
					{
					$temp="$RemotePath$file"
					$uri = New-Object System.Uri($temp) 
					[System.Net.FtpWebRequest]$ftp = [System.Net.WebRequest]::Create($uri.absoluteUri) 
					$ftp.Method = [System.Net.WebRequestMethods+FTP]::DeleteFile 
					$ftp.credentials=$cred
					write-output "Deleting $file on server"
					$response = $ftp.getresponse()	
					}
				$message="Completed"
				}
				$i=$i+1
			}
		#	elseif
		#	{
		#		$subFile=$("$file$(".srt")")
		#	}
			# if subtitle is available for a video ,Download it otherwise leave it
			#if($subFile -ne $(""))
			#{	
			#}
		}
		 
		
    }
	
	if(($err -eq $FALSE) -and ($message -eq "Completed"))
	{
		write-host "Number of videos downloaded : $i"
		write-host "Download completed successfully" -foregroundcolor green
	}
	elseif($bFiles -eq $FALSE)
	{
		write-host "No files to download" 
	}
	else
	{
		write-host "Download Failed"  -foregroundcolor red -backgroundcolor yellow
	}
	
	

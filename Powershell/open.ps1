
# args list
param([string]$content_dir="TV")

$content_root="C:\Users\baodepei\Videos"

# open first episode in TV/Movie shows
# update episode.list first
#$episodes=(Get-ChildItem "$content_root\$content_dir" | Where-Object {$_.name -match '(mp4|avi)'} | Select -ExpandProperty 'Name')

# save mp4|avi in extension from gc
$episodes=Get-Content "$content_root\$content_dir\episode.list"

IF ($episodes.count -gt 1)
{
    Set-Content "$content_root\$content_dir\episode.list" $episodes[1 .. ($episodes.length-1)]
} ELSE {
    Set-Content "$content_root\$content_dir\episode.list" ""
}

# open episode with shebulan
Stop-Process -ProcessName shebulan -ErrorAction SilentlyContinue

$video="$content_root\$content_dir\" +$episodes[0]
& "C:\Program Files\ShebulanGroup\shebulanV1.6.1\shebulan.exe" $video
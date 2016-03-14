#Current Functions
1. download the subtitle from opensubtitles.org and shooter.cn according to video hash
2. detect the language of the downloaded subtitle files, only keep English and Chinese (some subtitles may be dual language, eng and chn, this is preferable, some marked as eng but actually it's not)
3. convert the subtitles to .srt if it's not (say, .ass)
4. after getting the raw .srt of both languages, combine and format them according to the following rules

INPUT: subtitles files with .srt format. full filename is in the format of MOVIENAME.{chn|eng}.srt.

e.g.,

Bunheads.S01E14.HDTV.x264-2HD.VTV.chn.srt

Bunheads.S01E14.HDTV.x264-2HD.VTV.eng.srt

OUTPUT: two subtitle files for each movie: a dual language .lrc file and a dual language .srt file
an example of lrc format

[00:00.00]<R2>Previously on Bunheads...|前情提要 (dual language subs sit at the same line divided by a bar "|")

##Algorithm
1. some chinese subtitles may be encoded in GB/BIG5..., convert them to Unicode
2. Also want to combine consecutive sub lines in terms of an input parameter of time interval and make a single long line.
3. ignore some lines that are over/under a certain threshold 
4. a function to indicate the repetition of a line (<R2> in the above example means repeat twice)
5. combine 1,2,3,4 the algorithm is
  1. if the accumulated line has less than X words, continue, more, output and start over
  2. if the line has less than Y (say, 5) English words, skip, output previous and start over
  3. if the line is longer than Z (say, 10) sec, skip, output previous and start over
  4. by default, repeat twice


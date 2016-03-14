#! /usr/bin/env python
# -*- coding: utf-8 -*-
#    Copyleft 2011 wistful <wst public mail at gmail com>
#
#    This is a free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# -*- coding: utf-8 -*-
__author__ = 'wistful'

import re
import codecs
import hashlib


from collections import namedtuple

SubRecord = namedtuple('SubRecord', ['start', 'finish', 'text'])


class SrtFormatError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
def markInBlackList(filepath):
    blacklist = open('blacklist','a')
    data = open(filepath,'r').read()
    
    #print data
    blacklist.write(hashlib.md5(data).hexdigest()+"\n")

    blacklist.close()
    

def parse_time(str_time,filepath = ''):
    """
    convert string format of start-finish to integer(ms) format
    >>> parse_time("00:14:33,460 --> 00:14:35,419")
    (873460, 875419)
    """
    pattern_time = r"(?P<h1>\d+):(?P<m1>\d+):(?P<s1>\d+),(?P<ms1>\d+)\W*-->\W*(?P<h2>\d+):(?P<m2>\d+):(?P<s2>\d+),(?P<ms2>\d+)$"
    try:
        d = re.match(pattern_time, str_time.strip()).groupdict()
    except:
        message = u"Invalid string format '%s' , expect hh:mm:ss,msc --> hh:mm:ss,msc" % str_time
        return None,None
        markInBlackList(filepath)
        raise SrtFormatError(message)
    get_ms = lambda h, m, s, ms: (int(s) + int(m) * 60 + int(h) * 60 * 60) * 1000 + int(ms)
    return get_ms(d['h1'], d['m1'], d['s1'], d['ms1']), get_ms(d['h2'], d['m2'], d['s2'], d['ms2'])


def ms2time(ms,style = 1):
    """
    convert msc to string format
    >>> ms2time(233243)
    '00:03:53,243'
    >>> ms2time(442)
    '00:00:00,442'
    """
    it = int(ms / 1000)
    ms = ms - it * 1000
    ss = it % 60
    mm = ((it - ss) / 60) % 60
    hh = ((it - (mm * 60) - ss) / 3600) % 60
    if style is 1:
        return "%02d:%02d:%02d,%03d" % (hh, mm, ss, ms)
    if style is 2:
        return "%d:%d.%03d" %(mm+60*hh,ss,ms)



def parse_ms(start, finish):
    """
    convert msc representation to string format
    >>> parse_ms(442, 233243)
    '00:00:00,442 --> 00:03:53,243'
    """
    return "%s --> %s" % (ms2time(start), ms2time(finish))


def subreader(file_path):
    """
    generator return namedtuple SubRecord(start, finish, text)
    Args:
        file_path: full path to srt-file
    """
    pattern_index = r"^\d+$"
    # records, times, text = list(), None, list()
    start = finish = None
    text = []

    UTF16_LE_BOM = "\xff\xfe"

# much later
    if open(file_path, 'r').read(2) == UTF16_LE_BOM:
        data = codecs.open(file_path, 'r','utf-16')
    else:
        data = open(file_path, 'r')
        

    for line in data:
        line = line.strip()
        if re.match(pattern_index, line):
            if start and finish:
                yield SubRecord(start, finish,
                                text='{0}\n'.format('\n'.join(text)))
                start = finish = None
                
                text = []
            text = []
        elif '-->' in line:
            start, finish = parse_time(line,file_path)
        elif line:
            if(file_path.find('.chs.srt')>0 and len(text) == 0):
                line = '|'+line
            p = re.compile('{.*}|<.*>')
            line = p.sub('',line)
                
            text.append(line)
    if start and finish:
        yield SubRecord(start, finish, text='{0}\n'.format('\n'.join(text)))


def subwriter(filepath, subtitles):
    """
    filepath: path to srt-file
    subtitles: [SubRecord(start, finish, text), ...]

    write subtitles structure to srt-file
    """
    lines = ["{index}\n{time}\n{text}\n".format(index=str(index),
                                                time=parse_ms(rec.start,
                                                              rec.finish),
                                                text=rec.text.replace('|',''))
             for index, rec in enumerate(subtitles, 1)]
    
    open(filepath, 'w').writelines(lines)
    print '\033[1;32;40m'+'OTUPUT COMBINED SUB FILE:'+filepath.replace('.combined','')+ '\033[0m'
def lang(uchar):
        

        if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
            return 'chs'
        if uchar >=u'a' and uchar<=u'z':
            return 'eng'

def strLang(buffer):
    count_chs = 0
    count_eng = 0
    for b in buffer:
        if(lang(b)=='chs'):
            count_chs=count_chs+1
        elif lang(b)=='eng':
            count_eng=count_eng+1
    
    if(count_chs>0):
        return 'chs'
    elif(count_eng>0):
        return 'eng'


def lrcwriter(filepath,subtitles,mode=0):
    lines = []
    last_finish = 0;
    for index,rec in enumerate(subtitles,1):
      if last_finish !=0 and rec.start - last_finish > 1000:
        time = ms2time(last_finish, 2)
        mark = '<R0>'
        text = ''
        lines.append("[{_time}]{_mark}{_text}\n".format(_time=time,_mark=mark,_text=text).encode('gb18030'))
        
      last_finish = rec.finish
      duration = rec.finish - rec.start
      time = ms2time(rec.start, 2)
      text = rec.text
      if mode==1:
        # print 'this is mode 1 '
        text = text.replace('\r\n','\n')
        parts = text.split('\n')
        lang =''
        for i in range(0,len(parts)):
            p=parts[i]
            strlang = strLang(p.decode('utf-8'))
            # print strlang
            if lang=='':
                lang = strlang
                continue
            if lang!=strlang:
                if strlang == 'chs':
                    s = ''.join(parts[:i])
                    s =s + '|'
                    s = s+''.join(parts[i:])
                    text =s
                elif strlang == 'eng':
                    s = ''.join(parts[i:])                        
                    s =s+'|'
                    s = s+''.join(parts[:i])
                    text =s
                    break
                        
                        
      text = text.replace('\r\n','')
      text = text.replace('\n','')

      word_count = len(re.findall(r"[A-Za-z]+", text))
      num_count = len(re.findall(r"[0-9]+",text))
#        text_eng = text.split('|')[0]
#       word_count = len(text_eng.split(' '))
                                   
                    
      mark='<R1>'
      if word_count >= 8:
         mark='<R2>'
      if word_count < 5:
         mark = '<R0>'
      if num_count >30:
         mark = '<R0>'
      if duration > 5000:
         mark='<R0>'
      if mode==2:
         # mark = '<R2>'
         text = text.replace('|','')
      lines.append("[{_time}]{_mark}{_text}\r\n".format(_time=time,_mark=mark,_text=text).encode('gb18030'))

    open(filepath, 'w').writelines(lines)
    print '\033[1;32;40m'+'OUTPUT LRC FILE:'+filepath.replace('.combined','')+ '\033[0m'

if __name__ == '__main__':
    import doctest
    print doctest.testmod()

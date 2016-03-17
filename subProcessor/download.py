#!/usr/bin/python2
# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import urllib2
import zlib
from srtmerge import srt_merge
import subdl
import codecs
import chardet
import re
import ass2srt
import time

queryUrl = 'http://svplayer.shooter.cn/api/subapi.php'
userAgent = 'SPlayer Build 580'
contentType = 'multipart/form-data; boundary=----------------------------767a02e50d82'
boundary = '----------------------------767a02e50d82'


# file_path = 'F:\Videos\Game Of Thrones\Game.Of.Thrones.1x01.Winter.Is.Coming.720p.HDTV.x264-CTU.[tvu.org.ru].mkv'
def my_hash(path):
    fp = open(path, "rb")
    file_length = os.path.getsize(path)

    if file_length < 8192:
        return ""
    else:
        block_size = 4096
        offset = [block_size, file_length / 3 * 2, file_length / 3, file_length - 8192]
        hash_result = ""
        for i in range(0, 4):

            fp.seek(int(offset[i]))
            data_block = fp.read(block_size)
            hash_str = hashlib.md5(data_block)
            if len(hash_result) > 0:
                hash_result += ";"
            hash_result += hash_str.hexdigest().lower()
        # print hash_result
        return hash_result


def byte2int(bstr, width):
    """
    Convert a byte string into a signed integer value of specified width.
    """
    val = sum(ord(b) << 8 * n for (n, b) in enumerate(reversed(bstr)))
    if val >= (1 << (width - 1)):
        val -= (1 << width)
    return val


def str_lang(input_buffer):
    count_chs = 0
    count_eng = 0
    for b in input_buffer:
        if lang(b) == 'chs':
            count_chs += 1
        elif lang(b) == 'eng':
            count_eng += 1

    if count_chs > 1000 and count_eng > len(input_buffer) / 5:
        print "chs_eng srt is confirmed"
        return 'chs_eng'
    elif count_chs > 1000:
        print "chs srt is confirmed"
        return 'chs'
    elif count_eng > len(input_buffer) / 5:
        print 'eng srt is confirmed'
        return 'eng'
    else:
        return 'none'


def lang(uchar):
    if u'\u4e00' <= uchar <= u'\u9fa5':
        return 'chs'
    if u'a' <= uchar <= u'z':
        return 'eng'


def query_sub(hash_string, file_path):
    postdata = '------------------------------767a02e50d82'
    postdata += "\r\n"
    postdata += 'Content-Disposition: form-data; name="pathinfo"'
    postdata += "\r\n\r\n"
    postdata += file_path
    postdata += "\r\n"
    postdata += '------------------------------767a02e50d82'
    postdata += "\r\n"
    postdata += 'Content-Disposition: form-data; name="filehash"'
    postdata += "\r\n\r\n"
    postdata += hash_string
    postdata += "\r\n"
    postdata += '------------------------------767a02e50d82--'
    postdata += "\r\n"
    postdata = postdata.encode('utf-8')

    req = urllib2.Request(queryUrl)
    req.add_header('User-Agent', userAgent)
    req.add_header('Connection', "Keep-Alive")
    req.add_header('Content-Type', contentType)
    res = urllib2.urlopen(req, postdata)

    if res.getcode() == 200:
        print
        'connect to shooter.cn: ok'

    if res.getcode() == 200:
        stat_code = res.read(1)

        if len(stat_code) == 0:
            print("no data from shooter.cn")
            return 'none', 'none'
        stat_code = byte2int(stat_code, 8)
        if stat_code == -1:
            print("subtitle not found from shooter.cn")
            return 'none', 'none'
        if stat_code < 0:
            print("data connection error from shooter.cn")
            return 'none', 'none'
        print "stat_code is:", stat_code
        for i in range(0, stat_code):
            desc_len = byte2int(res.read(4), 32)
            if desc_len > 0:
                res.read(desc_len)

            byte2int(res.read(4), 32)
            num_of_files = res.read(1)

            if len(num_of_files) == 0:
                print("no file")
                continue
            num_of_files = byte2int(num_of_files, 8)
            print 'find ' + str(num_of_files) + ' sub file from shooter.cn'
            for j in range(0, num_of_files):
                byte2int(res.read(4), 32)
                ext_len = byte2int(res.read(4), 32)
                ext = res.read(ext_len)
                ext_string = ext.decode('utf-8', 'ignore')

                file_len = byte2int(res.read(4), 32)
                buffer_ = res.read(file_len)
                print ext_string + ' file found'
                bGzipped = (buffer_[0] == '\x1f') & (buffer_[1] == '\x8b') & (buffer_[2] == '\x08')
                if bGzipped:
                    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
                    buffer_ = d.decompress(buffer_)

                result = chardet.detect(buffer_)
                encoding = result["encoding"]
                buffer_ = buffer_.decode(encoding, 'ignore').encode('utf-8')
                p = re.compile('{.*}|<.*>')
                buffer_ = p.sub('', buffer_)
                buffer_ = buffer_.decode('utf-8', 'ignore')
                if ext_string == 'ass':
                    print 'converting ass file to srt file'
                    buffer_ = ass2srt.convert(buffer_)
                    ext_string = 'srt'
                os.path.split(file_path)
                root, extension = os.path.splitext(file_path)
                md5 = hashlib.md5(buffer_).hexdigest() + "\n"
                if blacklist.count(md5) > 0:
                    print 'this file is marked in blacklist'
                    continue

                str_lang_ = str_lang(buffer_)
                if str_lang_ == 'none':
                    print 'no file find from shooter.cn'
                    return 'none', 'none'
                if str_lang_ == 'chs_eng':
                    file_name_new = root + ".chs_eng." + ext_string
                if str_lang_ == 'chs':
                    file_name_new = root + ".chs." + ext_string
                if str_lang_ == 'eng':
                    file_name_new = root + ".eng." + ext_string

                fp_output = codecs.open(file_name_new, "w")
                fp_output.write(buffer_.encode('utf-8'))
                fp_output.close()

                return file_name_new, str_lang

    return '', 'none'


def srt2lrc():
    return ''


def get_shooter_sub(file_path):
    hash_str = hash(file_path)
    return query_sub(hash_str, file_path)


def get_open_subtitles_sub(file_path, lang_='eng'):
    argv = ['--existing=overwrite', '--lang=' + lang_, file_path]
    return subdl.main(argv)


def process_file(file_path):
    if not os.path.exists(f):
        print f + ' is not existed'
        return
    dir_name, basename = os.path.split(file_path)
    root, extension = os.path.splitext(file_path)
    print 'PROCESSING FILE:' + basename
    console_without_color()
    if os.path.exists(root + ".lrc"):
        print 'lrc file existed,quit now!'
        return

    sub_shooter, lang_ = get_shooter_sub(file_path)
    if lang_ == 'chs_eng':
        srt_merge([sub_shooter], root + ".combined.srt", 0, 1)
        return
    if lang_ == 'chs':
        sub_eng = get_open_subtitles_sub(file_path)
        if not sub_eng:
            console_color_yellow()
            print 'english sub file not found'
            console_without_color()
            srt_merge([sub_shooter], root + ".combined.srt", 0, 2)
            return srt_merge([sub_eng, sub_shooter], root + ".combined.srt", 0)

    if lang_ == 'eng':
        open_subtitle = get_open_subtitles_sub(file_path, 'chs')

        if not open_subtitle:
            console_color_yellow()
            print 'chinese sub file not found'
            console_without_color()
            srt_merge([sub_shooter], root + ".combined.srt", 0, 2)
            return srt_merge([sub_shooter, open_subtitle], root + ".combined.srt", 0)

    if lang_ == 'none':
        open_subtitle_chs = get_open_subtitles_sub(file_path, 'chs')
        open_subtitle_eng = get_open_subtitles_sub(file_path)
        if open_subtitle_eng and open_subtitle_chs:
            srt_merge([open_subtitle_chs, open_subtitle_eng], root + ".combined.srt", 0)
            return
        if open_subtitle_eng:
            srt_merge([open_subtitle_eng], root + ".combined.srt", 0, 2)
            console_color_yellow()
            print 'chinese sub file not found'
            console_without_color()
            return
        if open_subtitle_chs:
            srt_merge([open_subtitle_chs], root + ".combined.srt", 0, 2)
            console_color_yellow()
            print 'english sub file not found'
            console_without_color()
            return
        console_color_yellow()
        print 'NO SUB FILE FOUND'
        unfound_file.append(file_path)
        console_without_color()
    if os.path.exists(root + '.lrc'):
        open(root + '.lrc', 'rw').read()


def console_color_yellow():
    print '\033[1;31;40m'


def console_without_color():
    print '\033[0m'


def color_mess(mess):
    console_color_yellow()
    print mess
    console_without_color()


reload(sys)
sys.setdefaultencoding('utf-8')
if not os.path.exists('blacklist'):
    os.mknod('blacklist')
unfound_file = []
blacklist = open('blacklist', 'r').readlines()
file_path_ = sys.argv[1:]
for f in file_path_:
    console_color_yellow()
    print '*' * 80
    try:
        process_file(f)
    except Exception, e:
        color_mess(e)

    console_color_yellow()
    print '*' * 80
if len(unfound_file) > 0:
    print('CAN NOT FIND ANY SUB FILE FOR THESE FILES:\n')
    for f in unfound_file:
        print f
    if '--delete' in sys.argv:
        for f in unfound_file:
            ltime = int(os.stat(f).st_mtime)
            print ltime
            if ltime + 3600 * 24 * 10 < int(time.time()):
                os.rename(f, f + '.bak')

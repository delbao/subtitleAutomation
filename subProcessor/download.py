#!/usr/bin/python2
# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import urllib
import urllib2
import gzip
import zlib
from srtmerge import srtmerge
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


# filePath = 'F:\Videos\Game Of Thrones\Game.Of.Thrones.1x01.Winter.Is.Coming.720p.HDTV.x264-CTU.[tvu.org.ru].mkv'
def hash(path):
    fp = open(path, "rb")
    file_length = os.path.getsize(path)

    if (file_length < 8192):
        return "";
    else:
        block_size = 4096;
        num_of_segments = 4;
        offset = [block_size, file_length / 3 * 2, file_length / 3, file_length - 8192]
        hash_result = ""
        for i in range(0, 4):

            fp.seek(int(offset[i]))
            data_block = fp.read(block_size)
            hashstr = hashlib.md5(data_block)
            if (len(hash_result) > 0):
                hash_result += ";"
            hash_result += hashstr.hexdigest().lower()
        # print hash_result
        return hash_result


def byte2int(bstr, width):
    """
    Convert a byte string into a signed integer value of specified width.
    """
    val = sum(ord(b) << 8 * n for (n, b) in enumerate(reversed(bstr)))
    if val >= (1 << (width - 1)):
        val = val - (1 << width)
    return val


def srtLang(buffer):
    count_chs = 0
    count_eng = 0
    for b in buffer:
        if (lang(b) == 'chs'):
            count_chs = count_chs + 1
        elif lang(b) == 'eng':
            count_eng = count_eng + 1

    if (count_chs > 1000 and count_eng > len(buffer) / 5):
        print "chs_eng srt is confirmed"
        return 'chs_eng'
    elif (count_chs > 1000):
        print "chs srt is confirmed"
        return 'chs'
    elif count_eng > len(buffer) / 5:
        print 'eng srt is confirmed'
        return 'eng'
    else:
        return 'none'


def lang(uchar):
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return 'chs'
    if uchar >= u'a' and uchar <= u'z':
        return 'eng'


def querySub(hashString, filePath):
    i_headers = {"User-Agent": userAgent, "Content-Type": contentType}
    postdata = '------------------------------767a02e50d82'
    postdata += "\r\n"
    postdata += 'Content-Disposition: form-data; name="pathinfo"'
    postdata += "\r\n\r\n"
    postdata += filePath
    postdata += "\r\n"
    postdata += '------------------------------767a02e50d82'
    postdata += "\r\n"
    postdata += 'Content-Disposition: form-data; name="filehash"'
    postdata += "\r\n\r\n"
    postdata += hashString
    postdata += "\r\n"
    postdata += '------------------------------767a02e50d82--'
    postdata += "\r\n"
    postdata = postdata.encode('utf-8')

    req = urllib2.Request(queryUrl)
    req.add_header('User-Agent', userAgent)
    req.add_header('Connection', "Keep-Alive")
    req.add_header('Content-Type', contentType)
    # print postdata
    res = urllib2.urlopen(req, postdata)

    if res.getcode() == 200:
        print 'connect to shooter.cn: ok'

    if (res.getcode() == 200):
        statCode = res.read(1)

        if (len(statCode) == 0):
            print("no data from shooter.cn")
            return 'none', 'none'
        statCode = byte2int(statCode, 8)
        if (statCode == -1):
            print("subtitle not found from shooter.cn")
            return 'none', 'none'
        if (statCode < 0):
            print("data connection error from shooter.cn")
            return 'none', 'none'
        print "statCode is:", statCode
        for i in range(0, statCode):
            packageLen = byte2int(res.read(4), 32)

            descLen = byte2int(res.read(4), 32)
            if (descLen > 0):
                desc = res.read(descLen)

            fileDataLen = byte2int(res.read(4), 32)
            numOfFiles = res.read(1)

            if (len(numOfFiles) == 0):
                print("no file")
                continue
            numOfFiles = byte2int(numOfFiles, 8)
            print 'find ' + str(numOfFiles) + ' sub file from shooter.cn'
            for j in range(0, numOfFiles):
                singleFilePackLen = byte2int(res.read(4), 32)
                extLen = byte2int(res.read(4), 32)
                ext = res.read(extLen)
                extString = ext.decode('utf-8', 'ignore')

                fileLen = byte2int(res.read(4), 32)
                buffer = res.read(fileLen)
                print extString + ' file found'
                # if(extString!='srt'):
                #    print "not srt file, continue..."
                #   continue
                bGzipped = (buffer[0] == '\x1f') & (buffer[1] == '\x8b') & (buffer[2] == '\x08')
                if (bGzipped):
                    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
                    buffer = d.decompress(buffer)

                result = chardet.detect(buffer)
                encoding = result["encoding"]
                buffer = buffer.decode(encoding, 'ignore').encode('utf-8')
                p = re.compile('{.*}|<.*>')
                buffer = p.sub('', buffer)
                buffer = buffer.decode('utf-8', 'ignore')
                if extString == 'ass':
                    print 'converting ass file to srt file'

                    buffer = ass2srt.convert(buffer)
                    extString = 'srt'

                #                    fp_tmp_ass = open('tmp.ass','w')
                #                    fp_tmp_ass.write(buffer.encode('utf-8'))
                #                    fp_tmp_ass.close()
                #                    ass2srt.main(['tmp.ass'])
                #                    fp_tmp_srt = open('tmp.ass.srt','r')
                #                    buffer = fp_tmp_srt.read()
                #                    fp_tmp_srt.close()
                #

                dirname, basename = os.path.split(filePath)
                root, extension = os.path.splitext(filePath)
                md5 = hashlib.md5(buffer).hexdigest() + "\n"
                # print md5,blacklist.count(md5)
                if (blacklist.count(md5) > 0):
                    print 'this file is marked in blacklist'
                    continue

                srtlang = srtLang(buffer)
                if srtlang == 'none':
                    print 'no file find from shooter.cn'
                    return 'none', 'none'
                if (srtlang == 'chs_eng'):
                    filename = root + ".chs_eng." + extString
                if (srtlang == 'chs'):
                    filename = root + ".chs." + extString
                if (srtlang == 'eng'):
                    filename = root + ".eng." + extString


                    #  if(os.path.exists(filename)):
                    #      print filename+' exsited,bypassing'
                    #      return filename,srtlang
                fp_output = codecs.open(filename, "w")
                fp_output.write(buffer.encode('utf-8'))
                fp_output.close()

                return filename, srtlang

    return '', 'none'

    # print(content)


def srt2lrc(srtFile):
    return ''


def getShooterSub(filePath):
    hashstr = hash(filePath)
    return querySub(hashstr, filePath)


def getOpenSubtitlesSub(filePath, lang='eng'):
    argv = ['--existing=overwrite', '--lang=' + lang, filePath]
    return subdl.main(argv)


def processFile(filePath):
    """

    Returns:
        object: 
    """
    if not os.path.exists(f):
        print f + ' is not existed'
        return
    dirname, basename = os.path.split(filePath)
    root, extension = os.path.splitext(filePath)
    print 'PROCESSING FILE:' + basename
    print '\033[0m'
    if os.path.exists(root + ".lrc"):
        print 'lrc file existed,quit now!'
        return

    sub_shooter, lang = getShooterSub(filePath)
    if (lang == 'chs_eng'):
        srtmerge([sub_shooter], root + ".combined.srt", 0, 1)

        return
    if (lang == 'chs'):
        sub_eng = getOpenSubtitlesSub(filePath)

        if not sub_eng:
            print '\033[1;31;40m'
            print 'english sub file not found'
            print '\033[0m'

            srtmerge([sub_shooter], root + ".combined.srt", 0, 2)
            return
        srtmerge([sub_eng, sub_shooter], root + ".combined.srt", 0)

    if lang == 'eng':
        sub_openSubtitles = getOpenSubtitlesSub(filePath, 'chs')

        if not sub_openSubtitles:
            print '\033[1;31;40m'
            print 'chinese sub file not found'
            print '\033[0m'
            srtmerge([sub_shooter], root + ".combined.srt", 0, 2)
            return
        srtmerge([sub_shooter, sub_openSubtitles], root + ".combined.srt", 0)

    if lang == 'none':
        sub_openSubtitles_chs = getOpenSubtitlesSub(filePath, 'chs')

        sub_openSubtitles_eng = getOpenSubtitlesSub(filePath)
        if sub_openSubtitles_eng and sub_openSubtitles_chs:
            srtmerge([sub_openSubtitles_chs, sub_openSubtitles_eng], root + ".combined.srt", 0)

            return
        if sub_openSubtitles_eng:
            srtmerge([sub_openSubtitles_eng], root + ".combined.srt", 0, 2)

            print '\033[1;31;40m'
            print 'chinese sub file not found'
            print '\033[0m'

            return
        if sub_openSubtitles_chs:
            srtmerge([sub_openSubtitles_chs], root + ".combined.srt", 0, 2)
            print '\033[1;31;40m'
            print 'english sub file not found'
            print '\033[0m'
            return
        print '\033[1;31;40m'
        print 'NO SUB FILE FOUND'
        unfound_file.append(filePath)
        print '\033[0m'
    if os.path.exists(root + '.lrc'):
        lrc = open(root + '.lrc', 'rw').read()


reload(sys)
sys.setdefaultencoding('utf-8')
if not os.path.exists('blacklist'):
    os.mknod('blacklist')
unfound_file = []
blacklist = open('blacklist', 'r').readlines()
filePath = sys.argv[1:]
for f in filePath:
    print '\033[1;32;40m'
    print '*' * 80
    try:
        processFile(f)

    except Exception, e:
        print '\033[1;31;40m'
        print e
        print '\033[0m'

    print '\033[1;32;40m'
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
                # os.remove(f)

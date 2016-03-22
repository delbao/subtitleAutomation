import os
import re
import zlib
import codecs
import urllib2
import chardet
import hashlib

from hash import my_hash
from logging import getLogger
from lang_utils import srt_lang
from converter import byte2int, convert_ass_to_srt

blacklist = open('blacklist', 'r').readlines()

logger = getLogger()

queryUrl = 'http://svplayer.shooter.cn/api/subapi.php'
userAgent = 'SPlayer Build 580'
contentType = 'multipart/form-data; boundary=----------------------------767a02e50d82'
boundary = '----------------------------767a02e50d82'


def get_shooter_sub(file_path):
    hash_str = my_hash(file_path)
    return query_sub(hash_str, file_path)


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
        stat_code = res.read(1)
        if len(stat_code) == 0:
            return 'none', 'none'
        stat_code = byte2int(stat_code, 8)
        if stat_code == -1:
            return 'none', 'none'
        if stat_code < 0:
            return 'none', 'none'
        logger.info("stat_code is:" + str(stat_code))
        for i in range(0, stat_code):
            byte2int(res.read(4), 32)
            desc_len = byte2int(res.read(4), 32)
            if desc_len > 0:
                res.read(desc_len)
            byte2int(res.read(4), 32)
            num_of_files = res.read(1)
            if len(num_of_files) == 0:
                print("no file")
                continue
            num_of_files = byte2int(num_of_files, 8)
            for j in range(0, num_of_files):
                byte2int(res.read(4), 32)
                ext_len = byte2int(res.read(4), 32)
                ext = res.read(ext_len)
                ext_string = ext.decode('utf-8', 'ignore')
                file_len = byte2int(res.read(4), 32)
                buffer_ = res.read(file_len)
                logger.info(str(ext_string) + ' file found')
                zipped = (buffer_[0] == '\x1f') & (buffer_[1] == '\x8b') & (buffer_[2] == '\x08')
                if zipped:
                    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
                    buffer_ = d.decompress(buffer_)
                result = chardet.detect(buffer_)
                encoding = result["encoding"]
                buffer_ = buffer_.decode(encoding, 'ignore').encode('utf-8')
                p = re.compile('{.*}|<.*>')
                buffer_ = p.sub('', buffer_)
                buffer_ = buffer_.decode('utf-8', 'ignore')
                if ext_string == 'ass':
                    logger.info('converting ass file to srt file')
                    buffer_ = convert_ass_to_srt(buffer_)
                    ext_string = 'srt'
                root, extension = os.path.splitext(file_path)
                md5 = hashlib.md5(buffer_).hexdigest() + "\n"
                if blacklist.count(md5) > 0:
                    logger.info('this file is marked in blacklist')
                    continue
                srt_lang_ = srt_lang(buffer_)
                file_name = None
                if srt_lang_ == 'none':
                    return 'none', 'none'
                elif srt_lang_ == 'chs_eng':
                    file_name = root + ".chs_eng." + ext_string
                elif srt_lang_ == 'chs':
                    file_name = root + ".chs." + ext_string
                elif srt_lang_ == 'eng':
                    file_name = root + ".eng." + ext_string
                fp_output = codecs.open(file_name, "w")
                fp_output.write(buffer_.encode('utf-8'))
                fp_output.close()
                return file_name, srt_lang_
    return '', 'none'
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

QUERY_URL = 'http://svplayer.shooter.cn/api/subapi.php'
USER_AGENT = 'SPlayer Build 580'
CONTENT_TYPE = 'multipart/form-data; boundary=----------------------------767a02e50d82'
BOUNDARY = '----------------------------767a02e50d82'


def get_shooter_sub(file_path):
    hash_str = my_hash(file_path)
    return query_subtitles(hash_str, file_path)


def query_subtitles(hash_string, file_path):
    req = urllib2.Request(QUERY_URL)
    req.add_header('User-Agent', USER_AGENT)
    req.add_header('Connection', "Keep-Alive")
    req.add_header('Content-Type', CONTENT_TYPE)
    postdata = get_post_data(file_path, hash_string)
    res = urllib2.urlopen(req, postdata)
    if res.getcode() == 200:
        stat_code = res.read(1)
        if len(stat_code) == 0:
            return 'none', 'none'
        stat_code = byte2int(stat_code, 8)
        if stat_code == -1 or stat_code < 0:
            return 'none', 'none'
        logger.info("stat_code is:" + str(stat_code))
        for _ in range(stat_code):
            byte2int(res.read(4), 32)
            desc_len = byte2int(res.read(4), 32)
            if desc_len > 0:
                res.read(desc_len)
            byte2int(res.read(4), 32)
            num_of_files = res.read(1)
            if len(num_of_files) == 0:
                logger.info("no file")
                continue
            num_of_files = byte2int(num_of_files, 8)
            for __ in range(num_of_files):
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

                with codecs.open(file_name, "w") as fp_output:
                    fp_output.write(buffer_.encode('utf-8'))

                return file_name, srt_lang_
    return '', 'none'


def get_post_data(file_path, hash_string):
    strings = [
        '------------------------------767a02e50d82\r\n'
        'Content-Disposition: form-data; name="pathinfo"\r\n\r\n',
        file_path, '\r\n'
        '------------------------------767a02e50d82\r\n'
        'Content-Disposition: form-data; name="filehash"\r\n\r\n',
        hash_string, '\r\n'
        '------------------------------767a02e50d82--\r\n'
    ]
    return ''.join(strings).encode('utf-8')

import codecs
import hashlib
import re
import urllib2
import zlib
from logging import getLogger

import chardet

from os.path import exists, splitext, getsize

logger = getLogger()

QUERY_URL = 'http://svplayer.shooter.cn/api/subapi.php'
USER_AGENT = 'SPlayer Build 580'
CONTENT_TYPE = 'multipart/form-data; boundary=----------------------------767a02e50d82'
BOUNDARY = '----------------------------767a02e50d82'

if not exists('blacklist'):
    open('blacklist', 'w').close()
blacklist = open('blacklist', 'r').readlines()


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
                root, extension = splitext(file_path)
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


def my_hash(path):
    fp = open(path, "rb")
    file_length = getsize(path)

    if file_length < 8192:
        return ""
    else:
        block_size = 4096
        offset = [block_size, file_length / 3 * 2, file_length / 3, file_length - 8192]
        hash_result = ""
        for i in range(4):

            fp.seek(int(offset[i]))
            data_block = fp.read(block_size)
            hash_str = hashlib.md5(data_block)
            if len(hash_result) > 0:
                hash_result += ";"
            hash_result += hash_str.hexdigest().lower()
        return hash_result


def srt_lang(input_buffer):
    count_chs = 0
    count_eng = 0
    for b in input_buffer:
        if lang(b) == 'chs':
            count_chs += 1
        elif lang(b) == 'eng':
            count_eng += 1
    if count_chs > 1000 and count_eng > len(input_buffer) / 5:
        logger.info("chs_eng srt is confirmed")
        return 'chs_eng'
    elif count_chs > 1000:
        logger.info("chs srt is confirmed")
        return 'chs'
    elif count_eng > len(input_buffer) / 5:
        logger.info('eng srt is confirmed')
        return 'eng'
    else:
        return 'none'


def lang(uchar):
    if u'\u4e00' <= uchar <= u'\u9fa5':
        return 'chs'
    if u'a' <= uchar <= u'z':
        return 'eng'


def convert_ass_to_srt(input_buffer):
    result_lines = []
    for index, line in enumerate(input_buffer.split("\n")):
        if line[:9] == "Dialogue:":
            result_lines.append("%d\n" % index)
            clean_line = re.sub("{.*?}", "", line)
            entries = clean_line[10:].strip().split(",")
            result_lines.append(
                "%s --> %s\n" % (entries[1].replace(".", ",") + "0", entries[2].replace(".", ",") + "0"))
            result_lines.append("".join(entries[9:]).replace("\N", "\n") + "\n")
            result_lines.append("\n")
    return ''.join(result_lines)


def byte2int(b_str, width):
    val = sum(ord(b) << 8 * n for (n, b) in enumerate(reversed(b_str)))
    if val >= (1 << (width - 1)):
        val -= (1 << width)
    return val

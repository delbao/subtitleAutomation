import codecs
import hashlib
import re
import urllib2
import zlib
from logging import getLogger
from os.path import splitext

import chardet

from downloader.shooter.constants import QUERY_URL, blacklist, request_headers
from downloader.shooter.shooter_utils import hash_for_shooter, srt_lang, convert_ass_to_srt, byte2int

logger = getLogger()


def get_shooter_sub(file_path):
    hash_str = hash_for_shooter(file_path)
    return query_subtitles(hash_str, file_path)


def query_subtitles(hash_string, file_path):
    req = urllib2.Request(QUERY_URL, headers=request_headers)
    res = urllib2.urlopen(req, data=generate_post_data(file_path, hash_string))
    if res.getcode() == 200:
        stat_code_str = res.read(1)
        if not stat_code_check_pass(stat_code_str):
            return 'none', 'none'
        stat_code_int = byte2int(stat_code_str, 8)
        logger.info("stat_code is:" + str(stat_code_int))
        return process_url_result(res, stat_code_int, file_path)


def stat_code_check_pass(stat_code):
    if len(stat_code) != 0:
        stat_code = byte2int(stat_code, 8)
        if stat_code >= 0:
            return True
    return False


def process_url_result(url_res, stat_code, file_path):
    for _ in range(stat_code):
        read_header(url_res)
        for __ in range(get_number_of_files(url_res)):
            ext_string = read_file_ext(url_res)
            logger.info(str(ext_string) + ' file found')
            sub_file_content, ext_string = process_sub_file_buffer(get_sub_file_buffer(url_res), ext_string)
            if hashlib.md5(sub_file_content).hexdigest() not in blacklist:
                srt_lang_ = srt_lang(sub_file_content)
                if srt_lang_ in ['chs_eng', 'chs', 'eng']:
                    output_file_path = '%s.%s.%s' % ((splitext(file_path)[0]), srt_lang_, ext_string)
                    with codecs.open(output_file_path, "w") as output_file:
                        output_file.write(sub_file_content.encode('utf-8'))

                    return output_file_path, srt_lang_
            else:
                logger.info('this file is marked in blacklist')
    return '', 'none'


def get_sub_file_buffer(url_res):
    file_len = byte2int(url_res.read(4), 32)
    return url_res.read(file_len)


def process_sub_file_buffer(buffer_, ext_string):
    if buffer_[:3] == '\x1f\x8b\x08':
        decompressobj = zlib.decompressobj(16 + zlib.MAX_WBITS)
        buffer_ = decompressobj.decompress(buffer_)
    char_info = chardet.detect(buffer_)
    buffer_ = buffer_.decode(char_info["encoding"], 'ignore').encode('utf-8')
    pattern = re.compile('{.*}|<.*>')
    buffer_ = pattern.sub('', buffer_)
    buffer_ = buffer_.decode('utf-8', 'ignore')
    if ext_string == 'ass':
        logger.info('converting ass file to srt file')
        buffer_ = convert_ass_to_srt(buffer_)
        ext_string = 'srt'
    return buffer_, ext_string


def read_header(res):
    byte2int(res.read(4), 32)
    desc_len = byte2int(res.read(4), 32)
    if desc_len > 0:
        res.read(desc_len)
    byte2int(res.read(4), 32)


def get_number_of_files(url_res):
    num_of_files = url_res.read(1)
    if num_of_files:
        return byte2int(num_of_files, 8)
    else:
        logger.info("no files")
        return 0


def read_file_ext(url_res):
    url_res.read(4), 32
    ext_len = byte2int(url_res.read(4), 32)
    ext = url_res.read(ext_len)
    ext_string = ext.decode('utf-8', 'ignore')
    return ext_string


def generate_post_data(file_path, hash_string):
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

"""
download raw subtitle files from opensubtitles.org and subhd
"""
# !/usr/bin/python2
# -*- coding: utf-8 -*-
import logging
import os
import sys

import time_utils
from merger import srt_merge
from download_from_shooter import get_shooter_sub
from download_from_opensubtitle import get_subtitle_from_opensubtitle

LOGGING_FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
DATE_FORMAT = '[%Y-%m-%d %H:%M:%S]'
logging.getLogger().level = logging.DEBUG
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(datefmt=DATE_FORMAT, fmt=LOGGING_FORMAT)
ch.setFormatter(formatter)
logger.addHandler(ch)

queryUrl = 'http://svplayer.shooter.cn/api/subapi.php'
userAgent = 'SPlayer Build 580'
contentType = 'multipart/form-data; boundary=----------------------------767a02e50d82'
boundary = '----------------------------767a02e50d82'


def process_file(file_path):
    if not os.path.exists(f):
        logger.info(f + ' is not existed')
        return
    dir_name, basename = os.path.split(file_path)
    root, extension = os.path.splitext(file_path)
    logger.info('PROCESSING FILE:' + basename)

    if os.path.exists(root + ".lrc"):
        logger.info('lrc file existed,quit now!')
        return
    sub_shooter, lang_ = get_shooter_sub(file_path)
    if lang_ == 'chs_eng':
        srt_merge([sub_shooter], root + ".combined.srt", 0, 1)
        return
    if lang_ == 'chs':
        sub_eng = get_subtitle_from_opensubtitle(file_path)
        if not sub_eng:
            logger.info('english sub file not found')
            srt_merge([sub_shooter], root + ".combined.srt", 0, 2)
            return srt_merge([sub_eng, sub_shooter], root + ".combined.srt", 0)

    if lang_ == 'eng':
        open_subtitle = get_subtitle_from_opensubtitle(file_path, 'chs')

        if not open_subtitle:
            logger.info('chinese sub file not found')
            srt_merge([sub_shooter], root + ".combined.srt", 0, 2)
            return srt_merge([sub_shooter, open_subtitle], root + ".combined.srt", 0)

    if lang_ == 'none':
        open_subtitle_chs = get_subtitle_from_opensubtitle(file_path, 'chs')
        open_subtitle_eng = get_subtitle_from_opensubtitle(file_path)
        if open_subtitle_eng and open_subtitle_chs:
            srt_merge([open_subtitle_chs, open_subtitle_eng], root + ".combined.srt", 0)
            return
        if open_subtitle_eng:
            srt_merge([open_subtitle_eng], root + ".combined.srt", 0, 2)
            print 'chinese sub file not found'
            return
        if open_subtitle_chs:
            srt_merge([open_subtitle_chs], root + ".combined.srt", 0, 2)
            print 'english sub file not found'
            return
        print 'NO SUB FILE FOUND'
        unfound_file.append(file_path)
    if os.path.exists(root + '.lrc'):
        open(root + '.lrc', 'rw').read()


reload(sys)
sys.setdefaultencoding('utf-8')
if not os.path.exists('blacklist'):
    os.mknod('blacklist')
unfound_file = []
blacklist = open('blacklist', 'r').readlines()
file_path_ = sys.argv[1:]
for f in file_path_:
    try:
        process_file(f)
    except Exception as e:
        logger.exception(e)

if len(unfound_file) > 0:
    print('CAN NOT FIND ANY SUB FILE FOR THESE FILES:\n')
    for f in unfound_file:
        logger.info(f)
    if '--delete' in sys.argv:
        for f in unfound_file:
            ltime = int(os.stat(f).st_mtime)
            logger.info(ltime)
            if ltime + 3600 * 24 * 10 < int(time_utils.time()):
                os.rename(f, f + '.bak')

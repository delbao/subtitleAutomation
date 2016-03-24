"""
download raw subtitle files from opensubtitles.org and subhd
"""
# !/usr/bin/python2
# -*- coding: utf-8 -*-
import logging
import sys
from os.path import splitext, basename, exists

from downloader.opensubtitle.opensubtitle import get_opensubtitle_sub
from downloader.shooter.shooter import get_shooter_sub
from merger.merge_subs import srt_merge

logger = logging.getLogger()

LOGGING_FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
DATE_FORMAT = '[%Y-%m-%d %H:%M:%S]'


def configure_logging():
    logging.root.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(datefmt=DATE_FORMAT, fmt=LOGGING_FORMAT)
    stream_handler.setFormatter(formatter)
    logging.root.addHandler(stream_handler)


def download_subtitles():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    configure_logging()
    files_paths = sys.argv[1:]

    for file_path in files_paths:
        try:
            logger.info('PROCESSING FILE:' + basename(file_path))
            check_error_messages = files_check_error_messages(file_path)
            if check_error_messages:
                logger.info(check_error_messages)
            else:
                get_subtitles_for_the_file(file_path)
        except Exception:
            logger.exception('error occurred on processing file %s', file_path)


def files_check_error_messages(file_path):
    if not exists(file_path):
        return '%s not found', file_path
    if exists(splitext(file_path)[0] + ".lrc"):
        return 'lrc file existed,quit now!'


def get_subtitles_for_the_file(file_path):
    result_subtitle_file = splitext(file_path)[0] + ".combined.srt"
    sub_shooter, lang_ = get_shooter_sub(file_path)
    if lang_ == 'chs_eng':
        srt_merge([sub_shooter], result_subtitle_file, 0, 1)
    if lang_ == 'chs':
        get_eng_from_open_subtitile(sub_shooter, file_path, result_subtitle_file)
    if lang_ == 'eng':
        get_chs_from_open_subtitle(sub_shooter, file_path, result_subtitle_file)
    if lang_ == 'none':
        get_both_subtitles_from_open_subtitle(file_path, result_subtitle_file)


def get_eng_from_open_subtitile(sub_shooter, file_path, result_subtitle_file):
    sub_eng = get_opensubtitle_sub(file_path)
    if not sub_eng:
        logger.info('english sub file not found')
        srt_merge([sub_shooter], result_subtitle_file, 0, 2)
    else:
        srt_merge([sub_eng, sub_shooter], result_subtitle_file, 0)


def get_chs_from_open_subtitle(sub_shooter, file_path, result_subtitle_file):
    open_subtitle = get_opensubtitle_sub(file_path, 'chs')
    if not open_subtitle:
        logger.info('chinese sub file not found')
        srt_merge([sub_shooter], result_subtitle_file, 0, 2)
    else:
        srt_merge([sub_shooter, open_subtitle], result_subtitle_file, 0)


def get_both_subtitles_from_open_subtitle(file_path, result_subtitle_file):
    open_subtitle_chs = get_opensubtitle_sub(file_path, 'chs')
    open_subtitle_eng = get_opensubtitle_sub(file_path)
    if open_subtitle_eng and open_subtitle_chs:
        srt_merge([open_subtitle_chs, open_subtitle_eng], result_subtitle_file, 0)
    elif open_subtitle_eng:
        srt_merge([open_subtitle_eng], result_subtitle_file, 0, 2)
        print 'chinese sub file not found'
    elif open_subtitle_chs:
        srt_merge([open_subtitle_chs], result_subtitle_file, 0, 2)
        print 'english sub file not found'
    else:
        logger.warning('NO SUB FILE FOUND for file: %s', file_path)


if __name__ == '__main__':
    download_subtitles()

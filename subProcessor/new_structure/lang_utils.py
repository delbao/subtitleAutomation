from logging import getLogger

logger = getLogger()


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

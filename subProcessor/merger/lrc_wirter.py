import re
from logging import getLogger

from merger.time_utils import ms_to_string

logger = getLogger()


def lrc_writer(file_path, subtitles, mode=0):
    lines = []
    last_finish = 0
    for index, rec in enumerate(subtitles, 1):
        if last_finish != 0 and rec.start - last_finish > 1000:
            time = ms_to_string(last_finish, 2)
            lines.append("[{_time}]{_mark}{_text}\n".format(_time=time, _mark='<R0>', _text='').encode('gb18030'))
        last_finish = rec.finish
        duration = rec.finish - rec.start
        time = ms_to_string(rec.start, 2)
        text = rec.text
        if mode == 1:
            parts = text.splitlines()
            lang = ''
            for i in range(len(parts)):
                p = parts[i]
                subtitle_language_ = subtitle_language(p.decode('utf-8'))
                if lang == '':
                    lang = subtitle_language_
                    continue
                if lang != subtitle_language_:
                    if subtitle_language == 'chs':
                        s = ''.join(parts[:i])
                        s += '|'
                        s += ''.join(parts[i:])
                        text = s
                    elif subtitle_language == 'eng':
                        s = ''.join(parts[i:])
                        s += '|'
                        s += ''.join(parts[:i])
                        text = s
                        break
        text = text.replace('\r\n', '')
        text = text.replace('\n', '')
        word_count = len(re.findall(r"[A-Za-z]+", text))
        num_count = len(re.findall(r"[0-9]+", text))
        mark = '<R1>'
        if word_count >= 8:
            mark = '<R2>'
        if word_count < 5:
            mark = '<R0>'
        if num_count > 30:
            mark = '<R0>'
        if duration > 5000:
            mark = '<R0>'
        if mode == 2:
            text = text.replace('|', '')
        lines.append("[{_time}]{_mark}{_text}\r\n".format(_time=time, _mark=mark, _text=text).encode('gb18030'))
    open(file_path, 'w').writelines(lines)
    logger.info('OUTPUT LRC FILE: %s', file_path.replace('.combined', ''))


def subtitle_language(buffer_):
    count_eng = 0
    for char in buffer_:
        if language(char) == 'chs':
            return 'chs'
        elif language(char) == 'eng':
            count_eng += 1
    if count_eng > 0:
        return 'eng'


def language(uchar):
    if u'\u4e00' <= uchar <= u'\u9fa5':
        return 'chs'
    if u'a' <= uchar <= u'z':
        return 'eng'

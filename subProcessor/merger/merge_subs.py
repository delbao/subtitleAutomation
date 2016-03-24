import argparse
import codecs
import os
import re
import sys
from collections import namedtuple
from logging import getLogger

logger = getLogger()

__author__ = 'wistful'
__version__ = '0.6'
__release_date__ = "04/06/2013"

SUB_RECORD = namedtuple('SUB_RECORD', ['start', 'finish', 'text'])


def print_version():
    print("srt_merge: version %s (%s)" % (__version__, __release_date__))


def srt_merge(in_srt_files, out_srt, offset=0, mode=0):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    subs, result = [], []
    map(sub_reader, in_srt_files)
    for index, in_srt in enumerate(in_srt_files):
        _diff = offset if index == 0 else 0
        subs.extend([(rec.start + _diff, rec.finish + _diff, index, rec.text)
                     for rec in sub_reader(in_srt)])
    subs.sort()
    index = 0
    while index < len(subs) - 1:
        start, finish, flag, sub_text = subs[index]
        text = [(flag, sub_text)]
        combined_line = False
        for i in range(index + 1, len(subs)):
            sub_rec = subs[i]
            start2, finish2, flag2, sub_text2 = sub_rec
            if start2 < finish:
                finish = max(finish, start + (finish2 - start2) * 2 / 3)
                if combined_line:
                    sub_text2 = sub_text2.replace('|', '')
                text.append((flag2, sub_text2))
                combined_line = True
            else:
                break
        index = i
        x = sorted(enumerate(text), key=lambda (n, item): (item[0], n))
        y = [record[1][1] for record in x]
        result.append(SUB_RECORD(start, finish, "".join(y)))
    sub_writer(out_srt, result)
    root, ext = os.path.splitext(out_srt)
    lrc_writer(root + ".lrc", result, mode)
    for file_ in in_srt_files:
        os.remove(file_)
    os.rename(out_srt, out_srt.replace('.combined', ''))
    os.rename(root + ".lrc", root.replace('.combined', '') + '.lrc')


def _check_cmd_args(args):
    for inSrt in args.get('inPaths', []):
        if not os.path.exists(inSrt):
            print "file {srt_file} not exist".format(srt_file=inSrt)
            return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inPaths', type=str, nargs='+',
                        help='srt-files that must be merged')
    parser.add_argument('outPath', type=str,
                        help='output file')
    parser.add_argument('--offset', action='store_const', const=0, default=0,
                        help='offset in msc (default: 0)')
    parser.add_argument('--version', action="store_true",
                        dest='version', help='version')
    if '--version' in sys.argv:
        print_version()
    else:
        args = vars(parser.parse_args())
        if _check_cmd_args(args):
            srt_merge(args.get('inPaths', []), args.get('outPath'), args.get('offset'))


def sub_reader(file_path):
    pattern_index = r"^\d+$"
    start = finish = None
    text = []
    utf16_le_bom = "\xff\xfe"
    if open(file_path, 'r').read(2) == utf16_le_bom:
        data = codecs.open(file_path, 'r', 'utf-16')
    else:
        data = open(file_path, 'r')
    for line in data:
        line = line.strip()
        if re.match(pattern_index, line):
            if start and finish:
                yield SUB_RECORD(start, finish,
                                 text='{0}\n'.format('\n'.join(text)))
                start = finish = None
            text = []
        elif '-->' in line:
            start, finish = parse_time(line)
        elif line:
            if file_path.find('.chs.srt') > 0 and len(text) == 0:
                line = '|' + line
            pattern = re.compile('{.*}|<.*>')
            line = pattern.sub('', line)
            text.append(line)
    if start and finish:
        yield SUB_RECORD(start, finish, text='{0}\n'.format('\n'.join(text)))


def sub_writer(file_path, subtitles):
    lines = ["{index}\n{time}\n{text}\n".format(index=str(index),
                                                time=parse_ms(rec.start,
                                                              rec.finish),
                                                text=rec.text.replace('|', ''))
             for index, rec in enumerate(subtitles, 1)]

    open(file_path, 'w').writelines(lines)
    print 'OTUPUT COMBINED SUB FILE:', file_path.replace('.combined', '')


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
        if mode == 1:
            parts = rec.text.splitlines()
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


def parse_ms(start, finish):
    return "%s --> %s" % (ms_to_string(start), ms_to_string(finish))


def ms_to_string(ms, style=1):
    it = int(ms / 1000)
    ms_ = ms - it * 1000
    ss = it % 60
    mm = ((it - ss) / 60) % 60
    hh = ((it - (mm * 60) - ss) / 3600) % 60
    if style is 1:
        return "%02d:%02d:%02d,%03d" % (hh, mm, ss, ms_)
    if style is 2:
        return "%d:%d.%03d" % (mm + 60 * hh, ss, ms_)


def parse_time(str_time):
    pattern_time = r"(?P<h1>\d+):(?P<m1>\d+):(?P<s1>\d+),(?P<ms1>\d+)" \
                   r"\W*-->\W*(?P<h2>\d+):(?P<m2>\d+):(?P<s2>\d+),(?P<ms2>\d+)$"
    try:
        match_result = re.match(pattern_time, str_time.strip()).groupdict()
    except AttributeError:
        return None, None
    ms_1 = get_ms(match_result['h1'], match_result['m1'], match_result['s1'], match_result['ms1'])
    ms_2 = get_ms(match_result['h2'], match_result['m2'], match_result['s2'], match_result['ms2'])
    return ms_1, ms_2


def get_ms(hours, minutes, seconds, milliseconds):
    return (int(seconds) + int(minutes) * 60 + int(hours) * 60 * 60) * 1000 + int(milliseconds)


if __name__ == '__main__':
    main()

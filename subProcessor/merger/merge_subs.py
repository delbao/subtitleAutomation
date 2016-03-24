import argparse
import codecs
import os
import re
import sys
from collections import namedtuple
from logging import getLogger

from merger.lrc_wirter import lrc_writer
from merger.time_utils import parse_ms, parse_time

logger = getLogger()

__author__ = 'wistful'
__version__ = '0.6'
__release_date__ = "04/06/2013"

SUB_RECORD = namedtuple('SUB_RECORD', ['start', 'finish', 'text'])


def merge():
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


def print_version():
    print("srt_merge: version %s (%s)" % (__version__, __release_date__))


def _check_cmd_args(args):
    for inSrt in args.get('inPaths', []):
        if not os.path.exists(inSrt):
            print "file {srt_file} not exist".format(srt_file=inSrt)
            return False
    return True


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
    logger.info('OTUPUT COMBINED SUB FILE:', file_path.replace('.combined', ''))


if __name__ == '__main__':
    merge()

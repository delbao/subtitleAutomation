import os
import re
import sys
import gzip
import codecs
import base64
import StringIO
import xmlrpclib
import file_utils

from hash import movie_hash
from query import query_yn
from format import format_movie_name, format_subtitle_output_file_name
from langdet import LanguageDetector
from time_utils import parse_time, parse_ms
from collections import namedtuple
from languages import english

NAME = 'subdl'
VERSION = '1.0.3'

osdb_server = "http://api.opensubtitles.org/xml-rpc"
xmlrpc_server = xmlrpclib.Server(osdb_server)
login = xmlrpc_server.LogIn("", "", "en", NAME)
osdb_token = login["token"]
SubRecord = namedtuple('SubRecord', ['start', 'finish', 'text'])
options = {'lang': 'eng',
           'download': 'first',
           'output': None,
           'existing': 'abort'
           }


class SubtitleSearchResult:
    def __init__(self, dict_):
        self.__dict__ = dict_


def search_subtitles(file_name, langs_search):
    movie_hash_ = movie_hash(file_name)
    movie_byte_size = os.path.getsize(file_name)
    search_list = [({'sublanguageid': langs_search,
                    'moviehash': movie_hash_,
                    'moviebytesisrt2lrcze': str(movie_byte_size)})]
    print >> sys.stderr, "Searching for subtitles for moviehash=%s..." % movie_hash_
    try:
        results = xmlrpc_server.SearchSubtitles(osdb_token, search_list)
    except Exception, e:
        raise SystemExit("Error in XMLRPC SearchSubtitles call: %s" % e)
    data = results['data']
    return data and [SubtitleSearchResult(d) for d in data]


def sub_reader(file_path):
    pattern_index = r"^\d+$"
    start = finish = None
    text = []
    utf16_le_bom = "\xff\xfe"
    if open(file_path, 'r')   .read(2) == utf16_le_bom:
        data = codecs.open(file_path, 'r', 'utf-16')
    else:
        data = open(file_path, 'r')
    for line in data:
        line = line.strip()
        if re.match(pattern_index, line):
            if start and finish:
                yield SubRecord(start, finish,
                                text='{0}\n'.format('\n'.join(text)))
                start = finish = None
            text = []
        elif '-->' in line:
            start, finish = parse_time(line)
        elif line:
            if file_path.find('.chs.srt') > 0 and len(text) == 0:
                line = '|' + line
            p = re.compile('{.*}|<.*>')
            line = p.sub('', line)
            text.append(line)
    if start and finish:
        yield SubRecord(start, finish, text='{0}\n'.format('\n'.join(text)))


def sub_writer(file_path, subtitles):
    lines = ["{index}\n{time}\n{text}\n".format(index=str(index),
                                                time=parse_ms(rec.start,
                                                              rec.finish),
                                                text=rec.text.replace('|', ''))
             for index, rec in enumerate(subtitles, 1)]

    open(file_path, 'w').writelines(lines)
    print 'OTUPUT COMBINED SUB FILE:', file_path.replace('.combined', '')


def download_subtitle(sub_id):
    try:
        answer = xmlrpc_server.DownloadSubtitles(osdb_token, [sub_id])
        subtitle_compressed = answer['data'][0]['data']
    except Exception, e:
        raise SystemExit("Error in XMLRPC DownloadSubtitles call: %s" % e)
    return g_unzip_str(base64.decodestring(subtitle_compressed))


def g_unzip_str(zs):
    return gzip.GzipFile(fileobj=StringIO.StringIO(zs)).read()


def language(uchar):
    if u'\u4e00' <= uchar <= u'\u9fa5':
        return 'chs'
    if u'a' <= uchar <= u'z':
        return 'eng'


def subtitle_language(buffer_):
    count_chs = 0
    count_eng = 0
    for b in buffer_:
        if language(b) == 'chs':
            count_chs += 1
        elif language(b) == 'eng':
            count_eng += 1
    if count_chs > 0:
        return 'chs'
    elif count_eng > 0:
        return 'eng'


def display_subtitle_search_results(search_results):
    print
    "Found %d results:" % (len(search_results))
    id_subtitle_max_len = 0
    movie_name_max_len = 0
    downloads_max_len = 0
    for subtitle in search_results:
        id_subtitle = subtitle.IDSubtitleFile
        id_subtitle_max_len = max(id_subtitle_max_len, len(id_subtitle))
        movie_name = format_movie_name(subtitle.MovieName)
        movie_name_max_len = max(movie_name_max_len, len(movie_name))
        downloads = subtitle.SubDownloadsCnt
        downloads_max_len = max(downloads_max_len, len(downloads))
    n = 0
    max_len = len(repr(len(search_results)))
    for subtitle in search_results:
        n += 1
        id_subtitle = subtitle.IDS
        lang = subtitle.ISO639
        movie_name = format_movie_name(subtitle.MovieName)
        file_name = subtitle.Subfile_name
        rating = subtitle.SubRating
        downloads = subtitle.SubDownloadsCnt
        print ''
        if options['download'] == 'query':
            print "%s." % repr(n).rjust(max_len),
        print "#%s [%s] [Rat:%s DL:%s] %s %s " % (id_subtitle.rjust(id_subtitle_max_len),
                                                  lang,
                                                  rating.rjust(4),
                                                  downloads.rjust(downloads_max_len),
                                                  movie_name.ljust(movie_name_max_len),
                                                  file_name)


def select_search_result_by_id(id_, search_results):
    for search_result in search_results:
        if search_result.IDSubtitleFile == id_:
            return search_result
    raise SystemExit("Search results did not contain subtitle with id %s" % id_)


def download_and_save_subtitle(sub_id, destfile_name):
    if os.path.exists(destfile_name):
        if options['existing'] == 'abort':
            print "Subtitle %s already exists; aborting (try --interactive)." % destfile_name
            raise SystemExit(3)
        elif options['existing'] == 'bypass':
            print "Subtitle %s already exists; bypassing." % destfile_name
            return
        elif options['existing'] == 'overwrite':
            print "Subtitle %s already exists; overwriting." % destfile_name
        elif options['existing'] == 'query':
            if query_yn("Subtitle %s already exists.  Overwrite [y/n]?" % destfile_name):
                pass
            else:
                raise SystemExit("File not overwritten.")
        else:
            raise Exception("internal error: bad option.existing=%s" % options['existing'])
    print >> sys.stderr, "Downloading #%s to %s..." % (sub_id, destfile_name),
    s = download_subtitle(sub_id)
    if s[:3] == codecs.BOM_UTF8:
        s = s[3:]
    s = s.decode('utf-8', 'replace')
    if is_english(s):
        print "test"
        file_utils.write_file(destfile_name, s)
        print >> sys.stderr, "done, wrote %d bytes." % (len(s))
        return 'ok'
    else:
        return 'none'


def is_english(s):
    lang = LanguageDetector.detect(s)
    return lang == english


def auto_download_and_save(video_name, search_result, downloaded=None):
    output_file_name = format_subtitle_output_file_name(video_name, search_result)
    if downloaded is not None:
        if output_file_name in downloaded:
            raise SystemExit("Already wrote to %s!  Uniquely output file format." % output_file_name)
        downloaded[output_file_name] = 1
    res = download_and_save_subtitle(search_result.IDSubtitleFile, output_file_name)
    if res == 'none':
        return 'none'
    else:
        return output_file_name

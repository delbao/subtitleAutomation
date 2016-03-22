from StringIO import StringIO
import base64
import codecs
import getopt
import gzip
import os
import sys
import xmlrpclib
from logging import getLogger
import struct

from os.path import splitext

from new_structure.lang_getter.langdet import LanguageDetector
from new_structure.lang_getter.languages import english

logger = getLogger()

NAME = 'subdl'
VERSION = '1.0.3'
osdb_server = "http://api.opensubtitles.org/xml-rpc"
xmlrpc_server = xmlrpclib.Server(osdb_server)
login = xmlrpc_server.LogIn("", "", "en", NAME)
osdb_token = login["token"]

options = {
    'lang': 'eng',
    'download': 'first',
    'output': None,
    'existing': 'abort'
}


def get_opensubtitle_sub(file_path, lang_='eng'):
    video_file_name = parse_args(['--existing=overwrite', '--lang=' + lang_, file_path])
    search_results = search_subtitles(video_file_name, options['lang'])
    if not search_results:
        return
    if options['download'] == 'none':
        raise SystemExit
    elif options['download'] == 'all':
        return auto_download_and_save(video_file_name, search_results[0])
    elif options['download'] == 'first':
        downloaded = {}
        for search_result in search_results:
            res = auto_download_and_save(video_file_name, search_result, downloaded)
            if res == 'none':
                continue
            else:
                return res
    elif options['download'] == 'query':
        number_input = query_num("Enter result to download [1..%d]:" % (len(search_results)),
                                 min_=1, max_=len(search_results))
        auto_download_and_save(video_file_name, search_results[number_input - 1])
    elif is_number(options['download']):
        search_result = select_search_result_by_id(options['download'], search_results)
        auto_download_and_save(video_file_name, search_result)
    else:
        raise Exception("internal error: bad option['download']=%s" % options['download'])


class SubtitleSearchResult:
    def __init__(self, dict_):
        self.__dict__ = dict_


def search_subtitles(file_name, langs_search):
    movie_hash_ = movie_hash(file_name)
    movie_byte_size = os.path.getsize(file_name)
    search_list = [({'sublanguageid': langs_search,
                     'moviehash': movie_hash_,
                     'moviebytesisrt2lrcze': str(movie_byte_size)})]
    logger.info("Searching for subtitles for moviehash=%s...", movie_hash_)
    try:
        results = xmlrpc_server.SearchSubtitles(osdb_token, search_list)
    except Exception, e:
        raise SystemExit("Error in XMLRPC SearchSubtitles call: %s" % e)
    if results['data']:
        return [SubtitleSearchResult(data_el) for data_el in results['data']]
    else:
        return results['data']


def auto_download_and_save(video_file_name, search_result, downloaded=None):
    output_file_name = format_subtitle_output_file_name(video_file_name, search_result)
    if downloaded is not None:
        if output_file_name in downloaded:
            raise SystemExit("Already wrote to %s!  Uniquely output file format." % output_file_name)
        downloaded[output_file_name] = 1
    res = download_and_save_subtitle(search_result.IDSubtitleFile, output_file_name)
    if res == 'none':
        return 'none'
    else:
        return output_file_name


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
        with open(destfile_name, 'wb') as file_:
            file_.write(s)
        print >> sys.stderr, "done, wrote %d bytes." % (len(s))
        return 'ok'
    else:
        return 'none'


def is_english(string):
    return LanguageDetector.detect(string) == english


def select_search_result_by_id(id_, search_results):
    for search_result in search_results:
        if search_result.IDSubtitleFile == id_:
            return search_result
    raise SystemExit("Search results did not contain subtitle with id %s" % id_)


def download_subtitle(sub_id):
    try:
        answer = xmlrpc_server.DownloadSubtitles(osdb_token, [sub_id])
        subtitle_compressed = answer['data'][0]['data']
    except Exception, e:
        raise SystemExit("Error in XMLRPC DownloadSubtitles call: %s" % e)
    sub_stream = StringIO(base64.decodestring(subtitle_compressed))
    return gzip.GzipFile(fileobj=sub_stream).read()


def is_number(value):
    try:
        return int(value) > 0
    except ValueError:
        return False


def languages():
    languages_ = xmlrpc_server.GetSubLanguages('')['data']
    for lang in languages_:
        print lang['SubLanguageID'], lang['ISO639'], lang['LanguageName']
    raise SystemExit


def parse_args(args):
    try:
        opts, arguments = getopt.getopt(args, 'h?in', [
            'existing=', 'lang=', 'search-only=',
            'download=', 'output=', 'interactive',
            'list-languages',
            'version', 'versionx'])
    except getopt.GetoptError, e:
        raise SystemExit("%s: %s (see --help)" % (sys.argv[0], e))
    for option, value in opts:
        if option == '--versionx':
            print VERSION
            raise SystemExit
        elif option == '--version':
            print "%s %s" % (NAME, VERSION)
            raise SystemExit
        elif option == '--existing':
            if value in ['abort', 'overwrite', 'bypass', 'query']:
                pass
            else:
                raise SystemExit("Argument to --existing must be one of: abort, overwrite, bypass, query")
            options['existing'] = value
        elif option == '--lang':
            options['lang'] = value
        elif option == '--download':
            if value in ['all', 'first', 'query', 'none'] or is_number(value):
                pass
            else:
                raise SystemExit("Argument to --download must be numeric subtitle id or one: all, first, query, none")
            options['download'] = value
        elif option == '-n':
            options['download'] = 'none'
        elif option == '--output':
            options['output'] = value
        elif option == '--interactive' or option == '-i':
            options['download'] = 'query'
            options['existing'] = 'query'
        elif option == '--list-languages':
            languages()
        else:
            raise SystemExit("internal error: bad option '%s'" % option)
    if not options['output']:
        options['output'] = default_output_format()
    if len(arguments) != 1:
        raise SystemExit("syntax: %s [options] file_name.avi  (see --help)" % (sys.argv[0]))
    return arguments[0]


def query_num(info_message, min_, max_):
    while True:
        try:
            print info_message
            number_input = int(raw_input())
            if min_ <= number_input <= max_:
                return number_input
        except KeyboardInterrupt:
            raise SystemExit("Aborted")
        except ValueError:
            logger.warning('Failure on processing number')


def query_yn(input_message):
    while True:
        print input_message
        try:
            input_message = raw_input().lower()
            if input_message.startswith('y'):
                return True
            elif input_message.startswith('n'):
                return False
        except KeyboardInterrupt:
            raise SystemExit("Aborted")


def format_subtitle_output_file_name(video_name, search_result):
    video_base, video_ext = splitext(video_name)
    sub_base, sub_ext = splitext(search_result.SubFileName)
    repl = {
        '%': '%',
        'I': search_result.IDSubtitleFile,
        'm': video_base, 'M': video_ext,
        's': sub_base, 'S': sub_ext,
        'l': search_result.LanguageName,
        'L': search_result.ISO639
    }
    output_file_name = replace_format(options['output'], repl)
    assert output_file_name != video_name
    return output_file_name


def replace_format(input_, replacements):
    output = ''
    i = 0
    while i < len(input_):
        c = input_[i]
        if c == '%':
            i += 1
            c = input_[i]
            try:
                output += replacements[c]
            except:
                raise SystemExit("Bad '%s' in format specifier" % c)
        else:
            output += c
        i += 1
    return output


def default_output_format():
    if options['download'] == 'all':
        return "%m.%L.%I.%S"
    elif options['lang'] == 'all' or ',' in options['lang']:
        return "%m.%L.%S"
    else:
        return "%m.%S"


def movie_hash(name):
    longlong_format = '<Q'
    byte_size = struct.calcsize(longlong_format)
    assert byte_size == 8
    f = open(name, "rb")
    file_size = os.path.getsize(name)
    hash_ = file_size
    if file_size < 65536 * 2:
        raise Exception("Error hashing %s: file too small" % name)
    for x in range(65536 / byte_size):
        hash_ += struct.unpack(longlong_format, f.read(byte_size))[0]
        hash_ &= 0xFFFFFFFFFFFFFFFF
    f.seek(file_size - 65536, 0)
    for x in range(65536 / byte_size):
        hash_ += struct.unpack(longlong_format, f.read(byte_size))[0]
        hash_ &= 0xFFFFFFFFFFFFFFFF
    f.close()
    return "%016x" % hash_

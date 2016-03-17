#!/usr/bin/python2.7

# subdl - command-line tool to download subtitles from opensubtitles.org.
#
# Uses code from subdownloader (a GUI app).
import os
import sys
import struct
import xmlrpclib
import StringIO
import gzip
import base64
import getopt
import det
import codecs

__doc__ = '''\
Syntax: subdl [options] moviefile.avi

Subdl is a command-line tool for downloading subtitles from opensubtitles.org.

By default, it will search for English subtitles, display the results,
download the highest-rated result in the requested language and save it to the
appropriate file_name.

Options:
  --help               This text
  --version            Print version and exit
  --lang=LANGUAGES     Comma-separated list of languages in 3-letter code, e.g.
                       'eng,spa,fre', or 'all' for all.  Default is 'eng'.
  --list-languages     List available languages and exit.
  --download=ID        Download a particular subtitle by numeric ID.
  --download=first     Download the first search result [default].
  --download=all       Download all search results.
  --download=query     Query which search result to download.
  --download=none, -n  Display search results and exit.
  --output=OUTPUT      Output to specified output file_name.  Can include the
                       following format specifiers:
                         %I subtitle id
                         %m movie file base      %M movie file extension
                         %s subtitle file base   %S subtitle file extension
                         %l language (English)   %L language (2-letter ISO639)
                       Default is "%m.%S"; if multiple languages are searched,
                       then the default is "%m.%L.%S"; if --download=all, then
                       the default is "%m.%L.%I.%S".
  --existing=abort     Abort if output file_name already exists [default].
  --existing=bypass    Exit gracefully if output file_name already exists.
  --existing=overwrite Overwrite if output file_name already exists.
  --existing=query     Query whether to overwrite.
  --interactive, -i    Equivalent to --download=query --existing=query.
  '''

NAME = 'subdl'
VERSION = '1.0.3'

VERSION_INFO = '''\

This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

http://code.google.com/p/subdl/'''

osdb_server = "http://api.opensubtitles.org/xml-rpc"
xmlrpc_server = xmlrpclib.Server(osdb_server)
login = xmlrpc_server.LogIn("", "", "en", NAME)
osdb_token = login["token"]

options = {'lang': 'eng',
           'download': 'first',
           'output': None,
           'existing': 'abort'
           }


class subtitle_search_result:
    def __init__(self, dict):
        self.__dict__ = dict


def file_ext(file_name):
    return file_name[file_name.rfind('.') + 1:]


def file_base(file_name):
    return file_name[:file_name.rfind('.')]


def g_unzip_str(zs):
    return gzip.GzipFile(fileobj=StringIO.StringIO(zs)).read()


def writefile(file_name, str_):
    try:
        open(file_name, 'wb').write(str_)
    except Exception, e:
        raise SystemExit("Error writing to %s: %s" % (file_name, e))


def query_num(s, min_, max_):
    while True:
        print s
        try:
            n = raw_input()
        except KeyboardInterrupt:
            raise SystemExit("Aborted")
        try:
            n = int(n)
            if min_ <= n <= max_:
                return n
        except:
            pass


def query_yn(s):
    while True:
        print s
        try:
            s = raw_input().lower()
        except KeyboardInterrupt:
            raise SystemExit("Aborted")
        if s.startswith('y'):
            return True
        elif s.startswith('n'):
            return False


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


def search_subtitles(file_name, langs_search):
    movie_hash_ = movie_hash(file_name)
    movie_byte_size = os.path.getsize(file_name)
    search = [({'sublanguageid': langs_search,
                'moviehash': movie_hash_,
                'movie_byte_size': str(movie_byte_size)})]
    print >> sys.stderr, "Searching for subtitles for moviehash=%s..." % movie_hash_
    try:
        results = xmlrpc_server.search_subtitles(osdb_token, search)
    except Exception, e:
        raise SystemExit("Error in XMLRPC search_subtitles call: %s" % e)
    data = results['data']
    return data and [subtitle_search_result(d) for d in data]


def format_movie_name(s):
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    s = s.replace('"', "'")
    return '"%s"' % s


def display_subtitle_search_results(search_results):
    print
    "Found %d results:" % (len(search_results))
    id_subtitle_max_len = 0
    movie_name_max_len = 0
    downloads_max_len = 0
    for subtitle in search_results:
        id_subtitle = subtitle.IDSubtitleFile  # file = args
        id_subtitle_max_len = max(id_subtitle_max_len, len(id_subtitle))
        movie_name = format_movie_name(subtitle.MovieName)
        movie_name_max_len = max(movie_name_max_len, len(movie_name))
        downloads = subtitle.SubDownloadsCnt
        downloads_max_len = max(downloads_max_len, len(downloads))
    n = 0
    max_len = len(`len(search_results)`)
    for subtitle in search_results:
        n += 1
        id_subtitle = subtitle.IDSubtitleFile
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


def download_subtitle(sub_id):
    try:
        answer = xmlrpc_server.DownloadSubtitles(osdb_token, [sub_id])
        subtitle_compressed = answer['data'][0]['data']
    except Exception, e:
        raise SystemExit("Error in XMLRPC DownloadSubtitles call: %s" % e)
    return g_unzip_str(base64.decodestring(subtitle_compressed))


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
    if det.is_english(s):
        print
        "test"
        writefile(destfile_name, s)
        print >> sys.stderr, "done, wrote %d bytes." % (len(s))
        return 'ok'
    else:
        return 'none'


def replace_fmt(input_, replacements):
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
                raise SystemExit("Bad '%%s' in format specifier" % c)
        else:
            output += c
        i += 1
    return output


def format_subtitle_output_file_name(video_name, search_result):
    sub_name = search_result.Subfile_name
    repl = {
        '%': '%',
        'I': search_result.IDSubtitleFile,
        'm': file_base(video_name), 'M': file_ext(video_name),
        's': file_base(sub_name), 'S': file_ext(sub_name),
        'l': search_result.LanguageName,
        'L': search_result.ISO639
    }
    output_file_name = replace_fmt(options['output'], repl)
    assert output_file_name != video_name
    return output_file_name


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


def select_search_result_by_id(id_, search_results):
    for search_result in search_results:
        if search_result.IDSubtitleFile == id_:
            return search_result
    raise SystemExit("Search results did not contain subtitle with id %s" % id_)


def help_():
    print __doc__
    raise SystemExit


def is_number(value):
    try:
        return int(value) > 0
    except:
        return False


def languages():
    languages_ = xmlrpc_server.GetSubLanguages('')['data']
    for language in languages_:
        print language['SubLanguageID'], language['ISO639'], language['LanguageName']
    raise SystemExit


def default_output_fmt():
    if options['download'] == 'all':
        return "%m.%L.%I.%S"
    elif options['lang'] == 'all' or ',' in options['lang']:
        return "%m.%L.%S"
    else:
        return "%m.%S"


def parseargs(args):
    try:
        opts, arguments = getopt.getopt(args, 'h?in', [
            'existing=', 'lang=', 'search-only=',
            'download=', 'output=', 'interactive',
            'list-languages',
            'help', 'version', 'versionx'])
    except getopt.GetoptError, e:
        raise SystemExit("%s: %s (see --help)" % (sys.argv[0], e))
    for option, value in opts:
        if option == '--help' or option == '-h' or option == '-?':
            help_()
        elif option == '--versionx':
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
        options['output'] = default_output_fmt()
    if len(arguments) != 1:
        raise SystemExit("syntax: %s [options] file_name.avi  (see --help)" % (sys.argv[0]))
    return arguments[0]


def main(args):
    file_ = parseargs(args)
    if not os.path.exists(file_):
        return
    search_results = search_subtitles(file_, options['lang'])
    if not search_results:
        return
    if options['download'] == 'none':
        raise SystemExit
    elif options['download'] == 'all':
        return auto_download_and_save(file_, search_results[0])
    elif options['download'] == 'first':
        downloaded = {}
        for search_result in search_results:
            res = auto_download_and_save(file_, search_result, downloaded)
            if res == 'none':
                continue
            else:
                return res
    elif options['download'] == 'query':
        n = query_num("Enter result to download [1..%d]:" % (len(search_results)),
                      1, len(search_results))
        auto_download_and_save(file_, search_results[n - 1])
    elif is_number(options['download']):
        search_result = select_search_result_by_id(options['download'], search_results)
        auto_download_and_save(file_, search_result)
    else:
        raise Exception("internal error: bad option['download']=%s" % options['download'])

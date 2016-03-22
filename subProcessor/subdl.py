#!/usr/bin/python2.7

# subdl - command-line tool to download subtitles from opensubtitles.org.
#
# Uses code from subdownloader (a GUI app).
import getopt
from new_structure.file_utils import file_base, file_ext, default_output_format
from new_structure.subtitles import *

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
        except ValueError:
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


def format_movie_name(s):
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    s = s.replace('"', "'")
    return '"%s"' % s


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


def format_subtitle_output_file_name(video_name, search_result):
    sub_name = search_result.SubFileName
    repl = {
        '%': '%',
        'I': search_result.IDSubtitleFile,
        'm': file_base(video_name), 'M': file_ext(video_name),
        's': file_base(sub_name), 'S': file_ext(sub_name),
        'l': search_result.LanguageName,
        'L': search_result.ISO639
    }
    output_file_name = replace_format(options['output'], repl)
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


def help_():
    print __doc__
    raise SystemExit


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
        options['output'] = default_output_format()
    if len(arguments) != 1:
        raise SystemExit("syntax: %s [options] file_name.avi  (see --help)" % (sys.argv[0]))
    return arguments[0]



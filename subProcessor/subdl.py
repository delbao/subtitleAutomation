#!/usr/bin/python2.7

# subdl - command-line tool to download subtitles from opensubtitles.org.
#
# Uses code from subdownloader (a GUI app).
import getopt
from subtitles import *
from format import format_subtitle_output_file_name, default_output_format

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



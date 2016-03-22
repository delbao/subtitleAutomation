#!/usr/bin/python2.7

import getopt
from subtitles import *
from format import default_output_format


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



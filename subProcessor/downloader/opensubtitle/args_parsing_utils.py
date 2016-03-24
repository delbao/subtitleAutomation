import getopt
import sys
from logging import getLogger

from downloader.opensubtitle.constants import VERSION, NAME, options, xmlrpc_server

logger = getLogger()


def is_number(value):
    try:
        return int(value) > 0
    except ValueError:
        return False


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
            logger.info(VERSION)
            raise SystemExit()
        elif option == '--version':
            logger.info("%s %s" % (NAME, VERSION))
            raise SystemExit()
        elif option == '--existing':
            if value not in ['abort', 'overwrite', 'bypass', 'query']:
                raise SystemExit("Argument to --existing must be one of: abort, overwrite, bypass, query")
            options['existing'] = value
        elif option == '--lang':
            options['lang'] = value
        elif option == '--download':
            if value not in ['all', 'first', 'query', 'none'] or is_number(value):
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


def languages():
    languages_ = xmlrpc_server.GetSubLanguages('')['data']
    for lang in languages_:
        logger.info(' '.join((lang['SubLanguageID'], lang['ISO639'], lang['LanguageName'])))
    raise SystemExit()


def default_output_format():
    if options['download'] == 'all':
        return "%m.%L.%I.%S"
    elif options['lang'] == 'all' or ',' in options['lang']:
        return "%m.%L.%S"
    else:
        return "%m.%S"

import base64
import codecs
import gzip
import os
from StringIO import StringIO
from logging import getLogger

from downloader.opensubtitle.constants import options, xmlrpc_server, osdb_token
from downloader.opensubtitle.out_file_format_utils import format_subtitle_output_file_name
from downloader.opensubtitle.query_utils import query_yn
from lang_getter.langdet import get_language

logger = getLogger()


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
            logger.info("Subtitle %s already exists; aborting (try --interactive)." % destfile_name)
            raise SystemExit(3)
        elif options['existing'] == 'bypass':
            logger.info("Subtitle %s already exists; bypassing." % destfile_name)
            return
        elif options['existing'] == 'overwrite':
            logger.info("Subtitle %s already exists; overwriting." % destfile_name)
        elif options['existing'] == 'query':
            if query_yn("Subtitle %s already exists.  Overwrite [y/n]?" % destfile_name):
                pass
            else:
                raise SystemExit("File not overwritten.")
        else:
            raise Exception("internal error: bad option.existing=%s" % options['existing'])
    logger.info("Downloading #%s to %s..." % (sub_id, destfile_name))
    sub_content = download_subtitle(sub_id)
    if sub_content[:3] == codecs.BOM_UTF8:
        sub_content = sub_content[3:]
    sub_content = sub_content.decode('utf-8', 'replace')
    if is_english(sub_content):
        with open(destfile_name, 'wb') as out_file:
            out_file.write(sub_content)
        logger.info("done, wrote %d bytes." % (len(sub_content)))
        return 'ok'
    else:
        return 'none'


def is_english(string):
    return get_language(string) == 'en'


def download_subtitle(sub_id):
    try:
        answer = xmlrpc_server.DownloadSubtitles(osdb_token, [sub_id])
        subtitle_compressed = answer['data'][0]['data']
    except Exception, e:
        raise SystemExit("Error in XMLRPC DownloadSubtitles call: %s" % e)
    sub_stream = StringIO(base64.decodestring(subtitle_compressed))
    return gzip.GzipFile(fileobj=sub_stream).read()

import os
import struct
from logging import getLogger

from downloader.opensubtitle.args_parsing_utils import is_number, parse_args
from downloader.opensubtitle.constants import xmlrpc_server, osdb_token, options
from downloader.opensubtitle.download_and_save_sub import auto_download_and_save
from downloader.opensubtitle.query_utils import query_num

logger = getLogger()


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
        return construct_search_results_collection(results)
    else:
        return results['data']


def construct_search_results_collection(results):
    class SubtitleSearchResult:
        def __init__(self, dict_):
            self.__dict__ = dict_

    return [SubtitleSearchResult(data_el) for data_el in results['data']]


def select_search_result_by_id(id_, search_results):
    for search_result in search_results:
        if search_result.IDSubtitleFile == id_:
            return search_result
    raise SystemExit("Search results did not contain subtitle with id %s" % id_)


def movie_hash(name):
    longlong_format = '<Q'
    byte_size = struct.calcsize(longlong_format)
    assert byte_size == 8
    with open(name, "rb") as file_obj:
        file_size = os.path.getsize(name)
        hash_ = file_size
        if file_size < 65536 * 2:
            raise Exception("Error hashing %s: file too small" % name)
        for x in range(65536 / byte_size):
            hash_ += struct.unpack(longlong_format, file_obj.read(byte_size))[0]
            hash_ &= 0xFFFFFFFFFFFFFFFF
        file_obj.seek(file_size - 65536, 0)
        for x in range(65536 / byte_size):
            hash_ += struct.unpack(longlong_format, file_obj.read(byte_size))[0]
            hash_ &= 0xFFFFFFFFFFFFFFFF
    return "%016x" % hash_

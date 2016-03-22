import os

from format import format_subtitle_output_file_name
from parser_utils import parse_args, is_number, select_search_result_by_id
from query import query_num
from subtitles import options, search_subtitles, download_and_save_subtitle


def get_subtitle_from_opensubtitle(file_path, lang_='eng'):
    video_file_name = parse_args(['--existing=overwrite', '--lang=' + lang_, file_path])
    if not os.path.exists(video_file_name):
        return
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

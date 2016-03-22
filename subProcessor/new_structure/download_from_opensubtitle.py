import os
from query import query_num

from subProcessor.subdl import parse_args, auto_download_and_save, is_number, select_search_result_by_id
from subtitles import options, search_subtitles


def get_subtitle_from_opensubtitle(file_path, lang_='eng'):
    argv = ['--existing=overwrite', '--lang=' + lang_, file_path]
    return main(argv)


def main(args):
    file_ = parse_args(args)
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

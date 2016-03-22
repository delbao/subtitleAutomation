import os
from query import query_num

from subtitles import options, search_subtitles, download_and_save_subtitle
from parser_utils import parse_args, is_number, select_search_result_by_id
from format import format_subtitle_output_file_name


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

import subtitles
from file_utils import file_base, file_ext


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
    output_file_name = replace_format(subtitles.options['output'], repl)
    assert output_file_name != video_name
    return output_file_name


def default_output_format():
    if subtitles.options['download'] == 'all':
        return "%m.%L.%I.%S"
    elif subtitles.options['lang'] == 'all' or ',' in subtitles.options['lang']:
        return "%m.%L.%S"
    else:
        return "%m.%S"

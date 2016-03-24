from os.path import splitext

from downloader.opensubtitle.constants import options


def format_subtitle_output_file_name(video_name, search_result):
    video_base, video_ext = splitext(video_name)
    sub_base, sub_ext = splitext(search_result.SubFileName)
    repl = {
        '%': '%',
        'I': search_result.IDSubtitleFile,
        'm': video_base, 'M': video_ext,
        's': sub_base, 'S': sub_ext,
        'l': search_result.LanguageName,
        'L': search_result.ISO639
    }
    output_file_name = replace_format(options['output'], repl)
    assert output_file_name != video_name
    return output_file_name


def replace_format(input_, replacements):
    output = ''
    index = 0
    while index < len(input_):
        char = input_[index]
        if char == '%':
            index += 1
            char = input_[index]
            try:
                output += replacements[char]
            except:
                raise SystemExit("Bad '%s' in format specifier" % char)
        else:
            output += char
        index += 1
    return output

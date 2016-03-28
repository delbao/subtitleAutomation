import re


def parse_ms(start, finish):
    return "%s --> %s" % (ms_to_string(start), ms_to_string(finish))


def ms_to_string(ms, style=1):
    it = int(ms / 1000)
    ms_ = ms - it * 1000
    ss = it % 60
    mm = ((it - ss) / 60) % 60
    hh = ((it - (mm * 60) - ss) / 3600) % 60
    if style == 1:
        return "%02d:%02d:%02d,%03d" % (hh, mm, ss, ms_)
    if style == 2:
        return "%d:%d.%03d" % (mm + 60 * hh, ss, ms_)


def parse_time(str_time):
    pattern_time = r"(?P<h1>\d+):(?P<m1>\d+):(?P<s1>\d+),(?P<ms1>\d+)" \
                   r"\W*-->\W*(?P<h2>\d+):(?P<m2>\d+):(?P<s2>\d+),(?P<ms2>\d+)$"
    try:
        match_result = re.match(pattern_time, str_time.strip()).groupdict()
    except AttributeError:
        return None, None
    ms_1 = get_ms(match_result['h1'], match_result['m1'], match_result['s1'], match_result['ms1'])
    ms_2 = get_ms(match_result['h2'], match_result['m2'], match_result['s2'], match_result['ms2'])
    return ms_1, ms_2


def get_ms(hours, minutes, seconds, milliseconds):
    return (int(seconds) + int(minutes) * 60 + int(hours) * 60 * 60) * 1000 + int(milliseconds)

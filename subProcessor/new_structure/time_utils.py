import re


def parse_time(str_time):
    pattern_time = r"(?P<h1>\d+):(?P<m1>\d+):(?P<s1>\d+),(?P<ms1>\d+)" \
                   r"\W*-->\W*(?P<h2>\d+):(?P<m2>\d+):(?P<s2>\d+),(?P<ms2>\d+)$"
    try:
        d = re.match(pattern_time, str_time.strip()).groupdict()
    except AttributeError:
        return None, None
    return get_ms(d['h1'], d['m1'], d['s1'], d['ms1']), get_ms(d['h2'], d['m2'], d['s2'], d['ms2'])


def get_ms(h, m, s, ms):
    return (int(s) + int(m) * 60 + int(h) * 60 * 60) * 1000 + int(ms)


def ms_to_string(ms, style=1):
    it = int(ms / 1000)
    ms_ = ms - it * 1000
    ss = it % 60
    mm = ((it - ss) / 60) % 60
    hh = ((it - (mm * 60) - ss) / 3600) % 60
    if style is 1:
        return "%02d:%02d:%02d,%03d" % (hh, mm, ss, ms_)
    if style is 2:
        return "%d:%d.%03d" % (mm + 60 * hh, ss, ms_)


def parse_ms(start, finish):
    return "%s --> %s" % (ms_to_string(start), ms_to_string(finish))
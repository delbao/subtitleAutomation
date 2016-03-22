import re
from subtitles import subtitle_language
from time_utils import ms_to_string


def lrc_writer(file_path, subtitles, mode=0):
    lines = []
    last_finish = 0
    for index, rec in enumerate(subtitles, 1):
        if last_finish != 0 and rec.start - last_finish > 1000:
            time = ms_to_string(last_finish, 2)
            mark = '<R0>'
            text = ''
            lines.append("[{_time}]{_mark}{_text}\n".format(_time=time, _mark=mark, _text=text).encode('gb18030'))
        last_finish = rec.finish
        duration = rec.finish - rec.start
        time = ms_to_string(rec.start, 2)
        text = rec.text
        if mode == 1:
            text = text.replace('\r\n', '\n')
            parts = text.split('\n')
            lang = ''
            for i in range(0, len(parts)):
                p = parts[i]
                subtitle_language_ = subtitle_language(p.decode('utf-8'))
                if lang == '':
                    lang = subtitle_language_
                    continue
                if lang != subtitle_language_:
                    if subtitle_language == 'chs':
                        s = ''.join(parts[:i])
                        s += '|'
                        s += ''.join(parts[i:])
                        text = s
                    elif subtitle_language == 'eng':
                        s = ''.join(parts[i:])
                        s += '|'
                        s += ''.join(parts[:i])
                        text = s
                        break
        text = text.replace('\r\n', '')
        text = text.replace('\n', '')
        word_count = len(re.findall(r"[A-Za-z]+", text))
        num_count = len(re.findall(r"[0-9]+", text))
        mark = '<R1>'
        if word_count >= 8:
            mark = '<R2>'
        if word_count < 5:
            mark = '<R0>'
        if num_count > 30:
            mark = '<R0>'
        if duration > 5000:
            mark = '<R0>'
        if mode == 2:
            text = text.replace('|', '')
        lines.append("[{_time}]{_mark}{_text}\r\n".format(_time=time, _mark=mark, _text=text).encode('gb18030'))
    open(file_path, 'w').writelines(lines)
    print 'OUTPUT LRC FILE:', file_path.replace('.combined', '')

import hashlib
import re
from genericpath import getsize
from logging import getLogger

logger = getLogger()


def hash_for_shooter(path):
    with open(path, "rb") as file_obj:
        file_length = getsize(path)

        if file_length < 8192:
            return ""
        else:
            block_size = 4096
            offset_collection = [block_size, file_length / 3 * 2, file_length / 3, file_length - 8192]
            hash_result = ""
            for offset_el in offset_collection:
                file_obj.seek(int(offset_el))
                data_block = file_obj.read(block_size)
                if len(hash_result) > 0:
                    hash_result += ";"
                hash_result += hashlib.md5(data_block).hexdigest().lower()
            return hash_result


def srt_lang(input_buffer):
    count_chs = 0
    count_eng = 0
    for uchar in input_buffer:
        if lang(uchar) == 'chs':
            count_chs += 1
        elif lang(uchar) == 'eng':
            count_eng += 1
    if count_chs > 1000 and count_eng > len(input_buffer) / 5:
        logger.info("chs_eng srt is confirmed")
        return 'chs_eng'
    elif count_chs > 1000:
        logger.info("chs srt is confirmed")
        return 'chs'
    elif count_eng > len(input_buffer) / 5:
        logger.info('eng srt is confirmed')
        return 'eng'
    else:
        return 'none'


def lang(uchar):
    if u'\u4e00' <= uchar <= u'\u9fa5':
        return 'chs'
    if u'a' <= uchar <= u'z':
        return 'eng'


def convert_ass_to_srt(input_buffer):
    result_lines = []
    for index, line in enumerate(input_buffer.split("\n")):
        if line[:9] == "Dialogue:":
            result_lines.append("%d\n" % index)
            clean_line = re.sub("{.*?}", "", line)
            entries = clean_line[10:].strip().split(",")
            result_lines.append(
                "%s --> %s\n" % (entries[1].replace(".", ",") + "0", entries[2].replace(".", ",") + "0"))
            result_lines.append("".join(entries[9:]).replace("\N", "\n") + "\n")
            result_lines.append("\n")
    return ''.join(result_lines)


def byte2int(b_str, width):
    val = sum(ord(b) << 8 * n for (n, b) in enumerate(reversed(b_str)))
    if val >= (1 << (width - 1)):
        val -= (1 << width)
    return val

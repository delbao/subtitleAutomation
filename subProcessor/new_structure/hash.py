import os
import struct
import hashlib


def my_hash(path):
    fp = open(path, "rb")
    file_length = os.path.getsize(path)

    if file_length < 8192:
        return ""
    else:
        block_size = 4096
        offset = [block_size, file_length / 3 * 2, file_length / 3, file_length - 8192]
        hash_result = ""
        for i in range(0, 4):

            fp.seek(int(offset[i]))
            data_block = fp.read(block_size)
            hash_str = hashlib.md5(data_block)
            if len(hash_result) > 0:
                hash_result += ";"
            hash_result += hash_str.hexdigest().lower()
        return hash_result


def movie_hash(name):
    longlong_format = '<Q'
    byte_size = struct.calcsize(longlong_format)
    assert byte_size == 8
    f = open(name, "rb")
    file_size = os.path.getsize(name)
    hash_ = file_size
    if file_size < 65536 * 2:
        raise Exception("Error hashing %s: file too small" % name)
    for x in range(65536 / byte_size):
        hash_ += struct.unpack(longlong_format, f.read(byte_size))[0]
        hash_ &= 0xFFFFFFFFFFFFFFFF
    f.seek(file_size - 65536, 0)
    for x in range(65536 / byte_size):
        hash_ += struct.unpack(longlong_format, f.read(byte_size))[0]
        hash_ &= 0xFFFFFFFFFFFFFFFF
    f.close()
    return "%016x" % hash_

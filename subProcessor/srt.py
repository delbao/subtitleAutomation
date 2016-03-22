#! /usr/bin/env python
# -*- coding: utf-8 -*-
#    Copyleft 2011 wistful <wst public mail at gmail com>
#
#    This is a free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import hashlib
import doctest


__author__ = 'wistful'


class SrtFormatError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


def mark_in_black_list(file_path):
    blacklist = open('blacklist', 'a')
    data = open(file_path, 'r').read()
    blacklist.write(hashlib.md5(data).hexdigest() + "\n")
    blacklist.close()


if __name__ == '__main__':
    print doctest.testmod()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011 Björn Edström <be@bjrn.se>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import with_statement

import ConfigParser as configparser
import datetime
import os
import random
import shutil
import sqlite3
import sys


CONKEROR_RC_PATH = os.path.expanduser('~/.conkeror.mozdev.org/conkeror/')


class TemporaryCopyOfFile(object):
    '''Path handling of a temporary copy of a file. Will always unlink
       etc.
    '''
    def __init__(self, path):
        self.path = path
        filename = os.path.split(path)[1] + str(random.randint(0, 2**64))
        self.temp_path = '/tmp/%s.tmp' % (filename,)

    def __enter__(self):
        shutil.copyfile(self.path, self.temp_path)
        return self.temp_path

    def __exit__(self, type, value, traceback):
        os.unlink(self.temp_path)
        return False


def get_profile_path():
    '''Returns the path to the conkeror profile diretory.
    '''

    config = configparser.ConfigParser()
    config.read(os.path.join(CONKEROR_RC_PATH, 'profiles.ini'))

    # TODO: Support for multiple profiles perhaps?
    profile_path = config.get('Profile0', 'Path', 0)

    return os.path.join(CONKEROR_RC_PATH, profile_path)


def get_places_path():
    '''Returns the path to the bookmark database file.
    '''

    path = os.path.join(get_profile_path(), 'places.sqlite')
    return path


# TODO: This is just hacky...
if __name__ == '__main__':
    places_path = get_places_path()

    # TODO: Real command line parsing
    html = False
    if '--html' in sys.argv:
        html = True
        print '<html><head><meta http-equiv="content-type" content="text/html; charset=UTF-8"/></head><body>'

    with TemporaryCopyOfFile(places_path) as temp_path:
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()

        cursor.execute('''SELECT b.id, p.url, p.title, b.title, b.dateAdded
FROM moz_bookmarks
b INNER JOIN moz_places p ON b.fk = p.id
ORDER BY b.id DESC;''')

        for row in cursor:
            id, url, title1, title2, date = row
            date = datetime.datetime.fromtimestamp(date / 10.0**6)

            if html:
                print (u'''%s <a href="%s">%s</a><br>
''' % (date, url, title1)).encode('utf-8')
            else:
                print id
                print title1.encode('utf-8')
                print url.encode('utf-8')
                print date
                print

        conn.close()

    if html:
        print '</body></html>'

    sys.exit(0)

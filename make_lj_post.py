#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ftplib import FTP
from sys import argv
from string import split

import os


class Photo():
    """docstring for Photo"""
    URL = 'http://monastyrskiy.ru'
    HOST = 'monastyrskiy.ru'
    USER = 'dlm123'
    PASS = 'Dlmasd123!'

    FTP_PWD = argv[1]
    LOCAL_PWD = argv[2]
    COMMAND = argv[3]

    def ftpOpen(self):
        ftp = FTP(self.HOST, self.USER, self.PASS)
        #ftp.login()
        return ftp

    def makePost(self):
        f = Photo.ftpOpen(self)
        files = f.nlst(self.FTP_PWD)

        _counter = 1

        print '<div style="text-align: center;">'
        print '%i. <img src="%s/%s/%s"></div>\n\n' % (_counter,
                                                      self.URL,
                                                      self.FTP_PWD,
                                                      files[2])

        s = '<lj-cut text="Еще фото"><div style="text-align: center;">'
        print unicode(s, 'utf-8').encode('cp866')

        for i in xrange(3, len(files)):
            _counter += 1
            print '%i. <img src="%s/%s/%s">\n' % (_counter,
                                                  self.URL,
                                                  self.FTP_PWD,
                                                  files[i])

        print '</div><lj-like buttons="vkontakte, facebook" />'
        s = '<lj-repost button="Показать друзьям"></lj-repost>'
        print unicode(s, 'utf-8').encode('cp866')
        print '</lj-cut>'

        f.quit()

    def uploadPhotos(self):
        f = Photo.ftpOpen(self)

        path = split(self.FTP_PWD, '/')
        pwd = ''
        newDir = path[-1]

        for x in xrange(0, len(path) - 1):
            pwd = pwd + path[x] + '/'

        print 'Change dir to: %s' % pwd
        f.cwd(pwd)

        print "command %s" % self.COMMAND

        if self.COMMAND == 'rmdir':
            print "Remove dir: %s%s" % (pwd, newDir)
            f.cwd(newDir)
            files = f.nlst()
            for _file in xrange(2, len(files)):
                print 'Remove file: %s' % files[_file]
                f.delete(files[_file])
            print 'Remove dir: %s' % newDir
            f.cwd('/%s' % pwd)
            f.rmd(newDir)

        print 'Make new dir: %s' % newDir
        f.mkd(newDir)
        print 'Change dir to: %s' % newDir
        f.cwd(newDir)

        print 'Change local pwd to: %s' % self.LOCAL_PWD
        os.chdir(self.LOCAL_PWD)

        for l in os.listdir(self.LOCAL_PWD):
            if os.path.isfile(l):
                print 'Upload %s to %s' % (l, self.FTP_PWD)
                f.storbinary('STOR %s' % l, open(l, 'rb'))

        f.quit()


def main():
    p = Photo()
    p.uploadPhotos()
    p.makePost()


if __name__ == '__main__':
    main()

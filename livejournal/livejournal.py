#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlopen
from sys import argv
import html5lib
import sqlite3
import liveJournalBot
from datetime import date, datetime
from os import path
from string import split


def grpoupsParser():
    '''Занесение все пользователей из списка групп в таблицу users'''
    community = ('foto_history', 'ru_foto', 'prophotos_ru', 'foto_history', 'ru_travel')
    url = 'livejournal.com'
    args = '/profile/friendlist?socconns=friends&mode_full_socconns=1'

    connection = sqlite3.connect(getScriptPwd() + 'livejournal.db')
    #connection.execute('delete from users')
    cursor = connection.cursor()

    for comm in community:
        print 'Community: %s' % comm
        print 'http://%s.%s%s' % (comm, url, args)
        res = urlopen('http://%s.%s%s' % (comm, url, args))
        print 'Parsing html'
        parser = html5lib.HTMLParser(tree=html5lib.getTreeBuilder("lxml"))
        dom = parser.parse(res)
        root = dom.getroot()
        counter = 0
        skipped = 0

        print 'Adding users to DB'

        for node in root.findall(".//html:a",
                                namespaces={"html": "http://www.w3.org/1999/xhtml"}):
            try:
                #print node.get('href')
                cursor.execute('''INSERT INTO users
                    (name) VALUES ('?')''', node.text)
                counter += 1
            except:
                skipped += 1

        print '%s users added' % counter
        print '%s users skipped' % skipped

        connection.commit()

    print 'Total users', connection.execute('select count(*) from users').fetchone()

    cursor.close()
    connection.close()


def addFriends():

    sql = '''
        SELECT
            u.user_id, u.name
        FROM
            users u
        LEFT JOIN
            friends f
        ON
            u.user_id = f.user_id
        WHERE
            f.user_id IS NULL
        ORDER BY RANDOM()
        LIMIT 5
        '''

    connection = sqlite3.connect(getScriptPwd() + 'livejournal.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    for journal in cursor.execute('SELECT * FROM journals'):

        lj = liveJournalBot.LJbot(journal['login'], journal['password'])

        for user in connection.cursor().execute(sql):
            dt = date.today().isoformat()
            try:
                lj.addFriend(user['name'])
                log(u'%s add friend %s(%s) %s(%s)\n' % (datetime.now(),
                                          journal['login'],
                                          journal['journal_id'],
                                          user['name'],
                                          user['user_id']))
            except Exception:
                pass
            connection.execute('''INSERT INTO friends
                VALUES (?, ?, ?)''', (user['user_id'], journal['journal_id'], dt))

        lj.logout()

    connection.commit()
    connection.close()


def log(message=''):
    fh = open('/var/log/livejournal.log', 'a')
    fh.writelines(message.encode('utf-8'))
    fh.close()


def getScriptPwd():
    pwd = ''
    scriptpath = path.abspath(__file__)
    dirs = split(scriptpath, '/')
    for dir in dirs:
        if dir == dirs[-1]:
            break
        pwd += '%s/' % dir

    return pwd


def main():
    if len(argv) != 2:
        print 'Wrong argument!'
    elif argv[1] == 'groupsParser':
        grpoupsParser()
    elif argv[1] == 'addFriends':
        addFriends()
    else:
        print 'Wrong argument %s!' % argv[1]

if __name__ == '__main__':
    main()

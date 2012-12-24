#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import urllib
import urllib2
import hashlib
import re
from string import split


class ServerError (BaseException):
    pass


class AuthError (BaseException):
    pass


class ParseError (BaseException):
    pass


class LJbot (object):
    def __init__(self, login, password):
        self.login = login
        self.password = password

        self.flatServerUrl = u"http://www.livejournal.com/interface/flat"
        self.urlAddFriend = u'http://www.livejournal.com/friends/add.bml'
        self.urlEditFriend = u'http://www.livejournal.com/friends/edit.bml'
        self.urlProfile = u'http://www.livejournal.com/manage/profile/'
        self.urlLogOut = u'http://www.livejournal.com/logout.bml'
        self.urlLoginsManage = u'http://www.livejournal.com/manage/logins.bml'

        self.userPassword = password

        # Используемые регулярные выражения
        self.authFormRe = re.compile("(\\\\)?\"lj_form_auth(\\\\)?\" value=(\\\\)?\"(?P<auth>.*?)(\\\\)?\"", re.IGNORECASE| re.DOTALL | re.MULTILINE)
        self.authFormRemIdRe = re.compile("(\\\\)?\"remid(\\\\)?\" value=(\\\\)?\"(?P<remid>.*?)(\\\\)?\"", re.IGNORECASE| re.DOTALL | re.MULTILINE)

        self.cookie = self.loginAsUser(login, password)

        self.ljSession = self.cookie._cookies['.livejournal.com']['/']['ljsession'].value
        self.sessionId = split(self.ljSession, ':')[2][1:]

        text = self.openUrlWithCookie(self.urlProfile, self.cookie)

        self.auth_match = self.authFormRe.search(text)

        if not self.auth_match:
            raise ParseError

        cookieHandler = urllib2.HTTPCookieProcessor(self.cookie)
        self.opener = urllib2.build_opener(cookieHandler)

    def getLjFormAuth(self, url):
        text = self.openUrlWithCookie(url, self.cookie)
        _auth_match = self.authFormRe.search(text)

        print 'auth: ', _auth_match.group("auth")

        return _auth_match.group("auth")

    def parseResponse(self, textResponse):
        """
        Создать словарь по данным из ответа
        """
        elements = textResponse.split()
        names = elements[::2]
        values = elements[1::2]

        result = dict(zip(names, values))

        return result

    def getChallenge(self):
        """
        Получить оклик для авторизации
        """
        dataDict = {
                "mode": "getchallenge"
                }

        data = urllib.urlencode(dataDict)

        request = urllib2.Request(self.flatServerUrl, data)

        fp = urllib2.urlopen(request)
        text = fp.read()
        fp.close()

        response = self.parseResponse(text)
        return response

    def getAuthResponse(self, password, challenge):
        hpass = hashlib.md5(password).hexdigest()
        response = hashlib.md5(challenge + hpass).hexdigest()
        return response

    def loginAsUser(self, login, password):
        """
        Авторизация как посетитель сайта
        """
        challenge_resp = self.getChallenge()

        if challenge_resp["success"] != "OK":
            raise ServerError

        # Получим оклик
        challenge = challenge_resp["challenge"]

        # Получим ответ на оклик для авторизации
        auth_response = self.getAuthResponse(password, challenge)

        authData = urllib.urlencode({
                "chal": challenge,
                "response": auth_response,
                "user": login
                })

        server = "http://www.livejournal.com/login.bml"

        cookieHandler = urllib2.HTTPCookieProcessor()
        opener = urllib2.build_opener(cookieHandler)

        opener.addheaders = [
                ('User-Agent',
                 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11'),
                ]

        request = urllib2.Request(server, authData)

        fp = opener.open(request)
        fp.close()

        if len(cookieHandler.cookiejar) < 2:
            raise AuthError

        return cookieHandler.cookiejar

    def openUrlWithCookie(self, url, cookiejar):
        cookieHandler = urllib2.HTTPCookieProcessor(cookiejar)
        opener = urllib2.build_opener(cookieHandler)

        request = urllib2.Request(url)

        fp = opener.open(request)
        text = fp.read()
        fp.close()

        return text

    def loginClear(self, login, password):
        """
        Авторизация методом clear (лучше не пользоваться)
        """
        dataDict = {
                "mode": "login",
                "auth_method": "clear",
                "user": login,
                "password": password
                }

        data = urllib.urlencode(dataDict)

        request = urllib2.Request(self.flatServerUrl, data)

        fp = urllib2.urlopen(request)
        #text = fp.read()
        #info = fp.info()
        fp.close()

    def parseUrl(self, url):
        """
        Из адреса вычленить имя журнала и номер поста.
        Возвращает кортеж (username, id), например, для
        http://community.livejournal.com/ljournalist/314088.html:
        (ljournalist, 314088)
        """
        # Найдем номер поста и имя пользователя
        if url.startswith("http://community.livejournal.com"):
            # Сообщество
            urlRe = re.compile("http://community.livejournal.com/(?P<name>.*)/(?P<id>\d+)\.html", re.IGNORECASE)
        else:
            urlRe = re.compile("http://(?P<name>.*).livejournal.com/(?P<id>\d+)\.html", re.IGNORECASE)

        url_match = urlRe.search(url)

        if url_match == None:
            raise ParseError

        return url_match.group("name"), url_match.group("id")

    def logout(self):
        challenge = self.doCall({"mode": "getchallenge"})["challenge"]

        params = {
            'mode': 'sessionexpire',
            'user': self.login,
            'auth_method': "challenge",
            'auth_challenge': challenge,
            'auth_response': self.getAuthResponse(self.userPassword, challenge),
            # Kill all session
            'expireall': 'true',
            # You can get the id of a session from the third element of the session: ws:username:session_id:auth_code
            #'expire_id_num': self.sessionId,
        }

        self.doCall(params)

    def _logout(self, user):
        '''Так и не удалось заставить работать таким способом,
        сессия не удаляется'''

        fh = open('/home/monastyrskiy/tmp/lj-4.html', 'w')
        fh.write(self.openUrlWithCookie(self.urlLogOut, self.cookie))
        fh.close()

        #submit = u'Выход'
        #Submit = u'Log out'
        #lj_form_auth = self.getLjFormAuth(self.urlLoginsManage)

        params = {
            #'action:killall:': 1
            'user:': user,
            'sessid:': self.sessionId,
            #'_submit:': submit.encode('utf-8'),
            '_submit': 'Log out'
        }

        #params = {
        #    'lj_form_auth:': lj_form_auth,
        #    'x:': self.sessionId,
        #    'submit:': 'X',
        #}

        print 'params: ', params

        params_encoded = urllib.urlencode22(params)
        print 'params_encoded: ', params_encoded

        request = urllib2.Request(self.urlLogOut, params_encoded)

        cookieHandler = urllib2.HTTPCookieProcessor(self.cookie)
        _opener = urllib2.build_opener(cookieHandler)

        fp = _opener.open(request)

        fh = open('/home/monastyrskiy/tmp/lj-3.html', 'w')
        fh.write(fp.read())
        fh.close()

        fp.close()

        print ''
        print self.cookie
        self.cookie.clear()
        print self.cookie

    def addFriend(self, user):
        url = self.urlAddFriend + '?user=%s' % user
        text = self.openUrlWithCookie(url, self.cookie)
        remid_match = self.authFormRemIdRe.search(text)
        auth_match = self.authFormRe.search(text)

        remid = remid_match.group('remid')
        lj_form_auth = auth_match.group("auth")

        #cookieuser = self.login.replace("-", "_")

        params = {
            #"cookieuser": cookieuser,
            "lj_form_auth": lj_form_auth,
            "mode": 'add',
            "user": user,
            'editfriend_add_1_fg': '#000000',
            'editfriend_add_1_bg': '#FFFFFF',
            'friend_tags_mode': 'A',
            'friend_tags': '',
            'remid': remid
        }

        params_encoded = urllib.urlencode(params)
        request = urllib2.Request(url, params_encoded)

        fp = self.opener.open(request)
        #fh = open('/home/monastyrskiy/tmp/%s.html' % user, 'w')
        #fh.write(fp.read())
        #fh.close()
        fp.read()
        fp.close()

    def postComment(self, url, message, subject="", replyto=0):
        urlServer = "http://www.livejournal.com/talkpost_do.bml"

        # Надо узнать:
        # + lj_form_auth
        # + journal
        # + itemid
        # + cookieuser

        text = self.openUrlWithCookie(url, self.cookie)

        # lj_form_auth
        auth_match = self.authFormRe.search(text)

        if not auth_match:
            raise ParseError

        lj_form_auth = auth_match.group("auth")

        cookieuser = self.login.replace("-", "_")

        journal, itemid = self.parseUrl(url)

        journal = journal.replace("-", "_")

        params = {
            "usertype": "cookieuser",
            "subject": subject.encode("utf-8"),
            "body": message.encode("utf-8"),
            "lj_form_auth": lj_form_auth,
            "cookieuser": cookieuser,
            "journal": journal,
            "itemid": itemid,
            "parenttalkid": replyto
        }

        cookieHandler = urllib2.HTTPCookieProcessor(self.cookie)
        opener = urllib2.build_opener(cookieHandler)

        params_encoded = urllib.urlencode(params)
        request = urllib2.Request(urlServer, params_encoded)

        fp = opener.open(request)
        result = fp.read()
        fp.close()

    def doCall(self, args):
        request = urllib2.Request(self.flatServerUrl, urllib.urlencode(args))
        resp = urllib2.urlopen(request)
        l = resp.read().split("\n")
        return dict(zip(l[::2], l[1::2]))


if __name__ == "__main__":
    try:
        postUrl = "http://monastyrskiy.livejournal.com/740.html"

        login = u""
        password = u""

        bot = LJbot(login, password)

        subj = unicode("Тест", "utf-8")
        message = unicode("Это тестовый пост!!!", "utf-8")

        bot.postComment(postUrl, message, subject=subj, replyto=0)

    except ServerError:
        print "Server Error"
    except AuthError:
        print "Auth Error"
    except ParseError:
        print "Parse Error"

#!/usr/bin/env python
# -*- coding: utf-8 -*-

#lj-api.py
#
# This a simple interface to livejournal's flat client/server protocol
#
#
# The documentation for the Client/Sertver protocols:
# http://www.livejournal.com/doc/server/ljp.csp.protocol.html
#
# The documentation for the flat Client/Server Protocol:
# http://www.livejournal.com/doc/server/ljp.csp.flat.protocol.html
#
#

import urllib2
import urllib
import md5
import re


def md5hex(s):
    m = md5.new()
    m.update(s)
    return m.hexdigest()

def doCall(args):
    request = urllib2.Request("http://www.livejournal.com/interface/flat", urllib.urlencode(args))
    resp = urllib2.urlopen(request)
    l = resp.read().split("\n");
    return dict(zip(l[::2], l[1::2]))
    
    
def _methodCall(methodname, username, passwordMD5, params):
    challenge = doCall({"mode":"getchallenge"})["challenge"]
    data = {
        "mode":methodname,
        "user":username,
        "auth_method":"challenge",
        "auth_challenge":challenge,
        "auth_response":md5hex(challenge+passwordMD5),
    }
    data.update(params)
    return doCall(data)
    
def getEvents(username, passwordMD5, **params):
    data = _methodCall("getevents", username, passwordMD5, params)

    r = re.compile("(events|prop)_(\\d+)_(\\w+)")
    events = [{} for i in range(int(data["events_count"]))]
    props = [{} for i in range(int(data["prop_count"]))]
    
    details = {"events":events}
    for name, value in data.items():
        match = r.match(name)
        if match:
            number = int(match.group(2))
            field = match.group(3)
            if match.group(1)=="events":
                events[number-1][field] = value
            else:
                props[number-1][field] = value
        else:
            details[name] = value
    
    propdict = {}
    for prop in props:
        itemid = prop['itemid']
        name = prop['name']
        value = prop['value']
        propdict.setdefault(itemid, {})[name] = value
    print propdict.keys()
    print [event['itemid'] for event in events]
    for event in events:
        eventprops = propdict.get(event.get('itemid'),{})
        event.update(eventprops)
    return details

def addEvent(username, passwordMD5, event):
    params = {
        "subject":subject,
        "event":parse(event)
    }
    data = _methodCall("postevent", username, passwordMD5)


def editEvent(username, passwordMD5, event):
    pass

if __name__ == '__main__':
    username = someUsername
    passwordMD5 = somePassword
    params = { 
        "noprops":"0",
        "selecttype":"lastn",
        "howmany":"20",
        "truncate":"100"
    }
    info = getEvents(username, passwordMD5, **params)
    print info.keys()
    events = info["events"]
    for title in [event.get('subject', event['event']) 
                  for event 
                  in events]:
        print title
    print events[0]
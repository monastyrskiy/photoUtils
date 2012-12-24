#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml.etree import parse
from os import listdir, path, chdir
from datetime import datetime, timedelta
from string import split
from pyexiv2 import ImageMetadata


def function():
    return None


class parseKML():
    kmlPwd = "d:\Dropbox\GPS"
    _track = {}

    def __init__(self):
        chdir(self.kmlPwd)

        for kml in listdir(self.kmlPwd):
            if path.isfile(kml):
                doc = parse(open(kml, 'r'))
                root = doc.getroot()
                for e in root.findall('.//{http://www.opengis.net/kml/2.2}when',
                                      namespaces=root.nsmap):
                    dt = datetime.strptime(split(e.text, '.')[0], '%Y-%m-%dT%H:%M:%S')
                    # По какой-то причине время в треке указано в нулевой зоне
                    dt += timedelta(hours=4)
                    self._track[dt] = split(e.getnext().text, ' ')

                self._trackKeys = sorted(self._track.iterkeys())

    def getTrack(self):
        return self._track

    def getTrackKeys(self):
        return self._trackKeys

    def getCoord(self, _datetime):
        _oldDT = datetime(1970, 1, 1, 0, 0)
        _date = None
        _coord = ''

        for dt in self._trackKeys:
            #if datetime > _oldDT and _oldDT > datetime(1970, 1, 1, 0, 0):
                # Вышли за пределы трека, координаты не обнаружены
                #break
            if _datetime < dt:
                # Фотография сделана раньше начала трека, координаты отсутствуют
                if _oldDT == datetime(1970, 1, 1, 0, 0):
                    break
                # Нужно найти наименьший интервал между двумя датами
                if _datetime - _oldDT < dt - _datetime:
                    _date, _coord = _oldDT, self._track[_oldDT]
                    break
                else:
                    _date, _coord = dt, self._track[dt]
                    break
            _oldDT = dt
        return _date, _coord

    def parsePhoto(self, photoPwd):
        chdir(photoPwd)

        for photo in listdir(photoPwd):
            if path.isfile(photo):
                metadata = ImageMetadata(photo)
                metadata.read()

                dt = metadata['Exif.Photo.DateTimeOriginal'].value

                _datetime, coord = self.getCoord(dt)

                #metadata['GPS.GPSVersionID'] = '2.2.0.0'

                #metadata['GPS.GPSLatitude'] = 0
                #metadata['GPS.GPSLongitude'] = 2
                #metadata[''] = 3
                #metadata.write()

                print '%s %s %s %s' % (photo, dt, _datetime, coord)

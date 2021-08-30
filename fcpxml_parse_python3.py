#!python3
# -*- coding: utf-8 -*-

'''
Author:  Johannes Dürr
License: GPL V3

Automator App is based on the python GPL V3 Script by Thomas Goodwin "Final Cut Pro X FCPXML Parser"
Company: Geon Technologies, LLC, 2014

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.



Project Purpose:
    Extract markers and time codes from Final Cut Pro X's FCPXML 1.3 formatted files

Usage:
    Pass an XML element into Marker.scanForMarker().  If markers are found, the resulting list is returned in the order of discovery.
'''
import sys, datetime, pdb
from xml.etree.ElementTree import parse


# Converts the '64bit/32bits' timecode format into seconds
def parseFCPTimeSeconds (timeString):
    vals = [float(n) for n in timeString.replace('s','').split('/')]
    if 1 == len(vals):
        val = vals[0]
    else:
        val = vals[0]/vals[1]
    return val

from string import Template
from collections import OrderedDict
from itertools import repeat

class DeltaTemplate(Template):
    delimiter = "%"

def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = '{:02d}'.format(hours)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)

class Marker:
    def __init__(self, name, startTime):
        self._name = name
        self._startTime = startTime

    @property
    def startTime(self):
        return self._startTime

    @property
    def name(self):
        return self._name

    @staticmethod
    def scanForMarker(element, time=[]):
        start = offset = 0
        try:
            start = parseFCPTimeSeconds(element.attrib['start'])
        except:
            pass

        try:
            offset = parseFCPTimeSeconds(element.attrib['offset'])
        except:
            pass

        m = []
        if 'chapter-marker' == element.tag:
            m.append(Marker(element.attrib['value'], start + sum(time)))
        else:
            time.append(offset - start)
            for el in element:
                m.extend(Marker.scanForMarker(el, list(time)))
        return m


# EXAMPLE:
# Import file and convert it to a list of markers sorted by ID and start time
xmlroot = parse(sys.argv[1]).getroot()
markers = sorted(Marker.scanForMarker(xmlroot), key=lambda s: s.startTime)

final_list=[]

# print "RESULTING ORDERED LIST:"
mylist = sorted(set(markers), key=lambda s: s.startTime)
unique_list = list(OrderedDict(zip(mylist, repeat(None))))

for m in unique_list:
    final_list.append("{1} {0}".format(m.name, strfdelta(datetime.timedelta(seconds=m.startTime), '%H:%M:%S')))
    
printList = list(OrderedDict(zip(final_list, repeat(None))))
printList.sort()

for n in printList:
    print(n)


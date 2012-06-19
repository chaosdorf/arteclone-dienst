#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import sys
import os, subprocess, shutil, select
import signal

import gobject

import re
import urllib2, xml.dom.minidom
import pynotify
import ConfigParser
import locale
import gettext
import pygtk
import BeautifulSoup as BS
pygtk.require('2.0')

from Catalog import Catalog, unescape_html, get_lang


catalog = Catalog()
lists = []
# Hier bitte Verzeichnis angeben wo die Dateien landen sollen
destdirectory = "/home/User/Download/arte/"

def unescape_xml(text):
    text = text.replace( "%3A", ":").replace( "%2F", "/").replace( "%2C", ",")
    return BS.BeautifulStoneSoup(text, convertEntities=BS.BeautifulStoneSoup.XML_ENTITIES).contents[0]

def get_rtmp_url( url_page, quality ):
    page_soup = BS.BeautifulSoup( urllib2.urlopen(url_page).read() )

    movie_object = page_soup.find("object", classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000")
    movie = movie_object.find("param", {"name":"movie"})
    movie_url = "http" + unescape_xml(movie['value'].split("http")[-1])

    xml_soup = BS.BeautifulStoneSoup( urllib2.urlopen(movie_url).read() )
    movie_url = xml_soup.find("video", {'lang': get_lang()})['ref']

    xml_soup = BS.BeautifulStoneSoup( urllib2.urlopen(movie_url).read() )
    base_soup = xml_soup.find("urls")
    movie_url = base_soup.find("url", {"quality": quality}).string
    return movie_url


# Gibt ein Array zurueck mit den Infos und Seitenlinks von den Artestreams
def on_actu():
    catalog
    datalist = open('/tmp/database2', 'w')
    print >> datalist, '\n'.join(['%s;%s;%s;%s' % (video[Catalog.TITLE_TAG], video[Catalog.DATE_TAG], video[Catalog.URL_TAG], video[Catalog.IMAGE_TAG]) for video in  catalog.videos])
    datalist.close()
      
    f = open ("/tmp/database2", "r")
    for line in f:
        t = line.split(";")
        lists.append([t[0], t[1], t[2], t[3]])
    return lists

# Prueft ob File im Verzeichnis schon vorhanden.

def proofExist(streaminfos, directory):
    proofedList = []
    dirList = os.listdir(directory)
    for i in streaminfos:
        newFile = i[0] + ".flv"
        exists = 0
        for fname in dirList:
            if fname == newFile:
                exists = 1
        if exists == 0:
            proofedList.append(i)    
    return proofedList
# Beginn mit Programm

# hole array mit Seitenlinks, Bezeichnung, Datum ... wo die Streams liegen
streaminfos = on_actu()
streaminfos = proofExist(streaminfos, destdirectory)
for i in streaminfos:
    try:
        url_page = i[2]
        rtmp_url = get_rtmp_url( url_page, quality = "hd" )
        print "start Download: " + i[0]
        destination = destdirectory + i[0] + ".flv"
        
        cmd_dl = 'flvstreamer -r "%s" --flv "%s"' % (rtmp_url, destination)
        os.system(cmd_dl)
    except IOError:
        # foo
        lol = "foo"
        

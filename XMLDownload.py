#!/usr/bin/python

import getopt
import sys
import urllib
import os
import xml.etree.ElementTree as ET
import string

def printHelp():
    print "Usage:\n"
    print "  To see this help: Run without parameters.\n"
    print "  XMLDownloader <options - see below>"

    print "  --rss <URL>               URL of the watched RSS channel.\n"
    print "  --db <path=./files.db>    Database of the application.\n"
    print "  --cache <path=./rss.xml>  Where to store the downloaded xml content."
    print "  --files <folder>          Folder with write permission, where to put downloaded files."

def idFromLink(link):
    start = string.find(link,"id=") + 3
    end = string.find(link, "/", start)
    return link[start:end]

def handleRSS(rss, db, cache, files):
    try:
        old_file_size = os.stat(cache).st_size
    except:
        old_file_size = 0

    try:
        urllib.urlretrieve(rss,cache)
        new_file_size = os.stat(cache).st_size
    except:
        print "Error while downloading the RSS content."
        sys.exit(1)

    if old_file_size == new_file_size:
        print "Content size is the same as the last retrieved file size. Skip the rest."
        sys.exit(0)

    try:
        tree = ET.parse(cache)
        channel = tree.getroot()[0]
    except:
        print "Cannot parse RSS content."
        sys.exit(1)

    database = []
    try:
        f = open(db, 'r')
        for item in f:
            database.append(item.rstrip('\n'))
        f.close()
    except:
        print "Debug: No old database found."

    new_database = []

    try:
        for item in channel.iter('item'):
            link = item.find('link').text
            if link in database:
                print link + " found in old database, skip item."
            else:
                print link + " not found in old database. Download it."
                try:
                    urllib.urlretrieve(link, files + idFromLink(link) + ".torrent")
                except:
                    print "Download failed."
            new_database.append(link)

    except:
        print "Problem with parsing items in RSS content."
        sys.exit(1)

    try:
        f = open(db, 'w')
        for item in new_database:
            f.write("%s\n" % item)
        f.close()
    except:
        print "Error: Cannot write database file."


def main(argv):
    if argv == 1:
        printHelp()
        sys.exit(1)

    rss = ''
    db = os.path.dirname(os.path.abspath(__file__)) + '/files.db'
    cache = 'rss.xml'
    files = ''

    try:
        opts, args = getopt.getopt(argv,"",["rss=", "db=", "cache=", "files="])
    except getopt.GetoptError:
        print "Argument handlink error."
	printHelp()
        sys.exit(1)

    for opt, arg in opts:
        if opt == "--rss":
            rss = arg
        elif opt == "--cache":
            cache = arg
        elif opt == "--db":
            db = arg
        elif opt == "--files":
            files = arg

    if rss == "" or files == "" :
        print "--rss and --files parameters are mandatory. See help: "
        printHelp()
        sys.exit(3)

    handleRSS(rss, db, cache, files)

if __name__ == "__main__":
   main(sys.argv[1:])


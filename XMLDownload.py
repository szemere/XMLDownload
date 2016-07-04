#!/usr/bin/python

import getopt
import sys
import urllib
import urllib2
import os
import xml.etree.ElementTree as ET
import string
import httplib

def printHelp():
    print "Usage:\n"
    print "  To see this help: Run without parameters.\n"
    print "  XMLDownloader <options - see below>"

    print "  --rss <URL>               URL of the watched RSS channel.\n"
    print "  --db <path=./files.db>    Database of the application.\n"
    print "  --cache <path=./rss.xml>  Where to store the downloaded xml content."
    print "  --files <folder>          Folder with write permission, where to put downloaded files."


# parseRSS
# Get the content of the RSS feed. Returns a dictionary of {id:link} pairs. Link is the direct URL to the downloadable
# files. ID is a unique identifier which will be cached for avoid multiple downloads of the same file. (Can be the same
# as the link.) Why ID is necessary? In my personal case link contains personal key's as part of the URL which I don't
# wanna store. Modify this function to customise the script to your own feed format.
def parseRSS(content):
    return_value = {}
    try:
        channel = ET.fromstring(content)[0]
        for item in channel.iter('item'):
            link = item.find('link').text

            start = string.find(link, "id=") + 3
            end = string.find(link, "/", start)
            id = link[start:end]

            return_value[id] = link
    except:
        print "Problem with parsing RSS content."
    return return_value


def handleRSS(rss, db, cache, files):
    try:
        old_file_size = os.stat(cache).st_size
    except:
        old_file_size = 0

    try:
        response = urllib2.urlopen(rss)
        rss_content = response.read()
        new_file_size = len(rss_content)
    except:
        print "Error while downloading the RSS content."
        sys.exit(1)

    if new_file_size == old_file_size:
        print "Content size is the same as the last time. Skip the rest."
        sys.exit(0)
    else:
        try:
            f = open(cache, 'w')
            f.write(rss_content)
            f.close()
        except:
            print "Error while writing RSS content into cache: " + cache

    old_database = []
    try:
        f = open(db, 'r')
        for item in f:
            old_database.append(item.rstrip('\n'))
        f.close()
    except:
        print "Debug: No old database found."

    items = parseRSS(rss_content)

    new_database = []
    for id, link in items.iteritems():
        if id in old_database:
            print "ID: " + id + " is found in database. Skip it."
        else:
            try:
                # TODO - get filenames as parameter.
                print "New ID: " + id + " to download. Link: " + link,
                sys.stdout.flush()
                urllib.urlretrieve(link, files + id + ".torrent")
                print "- Download finished."
                new_database.append(id)
            except urllib.HTTPError, e:
                print "Error while downloading " +id + " from link: " + link + "HTTPError = " + str(e.code)
            except urllib.URLError, e:
                print "Error while downloading " + id + " from link: " + link + "URLError = " + str(e.reason)
            except Exception:
                import traceback
                print 'generic exception: ' + traceback.format_exc()
                print "Error while downloading " + id + " from link: " + link

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
        print "Argument handling error."
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

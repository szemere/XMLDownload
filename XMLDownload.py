#!/usr/bin/python

import getopt
import sys
import urllib
import urllib2
import os
import xml.etree.ElementTree as ET
import string
import httplib
import logging

def printHelp():
    print "Usage:\n"
    print "  To see this help: Run without parameters.\n"
    print "  XMLDownloader <options - see below>"

    print "  --rss <URL>               URL of the watched RSS channel.\n"
    print "  --db <path=./files.db>    Database of the application.\n"
    print "  --cache <path=./rss.xml>  Where to store the downloaded xml content."
    print "  --files <folder>          Folder with write permission, where to put downloaded files."
    print "  --debug                   Enables debug logs"


# parseRSS
# Get the content of the RSS feed. Returns a dictionary
# of {id:link} pairs. Link is the direct URL to the downloadable
# files. ID is a unique identifier which will be cached for avoid
# multiple downloads of the same file. (Can be the same
# as the link.) Why ID is necessary? In my personal case link
# contains personal key's as part of the URL which I don't
# wanna store. Modify this function to customise the script to
# your own feed format.
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
        logging.error("Problem with parsing RSS content.")
    return return_value

def fetchRSS(rss):
    try:
        response = urllib2.urlopen(rss)
        rss_content = response.read()
    except urllib2.URLError as e:
        raise e

    return rss_content

def isSameRSS(rss_content, cache):
    try:
        old_file_size = os.stat(cache).st_size
    except:
        old_file_size = 0

    new_file_size = len(rss_content)

    return new_file_size == old_file_size

def handleRSS(rss, db, cache, files):

    if (not os.path.isdir(files)):
        raise OSError(files + " does not exists")

    rss_content = fetchRSS(rss)

    if isSameRSS(rss_content, cache):
        logging.debug("RSS is the same. Skip the rest.")
        return
    else:
        try:
            with open(cache, 'w') as f:
                f.write(rss_content)
        except IOError as e:
            raise e

    old_database = []
    try:
        f = open(db, 'r')
        for item in f:
            old_database.append(item.rstrip('\n'))
        f.close()
    except:
        logging.debug("No old database found.")

    items = parseRSS(rss_content)

    new_database = []
    for id, link in items.iteritems():
        if id in old_database:
            logging.debug("ID: " + id + " is found in database. Skip it.")
        else:
            try:
                # TODO - get filenames as parameter.
                logging.debug("New ID: {} to download. Link: {}".format(id,link))
                sys.stdout.flush()
                urllib.urlretrieve(link, "{}/{}.torrent".format(files, id))
                logging.debug("- Download finished.")
                new_database.append(id)
            except urllib2.HTTPError, e:
                logging.error("Error while downloading {} from link: {} HTTPError = {}".format(id,
                                                                                               link,
                                                                                               str(e.code)))
            except urllib2.URLError, e:
                logging.error("Error while downloading {} from link: {} HTTPError = {}".format(id,
                                                                                               link,
                                                                                               str(e.reason)))
            except Exception:
                import traceback
                logging.error('generic exception: ' + traceback.format_exc())
                logging.error("Error while downloading {} from link: {}".format(id,link))

    try:

        with open(db, 'w') as f:
            for item in new_database:
                f.write("%s\n" % item)
    except IOError as e:
        raise e


def main(argv):
    if argv == 1:
        printHelp()
        sys.exit(1)

    rss = ''
    db = os.path.dirname(os.path.abspath(__file__)) + '/files.db'
    cache = 'rss.xml'
    files = ''

    try:
        opts, args = getopt.getopt(argv,"",["rss=", "db=", "cache=", "files=", "debug"])
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
        elif opt == "--debug":
            logging.getLogger().setLevel(logging.DEBUG)

    if rss == "" or files == "" :
        print "--rss and --files parameters are mandatory. See help: "
        printHelp()
        sys.exit(3)

    try:
        handleRSS(rss, db, cache, files)
    except OSError as e:
        logging.error(str(e))
        sys.exit(1)
    except urllib2.URLError as e:
        logging.error(str(e));
        sys.exit(2)
    except IOError as e:
        logging.error(str(e));
        sys.exit(3)

logging.basicConfig(level=logging.ERROR)
if __name__ == "__main__":
    main(sys.argv[1:])

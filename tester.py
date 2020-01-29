import time
import multiprocessing
import socketserver
import http.server
import unittest
import tempfile
import shutil
import XMLDownload
import os

class XMLDownloadTester(unittest.TestCase):

    tempdir=None

    @classmethod
    def setUpClass(self):
        """Call before every test case."""
        self.tempdir = tempfile.mkdtemp(dir=".")

        PORT = 8000
        Handler = http.server.SimpleHTTPRequestHandler
        socketserver.TCPServer.allow_reuse_address = True
        httpd = socketserver.TCPServer(("", PORT), Handler)
        self.server_process = multiprocessing.Process(target=httpd.serve_forever)
        self.server_process.daemon = True

        os.chdir("./testdata/")
        self.server_process.start()
        os.chdir("../")

    @classmethod
    def tearDownClass(self):
        """Call after every test case."""
        self.server_process.terminate()
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def testNotExistingFilesFolder(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        rss = None
        db = None
        cache = None
        files = "notexisting_directoryname"

        with self.assertRaises(OSError):
            XMLDownload.handleRSS(rss, db, cache, files);

    def testParseRSS(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        valid_str="<channel><item><link>http://localhost:8000/id=1234567/</link></item></channel>"
        invalid_str1="<invalidxml></link>"
        invalid_str2="<channel><item><link></link></item></channel>"

        self.assertEqual(XMLDownload.parseRSS(valid_str), {"1234567" : "http://localhost:8000/id=1234567/"} )
        self.assertEqual(XMLDownload.parseRSS(invalid_str1), {} )
        self.assertEqual(XMLDownload.parseRSS(invalid_str2), {} )

    def testOptimisticCase(self):
        XMLDownload.handleRSS("http://localhost:8000/rss.xml",
                              "{}/db.txt".format(self.tempdir),
                              "{}/cache.txt".format(self.tempdir),
                              self.tempdir);
        self.assertEqual(os.path.exists("{}/1234567.torrent".format(self.tempdir)),True)

if __name__ == "__main__":
    unittest.main() # run all tests

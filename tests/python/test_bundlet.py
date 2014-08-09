#!/usr/bin/python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-09
#

"""
"""

from __future__ import print_function, unicode_literals

import sys
import os
import random
import shutil
import tempfile
import logging
import cPickle
import unittest
import time
import urllib2

bundler_dir = os.path.join(os.path.dirname(os.path.dirname(
                           os.path.abspath(os.path.dirname(__file__)))),
                           'bundler')
# bundlet_dir = os.path.join(bundler_dir, 'bundlets')

# sys.path.insert(0, bundlet_dir)

from pybundler import bundler


VERSION_FILE = os.path.join(bundler_dir, 'meta', 'version_major')

if os.getenv('AB_BRANCH'):
    BUNDLER_VERSION = os.getenv('AB_BRANCH')
else:
    BUNDLER_VERSION = open(VERSION_FILE).read().strip()

BUNDLER_ID = 'net.deanishe.alfred-bundler-python'
BUNDLER_DIR = os.path.expanduser(
    '~/Library/Application Support/Alfred 2/Workflow Data/'
    'alfred.bundler-{}'.format(BUNDLER_VERSION))
BUNDLER_PY_LIB = os.path.join(BUNDLER_DIR, 'bundler', 'AlfredBundler.py')
DATA_DIR = os.path.join(BUNDLER_DIR, 'data')
ICON_CACHE = os.path.join(DATA_DIR, 'assets', 'icons')
COLOUR_CACHE = os.path.join(DATA_DIR, 'color-cache')
PYTHON_LIB_DIR = os.path.join(DATA_DIR, 'assets', 'python')
HELPER_DIR = os.path.join(PYTHON_LIB_DIR, BUNDLER_ID)
UPDATE_JSON_PATH = os.path.join(HELPER_DIR, 'update.json')
BACKGROUND_COLOUR_FILE = os.path.join(DATA_DIR, 'theme_background')
ALFRED_PREFS_PATH = os.path.expanduser(
    '~/Library/Preferences/com.runningwithcrayons.Alfred-Preferences.plist')
PIP_INSTALLER_URL = ('https://raw.githubusercontent.com/pypa/pip/'
                     'develop/contrib/get-pip.py')
REQUIREMENTS_TXT = os.path.join(os.path.dirname(__file__), 'requirements.txt')

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s:%(lineno)s '
                           '%(levelname)-8s %(message)s',
                    datefmt='%H:%M:%S')

log = logging.getLogger('tests')

log.debug('Bundler version : {}'.format(BUNDLER_VERSION))


def setUp():
    pass


def tearDown():
    pass


class BundletTests(unittest.TestCase):

    def setUp(self):
        self.install_dir = os.path.join(
            PYTHON_LIB_DIR, 'net.deanishe.alfred-bundler-python-test')
        self.tempdir = tempfile.mkdtemp()
        self.tempfile = os.path.join(self.tempdir,
                                     'test-{}'.format(os.getpid()),
                                     'test-{}.test'.format(os.getpid()))
        self.testurl = 'https://raw.githubusercontent.com/deanishe/alfred-workflow/master/README.md'
        self.badurl = 'http://eu.httpbin.org/status/201'
        if os.path.exists(self.install_dir):
            shutil.rmtree(self.install_dir)
        if self.install_dir in sys.path:
            sys.path.remove(self.install_dir)

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)
        if os.path.exists(self.install_dir):
            shutil.rmtree(self.install_dir)
        if self.install_dir in sys.path:
            sys.path.remove(self.install_dir)

    def test_init(self):
        """Install Python libraries"""

        with self.assertRaises(ImportError):
            import addhrefs

        with open(REQUIREMENTS_TXT, 'wb') as file:
            file.write('addhrefs==0.9.6')

        # Install requirements
        bundler.init(REQUIREMENTS_TXT)

        # Correct version is installed
        import addhrefs
        self.assertTrue(addhrefs.__version__ == '0.9.6')
        self.assertTrue(os.path.exists(self.install_dir))

        # Update requirements with newer version
        with open(REQUIREMENTS_TXT, 'wb') as file:
            file.write('addhrefs==0.9.7')

        # Update installed libraries
        bundler.init(REQUIREMENTS_TXT)
        reload(addhrefs)
        self.assertTrue(addhrefs.__version__ == '0.9.7')

        # reset file
        with open(REQUIREMENTS_TXT, 'wb') as file:
            file.write('html==1.15')

    def test_asset(self):
        """Asset"""
        path = os.path.join(DATA_DIR, 'assets', 'utility',
                            'Terminal-Notifier', 'latest',
                            'terminal-notifier.app', 'Contents', 'MacOS',
                            'terminal-notifier')
        self.assertEqual(bundler.utility('Terminal-Notifier', 'latest'), path)
        self.assertEqual(bundler.asset('Terminal-Notifier', 'latest'), path)
        self.assertEqual(bundler.utility('Terminal-Notifier'), path)
        self.assertEqual(bundler.asset('Terminal-Notifier'), path)

    def test_icon(self):
        """Web icons"""
        # 404 for invalid font
        with self.assertRaises(urllib2.HTTPError):
            bundler.icon('spaff', 'adjust')

        # 404 for invalid character
        with self.assertRaises(urllib2.HTTPError):
            bundler.icon('fontawesome', 'banditry!')

        # ValueError for invalid colour
        with self.assertRaises(ValueError):
            bundler.icon('fontawesome', 'adjust', 'hubbahubba')

        # Ensure directories are created, valid icon is downloaded and returned
        path = os.path.join(ICON_CACHE, 'fontawesome', 'ffffff', 'adjust.png')
        dirpath = os.path.dirname(path)
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)

        icon = bundler.icon('fontawesome', 'adjust', 'fff')
        self.assertEqual(icon, path)
        self.assertTrue(os.path.exists(path))

        if os.path.exists(path):
            os.unlink(path)

        # Returns correctly altered icon. Here: dark icon on dark background
        # returns light icon instead
        os.environ['alfred_theme_background'] = 'rgba(0,0,0,1.0)'
        path = os.path.join(ICON_CACHE, 'fontawesome', 'ffffff',
                            'ambulance.png')
        icon = bundler.icon('fontawesome', 'ambulance', '000', True)

        self.assertEqual(icon, path)
        self.assertTrue(os.path.exists(path))

        # Icon is returned from cache
        icon = bundler.icon('fontawesome', 'ambulance', '000', True)
        self.assertEqual(icon, path)

        if os.path.exists(path):
            os.unlink(path)

    def test_bootstrap(self):
        """Bootstrap"""

        # Delete and reset bundler
        if os.path.exists(BUNDLER_DIR):
            shutil.rmtree(BUNDLER_DIR)

        bundler._bundler = None

        # Invalid URL
        url = bundler.BASH_BUNDLET_URL
        bundler.BASH_BUNDLET_URL = 'http://github.com/deanishe/alfred-workflow/biscuits-and-chips'
        if os.path.exists(BUNDLER_DIR):
            shutil.rmtree(BUNDLER_DIR)

        with self.assertRaises(bundler.InstallationError):
            bundler._bootstrap()

        # Script that always fails
        bundler.BASH_BUNDLET_URL = 'https://raw.githubusercontent.com/shawnrice/alfred-bundler/devel/tests/python/fail.sh'
        if os.path.exists(BUNDLER_DIR):
            shutil.rmtree(BUNDLER_DIR)

        with self.assertRaises(bundler.InstallationError):
            bundler._bootstrap()

        # Clean install
        bundler.BASH_BUNDLET_URL = url
        bundler._bootstrap()
        self.assertTrue(os.path.exists(BUNDLER_DIR))
        self.assertTrue(os.path.exists(BUNDLER_PY_LIB))

    def test_download(self):
        """Download"""
        # Download a file
        self.assertFalse(os.path.exists(self.tempfile))
        bundler._download(self.testurl, self.tempfile)
        self.assertTrue(os.path.exists(self.tempfile))

        with self.assertRaises(IOError):
            bundler._download(self.badurl, self.tempfile)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

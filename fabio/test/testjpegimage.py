#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Project: Fable Input Output
#             https://github.com/silx-kit/fabio
#
#    Copyright (C) European Synchrotron Radiation Facility, Grenoble, France
#
#    Principal author:       Jérôme Kieffer (Jerome.Kieffer@ESRF.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Test JPEG format
"""

from __future__ import print_function, with_statement, division, absolute_import

import unittest
import os
import sys
import tempfile
import shutil

from .utilstest import UtilsTest

logger = UtilsTest.get_logger(__file__)
fabio = sys.modules["fabio"]
from .. import jpegimage

TEST_DIRECTORY = None
# Temporary directory where storing test data


def setUpModule():
    global TEST_DIRECTORY
    TEST_DIRECTORY = tempfile.mkdtemp(prefix="%s_data_" % __name__)


def tearDownModule():
    shutil.rmtree(TEST_DIRECTORY)


class TestJpegImage(unittest.TestCase):
    """Test the class format"""

    def setUp(self):
        if jpegimage.Image is None:
            self.skipTest("PIL is not available")

    def test_read_uint8(self):
        filename = UtilsTest.getimage("rand_uint8.jpg.bz2")[:-4]
        image_format = jpegimage.JpegImage()
        image = image_format.read(filename)
        self.assertEqual(image.data.shape, (64, 64))
        self.assertIn("jfif", image.header)

    def test_read_failing_file(self):
        filename = os.path.join(TEST_DIRECTORY, "2.jpg")
        filename_source = UtilsTest.getimage("rand_uint8.jpg.bz2")[:-4]

        with open(filename_source, "r+b") as fsource:
            with open(filename, "w+b") as ftest:
                ftest.write(fsource.read())
                ftest.seek(1)
                ftest.write(b".")

        image_format = jpegimage.JpegImage()
        try:
            _image = image_format.read(filename)
            self.fail()
        except IOError:
            pass

    def test_read_empty_file(self):
        filename = os.path.join(TEST_DIRECTORY, "3.jpg")
        f = open(filename, "wb")
        f.close()

        image_format = jpegimage.JpegImage()
        try:
            _image = image_format.read(filename)
            self.fail()
        except IOError:
            pass

    def test_read_missing_file(self):
        filename = os.path.join(TEST_DIRECTORY, "4.jpg")

        image_format = jpegimage.JpegImage()
        try:
            _image = image_format.read(filename)
            self.fail()
        except IOError:
            pass


class TestPilNotAvailable(unittest.TestCase):

    def setUp(self):
        filename = UtilsTest.getimage("rand_uint8.jpg.bz2")[:-4]
        self.filename = filename

        self.old = jpegimage.Image

    def tearDown(self):
        jpegimage.Image = self.old
        self.filename = None
        self.data = None

    def open_image(self):
        return fabio.open(self.filename)

    def test_with_pil(self):
        if jpegimage.Image is None:
            self.skipTest("PIL is not available")
        image = self.open_image()
        self.assertIsInstance(image, jpegimage.JpegImage)
        self.assertEqual(image.data.shape, (64, 64))
        self.assertIn("jfif", image.header)

    def test_without_pil(self):
        try:
            old = jpegimage.Image
            jpegimage.Image = None
            try:
                _image = self.open_image()
                self.fail()
            except IOError:
                pass
        finally:
            jpegimage.Image = old


class TestJpegImageInsideFabio(unittest.TestCase):
    """Test the format inside the fabio framework"""

    def test_read_uint8(self):
        filename = UtilsTest.getimage("rand_uint8.jpg.bz2")[:-4]
        image = fabio.open(filename)
        self.assertIsInstance(image, jpegimage.JpegImage)
        self.assertEqual(image.data.shape, (64, 64))
        self.assertIn("jfif", image.header)


def suite():
    loader = unittest.defaultTestLoader.loadTestsFromTestCase
    testsuite = unittest.TestSuite()
    testsuite.addTest(loader(TestJpegImage))
    testsuite.addTest(loader(TestJpegImageInsideFabio))
    testsuite.addTest(loader(TestPilNotAvailable))
    return testsuite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

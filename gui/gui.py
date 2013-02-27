# DFF -- An Open Source Digital Forensics Framework
# Copyright (C) 2009-2013 ArxSys
# This program is free software, distributed under the terms of
# the GNU General Public License Version 2. See the LICENSE file
# at the top of the source tree.
#  
# See http://www.digital-forensic.org for more information about this
# project. Please do not directly contact any of the maintainers of
# DFF for assistance; the project provides a web site, mailing lists
# and IRC channels for your use.
# 
# Author(s):
#  Jeremy MOUNIER <jmo@digital-forensic.org>
# 
import sys

from PyQt4.QtGui import QApplication, QSplashScreen, QPixmap
from PyQt4.QtCore import Qt

from dff.api.loader.loader import loader

from dff.ui.gui.mainwindow import MainWindow
from dff.ui.gui.translator import Translator
from dff.ui.gui.resources import gui_rc

from dff.ui.ui import UI

class SplashScreen(QSplashScreen):
  def __init__(self, pixmap, windowFlag, versionNumber):
     QSplashScreen.__init__(self, pixmap, windowFlag)
     self.versionNumber = versionNumber

  def drawContents(self, painter):
     QSplashScreen.drawContents(self, painter) 
     painter.drawText(10, 178, "Version " + str(self.versionNumber))	


class GUI(QApplication, UI):
    def __init__(self, debug = False, verbosity = 0):
        """Launch GUI"""
	QApplication.__init__(self, sys.argv)
        UI.__init__(self, debug, verbosity)
        self.translator = Translator()
        self.installTranslator(self.translator.getGeneric())
        self.installTranslator(self.translator.getDFF())
        self.setApplicationName("Digital Forensics Framework")
        # Below are macros replaced by CMake using configure_file please don't
        # commit this file with macros replaced, view those macros definition
        # in the top level CMakeLists.txt
        self.setApplicationVersion("1.3.0")
        pixmap = QPixmap(":splash.png")
        self.splash = SplashScreen(pixmap, Qt.WindowStaysOnTopHint, self.applicationVersion())
        self.splash.setMask(pixmap.mask()) 

    def createMainWindow(self):
        return MainWindow(self, self.debug)

    def launch(self, modulesPaths = None):
        self.splash.show()
        if modulesPaths:
          self.loadModules(modulesPaths, self.splash.showMessage)
        
        self.mainWindow = self.createMainWindow()
        self.mainWindow.initDockWidgets()
        self.translator.loadLanguage()
        self.mainWindow.show()
        self.splash.finish(self.mainWindow)
        sys.exit(self.exec_())


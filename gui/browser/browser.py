# DFF -- An Open Source Digital Forensics Framework
# Copyright (C) 2009-2016 ArxSys
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
#  Frederic Baguelin <fba@arxsys.fr>


from PyQt4 import QtGui, QtCore

from dff.ui.gui.browser.nodesbrowser import NodesBrowser
from dff.ui.gui.browser.datatypesbrowser import DatatypesBrowser
from dff.ui.gui.browser.tagsbrowser import TagsBrowser
from dff.ui.gui.browser.processusbrowser import ProcessusBrowser

class Browser(QtGui.QTabWidget):
    def __init__(self, parent=None):
        QtGui.QTabWidget.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setTabPosition(QtGui.QTabWidget.South)
        self.setTabShape(QtGui.QTabWidget.Triangular)
        self.__nodesBrowser = NodesBrowser(self)
        self.addTab(self.__nodesBrowser, self.tr("Tree"))
        self.__datatypesBrowser = DatatypesBrowser(self)
        self.addTab(self.__datatypesBrowser, self.tr("Types"))
        self.__tagsBrowser = TagsBrowser(self)
        self.addTab(self.__tagsBrowser, self.tr("Tags"))
        self.__processusBrowser = ProcessusBrowser(self)
        self.addTab(self.__processusBrowser, self.tr("Processus"))

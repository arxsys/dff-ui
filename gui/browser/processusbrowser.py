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

from dff.ui.gui.core.standardviews import StandardFrozenView
from dff.ui.gui.nodes.nodesitems import NodeItem
from dff.ui.gui.processus.processusviews import ProcessusTreeView
from dff.api.taskmanager.taskmanager import TaskManager 
from dff.api.types.libtypes import typeId, ConfigManager


# Manage zoom / views switch / column add / ...
class AbstractBrowser():
    def __init__(self):
        pass

    def setTreeView(self):
        pass

    def nodesView(self):
        pass

    def attributesView(self):
        pass


class ProcessusBrowser(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.__taskManager = TaskManager()
        self.__modulesConfig = ConfigManager.Get()
        self.__splitter = QtGui.QSplitter()
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        viewsLayout = QtGui.QHBoxLayout()
        self.__processusTreeView = ProcessusTreeView()
        self.__splitter.addWidget(self.__processusTreeView)
        viewsLayout.addWidget(self.__splitter)
        self.layout().addLayout(viewsLayout)

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

from dff.ui.gui.core.standardviews import StandardFrozenView, StandardFrozenTreeView
from dff.ui.gui.nodes.nodesitems import NodeItem
from dff.ui.gui.nodes.nodesviews import NodesTreeView, NodesDetailedView, NodesIconView
from dff.api.vfs.libvfs import VFS
from dff.api.taskmanager.taskmanager import TaskManager 
from dff.api.types.libtypes import typeId, ConfigManager


class NodesBrowser(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)
        root = VFS.Get().GetNode("/")
        self.__taskManager = TaskManager()
        self.__modulesConfig = ConfigManager.Get()
        self.__splitter = QtGui.QSplitter()
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        viewsLayout = QtGui.QHBoxLayout()
        self.__nodesTreeView = StandardFrozenTreeView(NodesTreeView)
        #self.__nodesTreeView = NodesTreeView()
        self.__nodesTreeView.displayRecursion(True)
        self.__nodesTreeView.model().setRootUid(root.uid())
        
        self.__nodesDetailedView = StandardFrozenView(NodesDetailedView)
        self.__nodesDetailedView.model().setRootUid(root.uid())

        self.__nodesIconView = NodesIconView()
        self.__nodesIconView.setModel(self.__nodesDetailedView.model())
        self.connect(self.__nodesTreeView,
                     QtCore.SIGNAL("clicked(const QModelIndex&)"),
                     self.treeViewClicked)
        self.connect(self.__nodesDetailedView,
                     QtCore.SIGNAL("doubleClicked(const QModelIndex&)"),
                     self.__doubleClicked)
        self.__splitter.addWidget(self.__nodesTreeView)
        self.__splitter.addWidget(self.__nodesDetailedView)
        self.__splitter.addWidget(self.__nodesIconView)
        #self.__nodesIconView.hide()
        viewsLayout.addWidget(self.__splitter)
        self.layout().addLayout(viewsLayout)
        #zoomSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        #zoomSlider.setTickInterval(1)
        #zoomSlider.setMinimum(1)
        #zoomSlider.setMaximum(NodesIconView.MaximumZoomFactor)
        #self.layout().addWidget(zoomSlider)

    
    def treeViewClicked(self, index):
        uid, success = self.__nodesTreeView.model().data(index, NodeItem.UidRole).toULongLong()
        isRecursive = self.__nodesTreeView.model().data(index, NodeItem.RecursionRole).toBool()
        if success and uid >= 0:
            self.__nodesDetailedView.model().setRootUid(uid, isRecursive)
            

    def __doubleClicked(self, index):
        node = index.model().nodeFromIndex(index)
        if node is None:
            return
        if node.hasChildren() or node.isDir():
            treeIndex = self.__nodesTreeView.model().createIndexFromUid(node.uid())
            if treeIndex.isValid():
                self.__nodesTreeView.setCurrentIndex(treeIndex)
            self.__nodesDetailedView.model().setRootUid(node.uid())
        else:
            compatibleModules = node.compatibleModules()
            if len(compatibleModules) == 1:
                module = compatibleModules[0]
                message = QtGui.QMessageBox(QtGui.QMessageBox.Question,
                                            self.tr("About to apply " + module),
                                            self.tr("Do you want to apply " + module + "?"),
                                            QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                            self)
                action = message.exec_()
                if action == QtGui.QMessageBox.Yes:
                    config = self.__modulesConfig.configByName(module)
                    nodeArguments = config.argumentsByType(typeId.Node)
                    if len(nodeArguments) == 1:
                        nodeArgument = nodeArguments[0]
                        args = {}
                        args[nodeArgument.name()] = node
                        self.__taskManager.add(module, args, ["thread", "gui"])
            else:
                for module in compatibleModules:
                    print module

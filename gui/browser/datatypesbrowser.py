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


from qtpy import QtWidgets, QtCore

from core.standardviews import StandardFrozenView
from nodes.nodesitems import NodeItem
from datatypes.datatypesviews import DatatypesTreeView
from datatypes.datatypesmodels import DatatypesNodesModel
from nodes.nodesviews import NodesDetailedView, NodesIconView
#from dff.api.taskmanager.taskmanager import TaskManager 
#from dff.api.types.libtypes import typeId, ConfigManager


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


class DatatypesBrowser(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)
        #self.__taskManager = TaskManager()
        #self.__modulesConfig = ConfigManager.Get()
        self.__splitter = QtWidgets.QSplitter()
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        viewsLayout = QtWidgets.QHBoxLayout()
        self.__datatypesTreeView = DatatypesTreeView()
        self.__nodesDetailedView = StandardFrozenView(NodesDetailedView)
        self.__nodesDetailedView.setModel(DatatypesNodesModel())
        #self.__nodesDetailedView.setRootUid(root.uid())
        #self.__nodesDetailedView.doubleClicked.connect(self.__doubleClicked)

        self.__nodesIconView = NodesIconView()
        self.__nodesIconView.setModel(self.__nodesDetailedView.model())
        self.__datatypesTreeView.clicked.connect(self.treeViewClicked)
        self.__splitter.addWidget(self.__datatypesTreeView)
        self.__splitter.addWidget(self.__nodesDetailedView)
        self.__splitter.addWidget(self.__nodesIconView)
        self.__nodesIconView.hide()
        viewsLayout.addWidget(self.__splitter)
        self.layout().addLayout(viewsLayout)
        #zoomSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        #zoomSlider.setTickInterval(1)
        #zoomSlider.setMinimum(1)
        #zoomSlider.setMaximum(NodesIconView.MaximumZoomFactor)
        #self.layout().addWidget(zoomSlider)

    
    def treeViewClicked(self, index):
        if not index.isValid():
            return
        datatypes = self.__datatypesTreeView.model().datatypesFromIndex(index)
        self.__nodesDetailedView.model().setDatatypes(datatypes)


    def __doubleClicked(self, index):
        if not index.isValid():
            return
        node = index.model().nodeFromIndex(index)
        if node is None:
            return
        if node.hasChildren() or node.isDir():
            self.__nodesTreeView.setCurrentIndexFromUid(node.uid())
            self.__nodesDetailedView.setRootUid(node.uid())
        else:
            compatibleModules = node.compatibleModules()
            if len(compatibleModules) == 1:
                module = compatibleModules[0]
                message = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question,
                                            self.tr("About to apply " + module),
                                            self.tr("Do you want to apply " + module + "?"),
                                            QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No,
                                            self)
                action = message.exec_()
                if action == QtWidgets.QMessageBox.Yes:
                    config = self.__modulesConfig.configByName(module)
                    nodeArguments = config.argumentsByType(typeId.Node)
                    if len(nodeArguments) == 1:
                        nodeArgument = nodeArguments[0]
                        args = {}
                        args[nodeArgument.name()] = node
                        self.__taskManager.add(module, args, ["thread", "gui"])
            else:
                for module in compatibleModules:
                    print(module)

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
from dff.ui.gui.nodes.nodesviews import NodesTreeView, NodesDetailedView, NodesIconView, NodesListView
from dff.api.vfs.libvfs import VFS
from dff.api.taskmanager.taskmanager import TaskManager 
from dff.api.types.libtypes import typeId, ConfigManager
from dff.ui.gui.api.widget.propertytable import PropertyTable

from dff.ui.gui.core.standardmenus import ViewAppearanceMenu, ViewAppearanceSliderMenu

from dff.ui.gui.widget.preview import Preview


class NodesViewStackedWidget(QtGui.QStackedWidget):
    def __init__(self, parent=None):
        super(NodesViewStackedWidget, self).__init__(parent)
        self.__detailedView = None
        self.__listView = None
        self.__iconView = None
        self.__viewMenu = ViewAppearanceMenu()
        self.__viewMenu.setCheckable(True)
        self.__viewActions = QtGui.QAction(self.tr("View"), self)
        self.__viewMenu.triggered.connect(self.__selectViewAction)
        self.__viewActions.setMenu(self.__viewMenu)
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.setContentsMargins(0, 0, 0, 0)


    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        widget = self.currentWidget()
        if widget is not None:
            actions = widget.currentActions()
            menu.addActions(actions)
        menu.addAction(self.__viewActions)
        menu.exec_(event.globalPos())


    def setCurrentViewAction(self, viewActionData):
        if not viewActionData.isValid():
            return
        viewType, success = viewActionData.toInt()
        if not success:
            return
        for action in self.__viewMenu.actions():
            action.setChecked(False)
            if action.data() == viewActionData:
                action.setChecked(True)
        self.selectView(viewType)


    def __selectViewAction(self, action):
        if action is None:
            return
        data = action.data()
        if not data.isValid():
            return
        self.emit(QtCore.SIGNAL("viewActionChanged(QVariant&)"), data)
        viewType, success = data.toInt()
        if not success:
            return
        self.selectView(viewType)


    def selectView(self, viewType):
        idx = -1
        if viewType in [ViewAppearanceMenu.Icon512, ViewAppearanceMenu.Icon256,
                        ViewAppearanceMenu.Icon128, ViewAppearanceMenu.Icon64]:
            self.__iconView.setIconSize(QtCore.QSize(viewType, viewType))
            idx = self.indexOf(self.__iconView)
        elif viewType == ViewAppearanceMenu.Details:
            idx = self.indexOf(self.__detailedView)
        elif viewType == ViewAppearanceMenu.List:
            idx = self.indexOf(self.__listView)
        if idx != -1:
            self.setCurrentIndex(idx)


    def setDetailedView(self, view):
        self.__detailedView = view
        self.addWidget(view)


    def setListView(self, view):
        self.__listView = view
        self.addWidget(view)


    def setIconView(self, view):
        self.__iconView = view
        self.addWidget(view)


class CustomMenuButton(QtGui.QPushButton):
    def __init__(self, parent=None):
        super(CustomMenuButton, self).__init__(parent)
        self.__customMenu = None
        self.setIcon(QtGui.QIcon(":view_icon.png"))
        self.setText("")
        self.setFlat(True)
        self.setMinimumSize(44, 16)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                       QtGui.QSizePolicy.Fixed)
        self.setSizePolicy(sizePolicy)
        self.setContentsMargins(0, 0, 0, 0)
        self.clicked.connect(self.__popupSelection)


    def setCustomMenu(self, menu):
        if menu == self.__customMenu:
            return
        self.__customMenu = menu
        self.__customMenu.setWindowFlags(QtCore.Qt.Popup)


    def __popupSelection(self, checked=False):
        pos = self.mapToGlobal(self.pos())
        x = pos.x()
        y = pos.y() + self.height()
        self.__customMenu.move(x, y)
        self.__customMenu.show()


class NodesBrowser(QtGui.QWidget):
    def __init__(self, parent=None):
        super(NodesBrowser, self).__init__(parent)
        root = VFS.Get().GetNode("/")
        self.__taskManager = TaskManager()
        self.__modulesConfig = ConfigManager.Get()
        self.__splitter = QtGui.QSplitter()
        self.__splitter.setContentsMargins(0, 0, 0, 0)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        viewsLayout = QtGui.QHBoxLayout()
        viewsLayout.setContentsMargins(0, 0, 0, 0)

        self.__nodesTreeView = NodesTreeView()
        self.__nodesTreeView.displayRecursion(True)
        self.__nodesTreeView.model().setRootUid(root.uid())
        
        self.__nodesDetailedView = StandardFrozenView(NodesDetailedView)
        self.__nodesDetailedView.model().setRootUid(root.uid())

        self.__nodesIconView = NodesIconView()
        self.__nodesIconView.setModel(self.__nodesDetailedView.model())

        self.__nodesListView = NodesListView()
        self.__nodesListView.setModel(self.__nodesDetailedView.model())

        self.__stackedWidget = NodesViewStackedWidget()
        self.__stackedWidget.setDetailedView(self.__nodesDetailedView)
        self.__stackedWidget.setIconView(self.__nodesIconView)
        self.__stackedWidget.setListView(self.__nodesListView)

        viewSelection = CustomMenuButton()
        self.__viewMenu = ViewAppearanceSliderMenu()
        viewSelection.setCustomMenu(self.__viewMenu)
        self.connect(self.__stackedWidget,
                     QtCore.SIGNAL("viewActionChanged(QVariant&)"),
                     self.__viewMenu.setCurrentViewAction)
        self.connect(self.__viewMenu,
                     QtCore.SIGNAL("viewActionChanged(QVariant&)"),
                     self.__stackedWidget.setCurrentViewAction)

        self.layout().addWidget(viewSelection)
        self.connect(self.__nodesTreeView,
                     QtCore.SIGNAL("clicked(const QModelIndex&)"),
                     self.treeViewClicked)
        self.connect(self.__nodesDetailedView,
                     QtCore.SIGNAL("doubleClicked(const QModelIndex&)"),
                     self.__doubleClicked)
        self.connect(self.__nodesDetailedView,
                     QtCore.SIGNAL("clicked(const QModelIndex&)"),
                     self.__detailedClicked)
        self.connect(self.__nodesIconView,
                     QtCore.SIGNAL("clicked(const QModelIndex&)"),
                     self.__detailedClicked)


        self.__splitter.addWidget(self.__nodesTreeView)
        self.__splitter.addWidget(self.__stackedWidget)
        self.__attributes = PropertyTable(None)
        self.__splitter.addWidget(self.__attributes)
        self.__splitter.setStretchFactor(0, 20)
        self.__splitter.setStretchFactor(1, 55)
        self.__splitter.setStretchFactor(2, 25)
        viewsLayout.addWidget(self.__splitter)
        self.layout().addLayout(viewsLayout)


    def __detailedClicked(self, index):
        node = self.__nodeFromIndex(index)
        if node is not None:
            self.__attributes.fill(node)


    def __nodeFromIndex(self, index):
        data = index.model().data(index, NodeItem.UidRole)
        node = None
        if data.isValid():
            uid, success = data.toULongLong()
            if success and uid >= 0:
                node = VFS.Get().getNodeById(uid)
        return node

    
    def treeViewClicked(self, index):
        data = index.model().data(index, NodeItem.UidRole)
        if not data.isValid():
            return
        uid, success = data.toULongLong()
        if not success or uid < 0:
            return
        isRecursive = self.__nodesTreeView.model().data(index, NodeItem.RecursionRole).toBool()
        self.__nodesDetailedView.model().setRootUid(uid, isRecursive)


    def __doubleClicked(self, index):
        node = self.__nodeFromIndex(index)
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

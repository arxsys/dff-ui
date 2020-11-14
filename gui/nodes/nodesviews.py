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

from qtpy import QtCore, QtGui, QtWidgets

from core.standarditems import HorizontalHeaderItem
from core.standardviews import StandardTableView, StandardTreeView, StandardIconView, StandardListView
from core.standardwidgets import ScrollableLabel
from nodes.nodesitems import NodeItem
from nodes.nodesmodels import NodesListModel, NodesTreeModel
from nodes.nodesdelegates import NodesDelegate, NodesTreeDelegate, NodesIconDelegate


class NodesDetailedView(StandardTableView):
  def __init__(self, parent=None):
    super(NodesDetailedView, self).__init__(parent)
    delegate = NodesDelegate()
    self.setItemDelegate(delegate)
    model = NodesListModel()
    self.setModel(model)


class NodesTreeView(StandardTreeView):
  def __init__(self, parent=None):
    super(NodesTreeView, self).__init__(parent)
    self.displayRecursion(True)
    delegate = NodesTreeDelegate()
    delegate.displayRecursion(True)
    self.setItemDelegate(delegate)
    model = NodesTreeModel()
    self.setModel(model)
    self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
    self.__displayFilesAction = QtWidgets.QAction(self.tr("Display files"), self)
    self.__displayFilesAction.setCheckable(True)
    self.__displayFilesAction.triggered.connect(self.__displayFiles)
    propertiesAction = QtWidgets.QAction(self.tr("Properties"), self)
    propertiesAction.setShortcuts(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_P))
    propertiesAction.setShortcutContext(QtCore.Qt.WidgetShortcut)
    propertiesAction.triggered.connect(self.properties)
    self.addAction(self.__displayFilesAction)
    self.addAction(propertiesAction)
    self.__defaultActions = self.actions()


  def contextMenuEvent(self, event):
    menu = QtGui.QMenu()
    menu.addActions(self.__defaultActions)
    menu.exec_(event.globalPos())


  def properties(self):
    index = self.currentIndex()
    if index.isValid():
      location = index.data(NodeItem.PathRole)
      name = index.data(NodeItem.NameRole)
      name.append(self.tr(" Properties"))
      properties = index.data(NodeItem.PropertiesRole).split("|")
      propertiesDialog = QtGui.QDialog(self)
      propertiesDialog.setFixedWidth(400)
      propertiesDialog.setWindowTitle(name)
      propertiesDialog.setLayout(QtGui.QGridLayout())
      if not location.isEmpty():
        locationAttribute = QtGui.QLabel(self.tr("Location:"))
        #scrollArea = QtGui.QScrollArea()
        locationValue = ScrollableLabel(location)
        locationValue.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        #scrollArea.setWidget(locationValue)
        #scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        propertiesDialog.layout().addWidget(locationAttribute, 0, 0)
        #propertiesDialog.layout().addWidget(scrollArea, 0, 1)
        propertiesDialog.layout().addWidget(locationValue, 0, 1)
      y = 1
      for _property in properties:
        items = _property.split(":")
        attributeLabel = QtGui.QLabel(items[0] + ":")
        valueLabel = QtGui.QLabel(items[1])
        propertiesDialog.layout().addWidget(attributeLabel, y, 0)
        propertiesDialog.layout().addWidget(valueLabel, y, 1)
        y += 1
      propertiesDialog.layout().setColumnStretch(1, 1)
      position = self.mapToGlobal(self.visualRect(index).center())
      propertiesDialog.move(position)
      propertiesDialog.exec_()


  def __displayFiles(self, checked):
    self.model().setFilesCreation(checked)


  def setCurrentIndexFromUid(self, uid):
    index = self.model().createIndexFromUid(uid)
    if index.isValid():
      self.setCurrentIndex(index)
    

  def setFilesDisplay(self, enable):
    self.model().setFilesCreation(enable)


class NodesIconView(StandardIconView):
  def __init__(self, parent=None):
    super(NodesIconView, self).__init__(1, parent)
    delegate = NodesIconDelegate()
    self.setItemDelegate(delegate)


class NodesListView(StandardListView):
  def __init__(self, parent=None):
    super(NodesListView, self).__init__(1, parent)
    #delegate = NodesIconDelegate()
    #self.setItemDelegate(delegate)

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

import locale

from PyQt4 import QtCore, QtGui

from dff.api.events.libevents import EventHandler
from dff.api.datatype.libdatatype import DataTypeManager
from dff.ui.gui.core.standarditems import HorizontalHeaderItem
from dff.ui.gui.datatypes.datatypesitems import DatatypeItem
from dff.ui.gui.core.standardmodels import StandardTreeModel
from dff.ui.gui.nodes.nodesitems import NodeItem
from dff.ui.gui.nodes.nodesmodels import NodesModel, NodesListModel


class DatatypesNodesModel(NodesModel, EventHandler):  
  def __init__(self, parent=None):
    NodesModel.__init__(self, parent)
    EventHandler.__init__(self)
    self._rootItem = NodeItem(-1, None)
    self.__isRecursive = False
    self.__items = {}
    index = 0
    for column in NodesListModel.DefaultColumns:
      self.addColumn(column, index)
      index += 1


  def setDatatypes(self, datatypes):
    self.beginResetModel()
    self.__items = {}
    self._rootItem = NodeItem(-1, None)
    for datatype in datatypes:
      nodes = DataTypeManager.Get().nodes(datatype)
      for node in nodes:
        childItem = NodeItem(node.uid(), self._rootItem)
        self._rootItem.appendChild(childItem)
        self.__items[node.uid()] = childItem
    self.sort(self.columnCount(), 0)
    self.endResetModel()


  def itemFromUid(self, uid):
    if self.__items.has_key(uid):
      return self.__items[uid]
    return None
  

  def Event(self, event):
      pass


  def flags(self, index):
    if not index.isValid():
      return 0
    column = index.column()
    if column < self.columnCount():
      if column == 0:
        flags = QtCore.Qt.ItemIsEnabled
        flags = flags | QtCore.Qt.ItemIsTristate
        flags = flags | QtCore.Qt.ItemIsUserCheckable
      else:
        flags = QtCore.Qt.ItemIsEnabled
        flags = flags | QtCore.Qt.ItemIsSelectable
      return flags
    return 0


class DatatypesTreeModel(StandardTreeModel, EventHandler):
  DefaultColumns = [HorizontalHeaderItem(0, "name",
                                         HorizontalHeaderItem.StringType)]

  
  def __init__(self, parent=None, displayChildrenCount=True):
    StandardTreeModel.__init__(self, parent, displayChildrenCount)
    EventHandler.__init__(self)
    self.__items = {}
    self.__dataTypes = DataTypeManager.Get()
    self.__dataTypes.connection(self)
    self.connect(self, QtCore.SIGNAL("registerDatatype"), self.insertTree)
    self._rootItem = DatatypeItem("", None)
    index = 0
    for column in DatatypesTreeModel.DefaultColumns:
      self.addColumn(column, index)
      index += 1
    self.__populate()


  def Event(self, event):
    value = event.value
    if value is None:
      return
    datatype = value.value()
    if datatype is None:
      return
    self.emit(QtCore.SIGNAL("registerDatatype"), datatype)


  def insertTree(self, datatype):
    try:
      self.__populate()
    except:
      import traceback
      traceback.print_exc()


  def __datatypesFromItem(self, item):
    if item.childCount() > 0:
      datatypes = []
      children = item.children()
      for child in children:
        datatype = self.__datatypesFromItem(child)
        datatypes.extend(datatype)
      return datatypes
    else:
      return [item.queryType()]


  def datatypesFromIndex(self, index):
    item = index.internalPointer()
    if item is None:
      return []
    if item.childCount() > 0:
      datatypes = []
      children = item.children()
      for child in children:
        datatype = self.__datatypesFromItem(child)
        datatypes.extend(datatype)
      return datatypes
    else:
      return [item.queryType()]
  

  def __populate(self):
    self.beginResetModel()
    self._rootItem = DatatypeItem("", None)
    self.__items = {}
    datatypes = self.__dataTypes.existingTypes()
    for datatype in datatypes:
      # An item can have several matching types. Currently, all types are
      # concatenated and space separated.
      types = datatype.split(" ")
      for _type in types:
        categories = _type.split("/")
        parentItem = self._rootItem
        path = ""
        for category in categories:
          if len(path):
            path = path + "/" + category
          else:
            path = category
          if not self.__items.has_key(path):
            childItem = DatatypeItem(category, parentItem)
            self.__items[path] = childItem
            parentItem.appendChild(childItem)
            parentItem = childItem
          else:
            parentItem = self.__items[path]
        childItem.setQueryType(datatype)
    self.endResetModel()

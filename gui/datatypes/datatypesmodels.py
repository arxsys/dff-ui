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

from qtpy import QtCore, QtWidgets

#from dff.api.events.libevents import EventHandler
#from dff.api.datatype.libdatatype import DataTypeManager
#from dff.api.filters.libfilters import Filter
from core.standarditems import HorizontalHeaderItem
from datatypes.datatypesitems import DatatypeItem
from core.standardmodels import StandardTreeModel
from nodes.nodesitems import NodeItem
from nodes.nodesmodels import NodesModel, NodesListModel

# XXX_XXX Mock Class
class EventHandler(object):
  def __init__(self):
    pass



class DatatypesNodesModel(NodesModel, EventHandler):  
  def __init__(self, parent=None):
    NodesModel.__init__(self, parent)
    EventHandler.__init__(self)
    self.__datatypes = []
    self.__rootItem = NodeItem(-1, None)
    self.__filteredRootItem = NodeItem(-1, None)
    #self.__filter = Filter("DatatypesNodesFilterModel")
    self.__items = {}
    self.__filteredItems = {}
    self.__isRecursive = False
    index = 0
    for column in NodesListModel.DefaultColumns:
      self.addColumn(column, index)
      index += 1


  def disableFilter(self):
    self.beginResetModel()
    self.setRootItem(self.__rootItem)
    self.endResetModel()


  def enableFilter(self, query):
    try:
      self.__filter.compile(query)
      self.__populate()
    except:
      self.disableFilter()


  def setDatatypes(self, datatypes):
    self.__datatypes = datatypes
    self.__populate()


  def __populate(self):
    self.beginResetModel()
    self.__rootItem = NodeItem(-1, None)
    self.__filteredRootItem = NodeItem(-1, None)
    self.__items = {}
    self.__filteredItems = {}
    if self._filtered:
      self.setRootItem(self.__filteredRootItem)
    else:
      self.setRootItem(self.__rootItem)
    for datatype in self.__datatypes:
      nodes = DataTypeManager.Get().nodes(datatype)
      for node in nodes:
        uid = node.uid()
        if self._filtered and self.__filter.match(uid):
          filteredItem = NodeItem(uid, self.__filteredRootItem)
          self.__filteredRootItem.appendChild(filteredItem)
          self.__filteredItems[uid] = filteredItem
        childItem = NodeItem(uid, self.__rootItem)
        self.__rootItem.appendChild(childItem)
        self.__items[uid] = childItem
    self.sort(self.columnCount(), 0)
    self.endResetModel()


  def itemFromUid(self, uid):
    if self._filtered:
      if self.__filteredItems.has_key(uid):
        return self.__filteredItems[uid]
      else:
        return None
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
    #self.__dataTypes = DataTypeManager.Get()
    #self.__dataTypes.connection(self)
    #self.connect(self, QtCore.SIGNAL("registerDatatype"), self.insertTree)
    self.__rootItem = DatatypeItem("", None)
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
    self.__rootItem = DatatypeItem("", None)
    self.setRootItem(self.__rootItem)
    self.__items = {}
    #datatypes = self.__dataTypes.existingTypes()
    datatypes = []
    for datatype in datatypes:
      # An item can have several matching types. Currently, all types are
      # concatenated and space separated.
      types = datatype.split(" ")
      for _type in types:
        categories = _type.split("/")
        parentItem = self.__rootItem
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

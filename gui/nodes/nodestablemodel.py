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

from PyQt4 import QtCore, QtGui

from dff.api.events.libevents import EventHandler
from dff.api.vfs.libvfs import VFS
from dff.api.filters.libfilters import Filter
from dff.api.types.libtypes import typeId

from dff.ui.gui.nodes.nodesitem import NodeItem


class NodesTableHeaderItem():

  AliasRole = QtCore.Qt.UserRole
  AttributeNameRole = QtCore.Qt.UserRole + 1
  DataTypeRole = QtCore.Qt.UserRole + 2
  PinRole = QtCore.Qt.UserRole + 3
  FilterRole = QtCore.Qt.UserRole + 4
  
  NameType = 0
  SizeType = 1
  DataType = 2
  TagType = 3
  TimeType = 4
  NumberType = 5
  StringType = 6

  def __init__(self, index, attributeName, dataType, isPinned=False, alias=""):
    self.__index = index
    self.__attributeName = attributeName
    self.__dataType = dataType
    self.__aliasName = alias
    self.__isPinned = isPinned
    self.__filter = ""


  def rawData(self, role):
    if role == QtCore.Qt.DisplayRole:
      if len(self.__aliasName):
        return self.__aliasName
      else:
        return self.__attributeName
    if role == NodesTableHeaderItem.AliasRole:
      return self.__aliasName
    if role == NodesTableHeaderItem.AttributeNameRole:
      return self.__attributeName
    if role == NodesTableHeaderItem.DataTypeRole:
      return self.__dataType
    if role == NodesTableHeaderItem.PinRole:
      return self.__isPinned
    if role == NodesTableHeaderItem.FilterRole:
      return self.__filter
    return None
    

  def data(self, role=QtCore.Qt.DisplayRole):
    if role == QtCore.Qt.DisplayRole or role == NodesTableHeaderItem.AttributeNameRole:
      name = QtCore.QString.fromUtf8(self.rawData(role))
      return QtCore.QVariant(name)
    if role == QtCore.Qt.SizeHintRole:
      return self.__sizeHintRole()
    if role == NodesTableHeaderItem.DataTypeRole:
      return QtCore.QVariant(self.__dataType)
    if role == NodesTableHeaderItem.PinRole:
      return QtCore.QVariant(self.__isPinned)
    if role == NodesTableHeaderItem.FilterRole:
      return QtCore.QVariant(self.__filter)
    return QtCore.QVariant()


  def setData(self, value, role):
    if role == NodesTableHeaderItem.AliasRole:
      self.__aliasName = value.toString()
      args = (self.__index)
      return (True, "aliasNameChanged()", args)
    if role == NodesTableHeaderItem.PinRole:
      self.__isPinned = value.toBool()
      args = (self.__index, self.__isPinned)
      return (True, "columnPinStateChanged(int, bool)", args)
    if role == NodesTableHeaderItem.FilterRole:
      self.__filter = value.toString()
      args = (self.__index)
      return (True, "filterChanged(int)", args)
    return (False, None, None)


  def __sizeHintRole(self):
    data = self.data(QtCore.Qt.DisplayRole)
    if data.isValid():
      fm = QtGui.QApplication.instance().fontMetrics()
      width = fm.width(data.toString())
      sizeHint = QtCore.QSize(width+100, fm.height()+10)
      return QtCore.QVariant(sizeHint)
    return QtCore.QVariant()


class NodesTableFilterModel(QtGui.QSortFilterProxyModel):
  def __init__(self, model, parent=None):
    QtGui.QSortFilterProxyModel.__init__(self, parent)
    self.setSourceModel(model)
    self.connect(model, QtCore.SIGNAL("filterChanged()"), self.__filterChanged)
    self.__filter = Filter("proxy")                 
    self.__compiled = False
    
    
  def __filterChanged(self):
    self.__compiled = False
    try:
      query = ""
      for column in xrange(0, self.sourceModel().columnCount()):
        _filter = self.sourceModel().headerData(column, QtCore.Qt.Horizontal, NodesTableHeaderItem.FilterRole)
        _filter = _filter.toString()
        if len(_filter):
          if len(query):
            query += " and " + _filter
          else:
            query = _filter
        self.__filter.compile(str(query))
        self.__compiled = True
        self.invalidateFilter()
    except:
      self.emit(QtCore.SIGNAL("badFilter(QString)"))

    
  def sort(self, column, order):
    self.sourceModel().sort(column, order)


  def nodeFromIndex(self, index):
    index = self.sourceModel().index(0, 0, index)
    return self.sourceModel().nodeFromIndex(index)

  
  def filterAcceptsRow(self, sourceRow, sourceParent):
    index = self.sourceModel().index(sourceRow, 0, sourceParent)
    if not index.isValid() or not self.__compiled:
      return False
    node = self.sourceModel().nodeFromIndex(index)
    if node is not None:
      self.__filter.process(node)
      matched = self.__filter.matchedNodes()
      if len(matched):
        return True
    return False
  
    
class NodesTableModel(QtCore.QAbstractItemModel, EventHandler):
  
  def __init__(self, parent=None, displayChildrenCount=False, createFiles=False):
    QtCore.QAbstractItemModel.__init__(self, parent)
    EventHandler.__init__(self)
    self.VFS = VFS.Get()
    self.VFS.connection(self)
    self.__rootUid = -1
    self.__rootItem = NodeItem(-1, None)
    self.__isRecursive = False
    self.__columns = [NodesTableHeaderItem(0, "name", NodesTableHeaderItem.NameType),
                      NodesTableHeaderItem(1, "uid", NodesTableHeaderItem.NumberType),
                      NodesTableHeaderItem(2, "size", NodesTableHeaderItem.SizeType),
                      NodesTableHeaderItem(3, "type", NodesTableHeaderItem.DataType),
                      NodesTableHeaderItem(4, "tags", NodesTableHeaderItem.TagType)]
    self.__items = {}
    self.__sortedColumns = [("name", QtCore.Qt.AscendingOrder)]


  def __del__(self):
    self.VFS.deconnection(self)
    
    
  def setRootNode(self, node, isRecursive=False):
    if node is None:
      return
    self.__rootUid = node.uid()
    self.__isRecursive = isRecursive
    self.__populate()


  def setRootUid(self, uid, isRecursive=False):
    node = VFS.Get().getNodeById(uid)
    if node is None:
      return
    self.__rootUid = uid
    self.__isRecursive = isRecursive
    self.__populate()
   

  def Event(self, event):
    value = event.value
    if value is None:
      return
    node = value.value()
    if node is None:
      return
    puid = node.parent().uid()
    if self.__isRecursive:
      # if recursive is enabled and node is under the current root recursion
      # the model is reset.
      if puid == self.__rootUid or self.__items.has_key(puid):
        self.__populate()
      return
    elif puid == self.__rootUid:
      nuid = node.uid()
      # if node already exists, just emit dataChanged. It means that node now
      # has children.
      if self.__items.has_key(nuid):
        item = self.__items[nuid]
        topLeft = self.createIndex(item.row(), 0, item)
        bottomRight = self.createIndex(item.row(), 1, item)
        self.dataChanged.emit(topLeft, bottomRight)
      # particular case, node corresponds to a new tree registered to parent.
      else:
        self.__populate()
    return

      
  def setData(self, index, value, role):
    if not index.isValid():
      return False
    item = index.internalPointer()
    if index.column() < len(self.__columns) and item is not None:
      column = self.__columns[index.column()]
      attribute = column.rawData(NodesTableHeaderItem.AttributeNameRole)
      success, signal = item.setData(attribute, value, role)
      if success:
        topLeft = self.createIndex(index.row(), 0, item)
        bottomRight = self.createIndex(index.row(), index.column(), item)
        self.dataChanged.emit(topLeft, bottomRight)
        if signal is not None:
          self.emit(QtCore.SIGNAL(signal))
      return success
    return False      
      
      
  def data(self, index, role):
    if not index.isValid():
      return QtCore.QVariant()
    item = index.internalPointer()
    if item is not None:
      if index.column() < len(self.__columns):
        column = self.__columns[index.column()]
        attribute = column.rawData(NodesTableHeaderItem.AttributeNameRole)
        itemData = item.data(role, attribute)
        return itemData
    return QtCore.QVariant()

  
  def flags(self, index):
    if not index.isValid():
      return 0
    return QtCore.Qt.ItemIsEnabled


  def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
    if section > len(self.__columns) - 1:
      return QtCore.QVariant()
    if orientation == QtCore.Qt.Horizontal:
      column = self.__columns[section]
      return column.data(role)
    return QtCore.QVariant()


  def setHeaderData(self, section, orientation, value, role=QtCore.Qt.EditRole):
    if section > len(self.__columns) - 1:
      return False
    if orientation == QtCore.Qt.Horizontal:
      column = self.__columns[section]
      success, signal, args  = column.setData(value, role)
      self.headerDataChanged.emit(orientation, section, section)
      if signal is not None:
        print signal, args
        if args is not None and len(args) > 0:
          self.emit(QtCore.SIGNAL(signal), *args)
        else:
          self.emit(QtCore.SIGNAL(signal))
      return success
    return False


  def nodeFromIndex(self, index):
    if not index.isValid():
      return None
    item = index.internalPointer()
    if item is None:
      return None
    uid = item.rawData("uid")
    if uid != -1:
      return VFS.Get().getNodeById(uid)
    return None


  def parent(self, index):
    if not index.isValid():
      return QtCore.QModelIndex()
    childItem = index.internalPointer()
    if childItem is None:
      return QtCore.QModelIndex()
    parentItem = childItem.parent()
    if parentItem is None:
      return QtCore.QModelIndex()
    if parentItem == self.__rootItem:
      return QtCore.QModelIndex()
    return self.createIndex(parentItem.row(), 0, parentItem)


  def rowCount(self, parent=QtCore.QModelIndex()):
    if not parent.isValid():
      parentItem = self.__rootItem
    else:
      parentItem = parent.internalPointer()
    return parentItem.childCount()


  def columnCount(self, parent=QtCore.QModelIndex()):
    return len(self.__columns)

  
  def index(self, row, column, parent=QtCore.QModelIndex()):
    if row < 0 or column < 0 or row > len(self.__items) - 1 or column > len(self.__columns) - 1:
      return QtCore.QModelIndex()
    return self.createIndex(row, column, self.__rootItem.child(row))


  # descending order == reverse on
  # python stable sort average performance is O(n log n)
  def sort(self, column, order):
    if column > len(self.__columns):
      return
    self.beginResetModel()
    column = self.__columns[column]
    attribute = column.rawData(NodesTableHeaderItem.AttributeNameRole)
    self.__sortedColumns = [(attribute, order)]
    self.__sort()
    self.endResetModel()


  def __sort(self):
    for attribute, order in self.__sortedColumns:
      self.__rootItem.sort(attribute, bool(order))


  def __recursivePopulate(self, node):
    children = node.children()
    for child in children:
      uid = child.uid()
      childItem = NodeItem(uid, self.__rootItem)
      self.__rootItem.appendChild(childItem)
      self.__items[uid] = childItem
      if child.hasChildren():
        self.__recursivePopulate(child)
        

  def __populate(self):
    rootNode = VFS.Get().getNodeById(self.__rootUid)
    if rootNode is None:
      return
    self.beginResetModel()
    self.__items = {}
    self.__rootItem = NodeItem(-1, None)
    children = rootNode.children()
    for child in children:
      uid = child.uid()
      childItem = NodeItem(uid, self.__rootItem)
      self.__rootItem.appendChild(childItem)
      self.__items[uid] = childItem
      if self.__isRecursive and child.hasChildren():
        self.__recursivePopulate(child)
    # use private sort which does not call beginResetModel()
    self.__sort()
    self.endResetModel()

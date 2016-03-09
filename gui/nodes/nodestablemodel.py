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
import functools

from PyQt4 import QtCore, QtGui

from dff.api.events.libevents import EventHandler
from dff.api.vfs.libvfs import VFS
from dff.ui.gui.nodes.nodesitem import NodeItem


class NodesTableModel(QtCore.QAbstractItemModel, EventHandler):
  def __init__(self, parent=None, displayChildrenCount=False, createFiles=False):
    QtCore.QAbstractItemModel.__init__(self, parent)
    EventHandler.__init__(self)
    self.VFS = VFS.Get()
    self.VFS.connection(self)
    self.__rootUid = -1
    self.__rootItem = NodeItem(-1, None)
    self.__isRecursive = False
    self.__columns = ["name", "uid", "size", "type"]
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
      print "sdfll;sdkflksdlfkl;sdkfl;ksdl;fkksdf"
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
    print "setData:", role
    return QtGui.QAbstractModel.setData(index, role)
      
      
  def data(self, index, role):
    if not index.isValid():
      return QtCore.QVariant()
    item = index.internalPointer()
    if item is not None:
      if index.column() < len(self.__columns):
        attribute = self.__columns[index.column()]
        return item.data(role, attribute)
    return QtCore.QVariant()

  
  def flags(self, index):
    if not index.isValid():
      return 0
    return QtCore.Qt.ItemIsEnabled


  def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
    if section > len(self.__columns) - 1:
      return QtCore.QVariant()
    if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
      return QtCore.QString.fromUtf8(self.__columns[section])
    return QtCore.QVariant()


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


  def rowCount(self, parent):
    if not parent.isValid():
      parentItem = self.__rootItem
    else:
      parentItem = parent.internalPointer()
    return parentItem.childCount()


  def index(self, row, column, parent):
    if row < 0 or column < 0 or row > len(self.__items) - 1 or column > len(self.__columns) - 1:
      return QtCore.QModelIndex()
    return self.createIndex(row, column, self.__rootItem.child(row))

  
  def rowCount(self, parent):
    return len(self.__items)
  

  def columnCount(self, parent):
    return len(self.__columns)


  # descending order == reverse on
  # python stable sort average performance is O(n log n)
  def sort(self, column, order):
    if column > len(self.__columns):
      return
    self.beginResetModel()
    attribute = self.__columns[column]
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

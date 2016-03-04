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
from dff.ui.gui.nodes.nodestreemodel import NodeItem

class NodesTableModel(QtCore.QAbstractItemModel, EventHandler):
  def __init__(self, parent=None, displayChildrenCount=False, createFiles=False):
    QtCore.QAbstractItemModel.__init__(self, parent)
    EventHandler.__init__(self)
    self.VFS = VFS.Get()
    self.VFS.connection(self)
    self.__rootUid = -1
    self.__columns = ["name", "uid", "size", "type"]
    self.__items = []


  def __del__(self):
    self.VFS.deconnection(self)

    
  def setRootNode(self, node):
    if node is None:
      return
    self.__rootUid = node.uid()
    self.__populate()


  def setRootUid(self, uid):
    node = VFS.Get().getNodeById(uid)
    if node is None:
      return
    self.__rootUid = uid
    self.__populate()
   

  def Event(self, event):
    value = event.value
    if value is None:
      return
    node = value.value()
    if node is None:
      return
    self.emit(QtCore.SIGNAL("insertTree"), node.uid())

      
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
    return QtCore.QModelIndex()


  def index(self, row, column, parent):
    if row > len(self.__items) - 1:
      return QtCore.QModelIndex()
    return self.createIndex(row, column, self.__items[row])

  
  def rowCount(self, parent):
    print len(self.__items)
    return len(self.__items)
  

  def columnCount(self, parent):
    return len(self.__columns)
    

  def __populate(self):
    rootNode = VFS.Get().getNodeById(self.__rootUid)
    if rootNode is None:
      return
    self.__items = []
    children = rootNode.children()
    self.beginInsertRows(QtCore.QModelIndex(), 0, len(children))
    for child in children:
      childItem = NodeItem(child.uid())
      self.__items.append(childItem)
    self.endInsertRows()

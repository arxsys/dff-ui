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
from dff.api.vfs.libvfs import VFS
from dff.ui.gui.nodes.nodesitem import NodeItem


class NodesTreeModel(QtCore.QAbstractItemModel, EventHandler):
  def __init__(self, parent=None, displayChildrenCount=False, createFiles=False):
    QtCore.QAbstractItemModel.__init__(self, parent)
    EventHandler.__init__(self)
    self.VFS = VFS.Get()
    self.VFS.connection(self)
    self.connect(self, QtCore.SIGNAL("registerTree"), self.insertTree)
    self.__rootUid = -1
    self.__rootItem = NodeItem(-1, None)
    self.__items = {}
    self.__columns = ["name", "uid", "size", "type", "row"]
    self.__displayChildrenCount = displayChildrenCount
    self.__createFiles = createFiles
    

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
   

  def setFilesCreation(self, create):
    self.__createFiles = create
    self.__populate()
    
    
  def setDisplayChildrenCount(self, count):
    self.__displayChildrenCount = count
    topLeft = self.createIndex(self.__rootItem.row(), 0, self.__rootItem)
    bottomRight = self.createIndex(self.__rootItem.row(), 1, self.__rootItem)
    self.dataChanged.emit(topLeft, bottomRight)


  def Event(self, event):
    value = event.value
    if value is None:
      return
    node = value.value()
    if node is None:
      return
    self.emit(QtCore.SIGNAL("registerTree"), node.uid())


  def insertTree(self, uid):
    node = VFS.Get().getNodeById(uid)
    if node is None:
      return
    parent = node.parent()
    # Should not happen but have to find a way
    # to trigger this case
    if parent is None:
      return
    puid = parent.uid()
    if not self.__items.has_key(puid):
      # Special case in DFF when. Parent was previously a file and becomes a
      # virtual Folder (module applied on it).
      # While populating tree, parent had neither children nor was a isDir, so
      # NodeItem was not created for it. We need, to create NodeItem for
      # this parent and add it to its ancestor.
      # Ancestor must exist otherwise something has been done completly
      # wrong somewhere. Meaning that parent was not a folder so what was it ?!
      ancestor = parent.parent()
      ancestorItem = self.__items[ancestor.uid()]
      index = self.createIndex(ancestorItem.row(), 0, ancestorItem)
      insertIdx = self.__findIndexToInsert(ancestorItem, parent.name(), 0, ancestorItem.childCount()-1)
      self.beginInsertRows(index, insertIdx, 1)
      parentItem = NodeItem(parent.uid(), ancestorItem)
      self.__items[parent.uid()] = parentItem
      ancestorItem.insertChild(insertIdx, parentItem)
      nodeItem = NodeItem(node.uid(), parentItem)
      self.__items[node.uid()] = nodeItem
      parentItem.appendChild(nodeItem)
      self.__createTreeItems(node, nodeItem)
      self.endInsertRows()
      changedItem = ancestorItem
    else:
      # Just add our new tree to the parent.
      parentItem = self.__items[puid]
      index = self.createIndex(parentItem.row(), 0, parentItem)
      insertIdx = self.__findIndexToInsert(parentItem, node.name(), 0, parentItem.childCount()-1)
      self.beginInsertRows(index, insertIdx, 1)
      childItem = NodeItem(node.uid(), parentItem)
      self.__items[node.uid()] = childItem
      parentItem.insertChild(insertIdx, childItem)
      self.__createTreeItems(node, childItem)
      self.endInsertRows()
      changedItem = parentItem
    topLeft = self.createIndex(changedItem.row(), 0, changedItem)
    bottomRight = self.createIndex(changedItem.row(), 1, changedItem)
    self.dataChanged.emit(topLeft, bottomRight)
    
      
  def setData(self, index, value, role):
    if not index.isValid():
      return QtCore.QVariant()
    item = index.internalPointer()
    if index.column() < len(self.__columns) and item is not None:
      attribute = self.__columns[index.column()]
      success, signal = item.setData(attribute, value, role)
      if signal is not None:
        self.emit(QtCore.SIGNAL(signal))
      return success
    return QtGui.QAbstractModel.setData(index, value, role)
      
      
  def data(self, index, role):
    if not index.isValid():
      return QtCore.QVariant()
    item = index.internalPointer()
    if index.column() < len(self.__columns) and item is not None:
      attribute = self.__columns[index.column()]
      return item.data(role, attribute, self.__displayChildrenCount)
    return QtCore.QVariant()

    
  def flags(self, index):
    if not index.isValid():
      return 0
    # QtCore.Qt.ItemIsUserCheckable is disabled and is managed by delegate
    return QtCore.Qt.ItemIsEnabled


  def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
    #print section
    if section > len(self.__columns) - 1:
      return QtCore.QVariant()
    if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
      return QtCore.QString.fromUtf8(self.__columns[section])
    return QtCore.QVariant()


  def index(self, row, column, parent):
    if not self.hasIndex(row, column, parent):
      return QtCore.QModelIndex()
    if parent is None:
      return QtCore.QModelIndex()
    if not parent.isValid():
      parentItem = self.__rootItem
    else:
      parentItem = parent.internalPointer()
    childItem = parentItem.child(row)
    if childItem is not None:
      return self.createIndex(row, column, childItem)
    else:
      return QtCore.QModelIndex()


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
  

  def columnCount(self, parent):
    return len(self.__columns)


  def __createTreeItems(self, node, parent):
    if node is None or parent is None:
      return
    children = node.children()
    for child in children:
      if child.hasChildren() or child.isDir():
        childItem = NodeItem(child.uid(), parent)
        self.__items[child.uid()] = childItem
        self.__createTreeItems(child, childItem)
        parent.appendChild(childItem)
      elif self.__createFiles:
        childItem = NodeItem(child.uid(), parent)
        self.__items[child.uid()] = childItem
        parent.appendChild(childItem)        
    parent.sort("name", False)


  def __populate(self):
    rootNode = VFS.Get().getNodeById(self.__rootUid)
    if rootNode is None:
      return
    self.beginResetModel()
    self.__items = {}
    self.__rootItem = NodeItem(-1, None)
    childItem = NodeItem(self.__rootUid, self.__rootItem)
    self.__items[self.__rootUid] = childItem
    self.__rootItem.appendChild(childItem)
    self.__createTreeItems(rootNode, childItem)
    self.endResetModel()
    self.emit(QtCore.SIGNAL("insertedFoldersCount(int)"), len(self.__items))


  # TreeModel only sorts based on nodes' name
  def __findIndexToInsert(self, item, key, imin, imax):
    if item is None or item.childCount() == 0:
      return 0
    if imax < imin:
      return imin
    imid = (imin + imax) / 2
    node = VFS.Get().getNodeById(item.child(imid).uid())
    #XXX check behaviour of strcoll on unicode
    position = locale.strcoll(key, node.name())
    if imax == imin:
      if position <= 0:
        return imax
      else:
        return imax+1
    # key is before node.name()
    if position < 0:
      return self.__findIndexToInsert(item, key, imin, imid-1)
    # key is after node.name()
    elif position > 0:
      return self.__findIndexToInsert(item, key, imid+1, imax)
    else:
      return imid

      
                              

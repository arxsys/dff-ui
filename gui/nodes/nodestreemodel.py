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
from dff.ui.gui.nodes.nodesitem import NodeItem

class NodeTreeItem(NodeItem):
  def __init__(self, uid, parent):
    NodeItem.__init__(self, uid)
    self.__children = []
    self.__parent = parent


  def parent(self):
    return self.__parent


  def appendChild(self, child):
    self.__children.append(child)


  def child(self, row):
    if row < len(self.__children):
      return self.__children[row]
    else:
      return None

    
  def childCount(self):
    return len(self.__children)


  def row(self):
    if self.__parent is not None:
      return self.__parent.indexOf(self)
    return 0
  

  def indexOf(self, item):
    return self.__children.index(item)


class NodesTreeModel(QtCore.QAbstractItemModel, EventHandler):
  def __init__(self, parent=None, displayChildrenCount=False, createFiles=False):
    QtCore.QAbstractItemModel.__init__(self, parent)
    EventHandler.__init__(self)
    self.VFS = VFS.Get()
    self.connect(self, QtCore.SIGNAL("insertTree"), self.insertTree)
    self.VFS.connection(self)
    self.__rootUid = -1
    self.__rootItem = NodeTreeItem(-1, None)
    self.__items = {}
    self.__columns = ["name", "uid", "size", "type"]
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
    self.emit(QtCore.SIGNAL("insertTree"), node.uid())


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
      # NodeTreeItem was not created for it. We need, to create NodeTreeItem for
      # this parent and add it to its ancestor.
      # Ancestor must exist otherwise something has been done completly
      # wrong somewhere. Meaning that parent was not a folder so what was it ?!
      ancestor = parent.parent()
      ancestorItem = self.__items[ancestor.uid()]
      parentItem = NodeTreeItem(parent.uid(), ancestorItem)
      ancestorItem.appendChild(parentItem)
      nodeItem = NodeTreeItem(node.uid(), parentItem)
      parentItem.appendChild(nodeItem)
      self.__createTreeItems(node, nodeItem)
      index = self.createIndex(ancestorItem.row(), 0, ancestorItem)
      self.beginInsertRows(index, ancestorItem.childCount(), 1)
      self.endInsertRows()
    else:
      # Just add our new tree to the parent.
      parentItem = self.__items[puid]
      childItem = NodeTreeItem(node.uid(), parentItem)
      self.__items[node.uid()] = childItem
      parentItem.appendChild(childItem)
      index = self.createIndex(parentItem.row(), 0, parentItem)
      self.beginInsertRows(index, parentItem.childCount(), 1)
      self.__createTreeItems(node, childItem)
      self.endInsertRows()
    topLeft = self.createIndex(self.__rootItem.row(), 0, self.__rootItem)
    bottomRight = self.createIndex(self.__rootItem.row(), 1, self.__rootItem)
    self.dataChanged.emit(topLeft, bottomRight)

      
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
        return item.data(role, attribute, self.__displayChildrenCount)
    return QtCore.QVariant()
  
  
  def flags(self, index):
    if not index.isValid():
      return 0
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
        childItem = NodeTreeItem(child.uid(), parent)
        self.__items[child.uid()] = childItem
        self.__createTreeItems(child, childItem)
        parent.appendChild(childItem)
      elif self.__createFiles:
        childItem = NodeTreeItem(child.uid(), parent)
        self.__items[child.uid()] = childItem
        parent.appendChild(childItem)        
    

  def __populate(self):
    self.__items = {}
    rootNode = VFS.Get().getNodeById(self.__rootUid)
    if rootNode is None:
      return
    self.__items = {}
    self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
    self.__rootItem = NodeTreeItem(-1, None)
    childItem = NodeTreeItem(self.__rootUid, self.__rootItem)
    self.__items[self.__rootUid] = childItem
    self.__rootItem.appendChild(childItem)
    self.__createTreeItems(rootNode, childItem)
    self.endInsertRows()
    self.emit(QtCore.SIGNAL("insertedFoldersCount(int)"), len(self.__items))

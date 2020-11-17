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

from qtpy import QtCore, QtGui, QtWidgets

#from dff.api.events.libevents import EventHandler
#from dff.api.vfs.libvfs import VFS
#from dff.api.filters.libfilters import Filter

from nodes.nodesitems import NodeItem, NodeTreeItem
from core.standardmodels import StandardModel, StandardTreeModel
from core.standarditems import HorizontalHeaderItem

# XXX move it nodes?
#from dff.ui.gui.api.thumbnail import ThumbnailManager


# XXX_XXX Mock Class
class EventHandler(object):
  def __init__(self):
    pass

class NodesModel(StandardModel):
  def __init__(self, parent=None):
    super(NodesModel, self).__init__(parent)
    #thumbnailer = ThumbnailManager().getInstance()
    self.__waitingMessage = self.tr("Rendering list...")
    self.__statusBar = QtWidgets.QApplication.instance().mainWindow().statusBar()
    #self.connect(thumbnailer, QtCore.SIGNAL("ThumbnailUpdate"), self.__thumbnailUpdate)


  def itemFromUid(self, uid):
    raise NotImplementedError


  def __thumbnailUpdate(self, node, pixmap):
    if node != None:
      uid = node.uid()
      item = self.itemFromUid(uid)
      if item is not None:
        topLeft = self.createIndex(item.row(), 0, item)
        bottomRight = self.createIndex(item.row(), 1, item)
        self.dataChanged.emit(topLeft, bottomRight)
  
    
class NodesListModel(NodesModel, EventHandler):
  DefaultColumns = [HorizontalHeaderItem(0, "checked",
                                         HorizontalHeaderItem.CheckedType,
                                         HorizontalHeaderItem.ForcePinned,
                                         resizable=False),
                    HorizontalHeaderItem(1, "name",
                                         HorizontalHeaderItem.StringType),
                    HorizontalHeaderItem(2, "uid",
                                         HorizontalHeaderItem.NumberType),
                    HorizontalHeaderItem(3, "size",
                                         HorizontalHeaderItem.SizeType),
                    HorizontalHeaderItem(4, "type",
                                         HorizontalHeaderItem.DataType),
                    HorizontalHeaderItem(5, "tags",
                                         HorizontalHeaderItem.TagType)]

  def __init__(self, parent=None):
    NodesModel.__init__(self, parent)
    EventHandler.__init__(self)
    #self.VFS = VFS.Get()
    #self.VFS.connection(self)
    self.__rootUid = -1
    self.__rootItem = NodeItem(-1, None)
    self.__filteredRootItem = NodeItem(-1, None)
    self.__isRecursive = False
    #self.__filter = Filter("NodesFilterModel")
    self.__items = {}
    self.__filteredItems = {}
    #self.connect(self, QtCore.SIGNAL("updateModel(long, long)"), self.__updateModel)
    index = 0
    for column in NodesListModel.DefaultColumns:
      self.addColumn(column, index)
      index += 1


  def __del__(self):
    pass
    #self.VFS.deconnection(self)


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


  def itemFromUid(self, uid):
    if self._filtered:
      if self.__filteredItems.has_key(uid):
        return self.__filteredItems[uid]
      return None
    if self.__items.has_key(uid):
      return self.__items[uid]
    return None


  def Event(self, event):
    if event is None:
      return
    if event.value is None:
      return
    node = event.value.value()
    if node is None:
      return
    uid = node.uid()
    puid = node.parent().uid()
    self.emit(QtCore.SIGNAL("updateModel(long, long)"), uid, puid)


  def setRootNode(self, node, isRecursive=False):
    if node is None:
      return
    self.__rootUid = node.uid()
    self.__isRecursive = isRecursive
    self.__populate()


  def setRootUid(self, uid, isRecursive=False):
    #node = VFS.Get().getNodeById(uid)
    node = None
    if node is None:
      return
    self.__rootUid = uid
    self.__isRecursive = isRecursive
    self.__populate()


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


  def __updateModel(self, uid, puid):
    if self.__isRecursive:
      # if recursive is enabled and node is under the current root recursion
      # the model is reset.
      if puid == self.__rootUid or puid in self.__items:
        self.__populate()
      return
    elif puid == self.__rootUid:
      # if node already exists, just emit dataChanged. It means that node now
      # has children.
      if uid in self.__items:
        item = self.__items[uid]
        topLeft = self.createIndex(item.row(), 0, item)
        bottomRight = self.createIndex(item.row(), 1, item)
        self.dataChanged.emit(topLeft, bottomRight)
      # particular case, node corresponds to a new tree registered to parent.
      else:
        self.__populate()
    return
        
  
  def __recursivePopulate(self, node, totalChildren):
    children = node.children()
    for child in children:
      uid = child.uid()
      if self._filtered and self.__filter.match(child):
        filteredItem = NodeItem(uid, self.__filteredRootItem)
        self.__filteredRootItem.appendChild(filteredItem)
        self.__filteredItems[uid] = filteredItem
      childItem = NodeItem(uid, self.__rootItem)
      self.__rootItem.appendChild(childItem)
      self.__items[uid] = childItem
      if len(self.__items) % 5000 == 0:
        self._displayStatusProgression(len(self.__items), totalChildren)
      if child.hasChildren():
        self.__recursivePopulate(child, totalChildren)


  def __populate(self):
    rootNode = VFS.Get().getNodeById(self.__rootUid)
    if rootNode is None:
      return
    self.beginResetModel()
    self.__items = {}
    self.__filteredItems = {}
    self.__rootItem = NodeItem(-1, None)
    self.__filteredRootItem = NodeItem(-1, None)
    if self._filtered:
      self.setRootItem(self.__filteredRootItem)
    else:
      self.setRootItem(self.__rootItem)
    children = rootNode.children()
    totalChildren = rootNode.totalChildrenCount()
    self._displayStatusProgression(0, totalChildren)
    for child in children:
      uid = child.uid()
      if self._filtered and self.__filter.match(child):
        filteredItem = NodeItem(uid, self.__filteredRootItem)
        self.__filteredRootItem.appendChild(filteredItem)
        self.__filteredItems[uid] = filteredItem
      childItem = NodeItem(uid, self.__rootItem)
      self.__rootItem.appendChild(childItem)
      self.__items[uid] = childItem
      if len(self.__items) % 5000 == 0:
        self._displayStatusProgression(len(self.__items), totalChildren)
      if self.__isRecursive and child.hasChildren():
        self.__recursivePopulate(child, totalChildren)
    self.sort(self.columnCount(), 0)
    self._clearStatusMessage()
    self.endResetModel()


class NodesTreeModel(StandardTreeModel, EventHandler):
  DefaultColumns = [HorizontalHeaderItem(0, "name",
                                         HorizontalHeaderItem.StringType)]
                    #HorizontalHeaderItem(1, "uid",
                    #                     HorizontalHeaderItem.NumberType),
                    #HorizontalHeaderItem(2, "size",
                    #                     HorizontalHeaderItem.SizeType),
                    #HorizontalHeaderItem(3, "type",
                    #                     HorizontalHeaderItem.DataType),
                    #HorizontalHeaderItem(4, "tags",
                    #                     HorizontalHeaderItem.TagType)]


  def __init__(self, parent=None, displayChildrenCount=False, createFiles=False):
    StandardTreeModel.__init__(self, parent, displayChildrenCount)
    EventHandler.__init__(self)
    #self.VFS = VFS.Get()
    #self.VFS.connection(self)
    #self.__thumbnailer
    #self.connect(self, QtCore.SIGNAL("registerTree(long)"), self.insertTree)
    self.__rootItem = NodeTreeItem(-1, None)
    self.__items = {}
    self.__rootUid = -1
    self.__createFiles = createFiles
    index = 0
    for column in NodesTreeModel.DefaultColumns:
      self.addColumn(column, index)
      index += 1

    

  def __del__(self):
    pass
    #self.VFS.deconnection(self)

    
  def flags(self, index):
    if not index.isValid():
      return 0
    column = index.column()
    flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
    return flags


  def setRootNode(self, node):
    if node is None:
      return
    self.__rootUid = node.uid()
    self.__populate()


  def setRootUid(self, uid):
    #node = VFS.Get().getNodeById(uid)
    node = None
    if node is None:
      return
    self.__rootUid = uid
    self.__populate()
   

  def setFilesCreation(self, create):
    self.__createFiles = create
    self.__populate()
    
    
  def Event(self, event):
    value = event.value
    if value is None:
      return
    node = value.value()
    if node is None:
      return
    self.emit(QtCore.SIGNAL("registerTree(long)"), node.uid())


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
    if node.size() > 0 and not self.__createFiles:
      return
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
      parentItem = NodeTreeItem(parent.uid(), ancestorItem)
      self.__items[parent.uid()] = parentItem
      ancestorItem.insertChild(insertIdx, parentItem)
      nodeItem = NodeTreeItem(node.uid(), parentItem)
      self.__items[node.uid()] = nodeItem
      parentItem.appendChild(nodeItem)
      self._displayStatusMessage(self.tr("Rendering tree..."))
      self.__createTreeItems(node, nodeItem)
      self._clearStatusMessage()
      self.endInsertRows()
      changedItem = ancestorItem
    else:
      # Just add our new tree to the parent.
      parentItem = self.__items[puid]
      index = self.createIndex(parentItem.row(), 0, parentItem)
      insertIdx = self.__findIndexToInsert(parentItem, node.name(), 0, parentItem.childCount()-1)
      self.beginInsertRows(index, insertIdx, 1)
      childItem = NodeTreeItem(node.uid(), parentItem)
      self.__items[node.uid()] = childItem
      parentItem.insertChild(insertIdx, childItem)
      self._displayStatusMessage(self.tr("Rendering tree..."))
      self.__createTreeItems(node, childItem)
      self._clearStatusMessage()
      self.endInsertRows()
      changedItem = parentItem
    topLeft = self.createIndex(changedItem.row(), 0, changedItem)
    bottomRight = self.createIndex(changedItem.row(), 1, changedItem)
    self.dataChanged.emit(topLeft, bottomRight)


  def createIndexFromUid(self, uid):
    if not self.__items.has_key(uid):
      return QtCore.QModelIndex()
    item = self.__items[uid]
    return self.createIndex(item.row(), 0, item)


  def __createTreeItems(self, node, parent):
    children = node.children()
    for child in children:
      if child.hasChildren() or child.isDir():
        childItem = NodeTreeItem(child.uid(), parent)
        self.__items[child.uid()] = childItem
        if len(self.__items) % 5000 == 0:
          self._displayStatusMessage(self.tr("Rendering tree..."))
        self.__createTreeItems(child, childItem)
        parent.appendChild(childItem)
      elif self.__createFiles:
        childItem = NodeTreeItem(child.uid(), parent)
        self.__items[child.uid()] = childItem
        if len(self.__items) % 5000 == 0:
          self._displayStatusMessage(self.tr("Rendering tree..."))
        parent.appendChild(childItem)
    parent.sort("name", HorizontalHeaderItem.StringType, False)


  def __populate(self):
    rootNode = VFS.Get().getNodeById(self.__rootUid)
    if rootNode is None:
      return
    self.beginResetModel()
    self.__items = {}
    self.__rootItem = NodeTreeItem(-1, None)
    self.setRootItem(self.__rootItem)
    if rootNode.size() == 0 or (rootNode.size() > 0 and not self.__createFiles):
      childItem = NodeTreeItem(self.__rootUid, self.__rootItem)
      self.__items[self.__rootUid] = childItem
      self.__rootItem.appendChild(childItem)
      self._displayStatusMessage(self.tr("Rendering tree..."))
      self.__createTreeItems(rootNode, childItem)
      self._clearStatusMessage()
    self.endResetModel()


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

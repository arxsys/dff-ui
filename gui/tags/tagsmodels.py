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
from dff.api.vfs.libvfs import TagsManager
from dff.api.filters.libfilters import Filter
from dff.ui.gui.core.standarditems import StandardItem, HorizontalHeaderItem
from dff.ui.gui.tags.tagsitems import TagItem
from dff.ui.gui.core.standardmodels import StandardTreeModel
from dff.ui.gui.nodes.nodesitems import NodeItem
from dff.ui.gui.nodes.nodesmodels import NodesModel, NodesListModel


class TagsNodesModel(NodesModel, EventHandler):
  def __init__(self, parent=None):
    NodesModel.__init__(self, parent)
    EventHandler.__init__(self)
    self.__tag = ""
    self.__rootItem = NodeItem(-1, None)
    self.__filteredRootItem = NodeItem(-1, None)
    self.__filter = Filter("TagsNodesFilterModel")
    self.__items = {}
    self.__filteredItems = {}
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


  def setTag(self, tag):
    self.__tag = tag
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
    nodesUid = TagsManager.get().nodes(self.__tag)
    for uid in nodesUid:
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


class TagsTreeModel(StandardTreeModel, EventHandler):
  DefaultColumns = [HorizontalHeaderItem(0, "name",
                                         HorizontalHeaderItem.StringType)]

  
  def __init__(self, parent=None, displayChildrenCount=True):
    StandardTreeModel.__init__(self, parent, displayChildrenCount)
    EventHandler.__init__(self)
    self.__items = {}
    TagsManager.get().connection(self)
    self.connect(self, QtCore.SIGNAL("tagEvent(void)"), self.__tagEvent)
    self.__rootItem = StandardItem(None)
    index = 0
    for column in TagsTreeModel.DefaultColumns:
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
    self.emit(QtCore.SIGNAL("tagEvent(void)"))


  def __tagEvent(self):
    try:
      self.__populate()
    except:
      import traceback
      traceback.print_exc()


  def tagIdFromIndex(self, index):
    item = index.internalPointer()
    if item is None:
      return -1
    return item.tagId()


  def __populate(self):
    self.beginResetModel()
    self.__rootItem = StandardItem(None)
    self.setRootItem(self.__rootItem)
    self.__items = {}
    tags = TagsManager.get().tags()
    for tag in tags:
      tagId = tag.id()
      tagItem = TagItem(tagId, self.__rootItem)
      self.__items[tagId] = tagItem
      self.__rootItem.appendChild(tagItem)
    self.endResetModel()

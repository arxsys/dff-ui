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

from qtpy import QtCore, QtGui

#from dff.api.events.libevents import EventHandler
#from dff.api.taskmanager.processus import ProcessusManager 
from core.standarditems import StandardItem, HorizontalHeaderItem
from processus.processusitems import ProcessusItem, ProcessusCategory
from core.standardmodels import StandardTreeModel
from nodes.nodesitems import NodeItem
from nodes.nodesmodels import NodesModel, NodesListModel

# XXX_XXX Mock Class
class EventHandler(object):
  def __init__(self):
    pass

class ProcessusTreeModel(StandardTreeModel, EventHandler):
  DefaultColumns = [HorizontalHeaderItem(0, "name",
                                         HorizontalHeaderItem.StringType),
                    HorizontalHeaderItem(1, "pid",
                                         HorizontalHeaderItem.NumberType),
                    HorizontalHeaderItem(2, "status",
                                         HorizontalHeaderItem.StringType),
                    HorizontalHeaderItem(3, "duration",
                                         HorizontalHeaderItem.StringType)]


  def __init__(self, parent=None, displayChildrenCount=True):
    StandardTreeModel.__init__(self, parent, displayChildrenCount)
    EventHandler.__init__(self)
    self.__items = {}
    #ProcessusManager()
    #self.connect(self, QtCore.SIGNAL("moduleEvent(void)"), self.__moduleEvent)
    self.__rootItem = StandardItem(None)
    index = 0
    for column in ProcessusTreeModel.DefaultColumns:
      self.addColumn(column, index)
      index += 1
    self.__populate()

    
  def refresh(self):
    processusManager = ProcessusManager()
    for processus in processusManager:
      name = processus.name
      if not self.__items.has_key(name):
        row = self.__rootItem.childCount()
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        categoryItem = ProcessusCategory(name, self.__rootItem)
        self.__rootItem.appendChild(categoryItem)
        self.__items[name] = categoryItem
        self.endInsertRows()
        changedItem = self.__rootItem
      else:
        categoryItem = self.__items[name]
      pid = processus.pid
      if self.__items.has_key(pid):
        processusItem = self.__items[pid]
        left = self.createIndex(processusItem.row(), 0, processusItem)
        right = self.createIndex(processusItem.row(), self.columnCount(),
                                 processusItem)
        self.dataChanged.emit(left, right)
      else:
        index = self.createIndex(categoryItem.row(), 0, categoryItem)
        row = categoryItem.childCount()
        self.beginInsertRows(index, row, row)
        processusItem = ProcessusItem(pid, categoryItem)
        self.__items[pid] = processusItem
        categoryItem.appendChild(processusItem)
        self.endInsertRows()

    
  def Event(self, event):
    value = event.value
    if value is None:
      return
    datatype = value.value()
    if datatype is None:
      return
    self.emit(QtCore.SIGNAL("moduleEvent(void)"))


  def __moduleEvent(self):
    try:
      self.__populate()
    except:
      import traceback
      traceback.print_exc()


  def pidFromIndex(self, index):
    item = index.internalPointer()
    if item is None:
      return -1
    return item.pid()


  def __populate(self):
    self.beginResetModel()
    self.__rootItem = StandardItem(None)
    self.setRootItem(self.__rootItem)
    self.__items = {}
    #processusManager = ProcessusManager()
    processusManager = list()
    for processus in processusManager:
      name = processus.name
      if not self.__items.has_key(name):
        categoryItem = ProcessusCategory(name, self.__rootItem)
        self.__rootItem.appendChild(categoryItem)
        self.__items[name] = categoryItem
      else:
        categoryItem = self.__items[name]
      pid = processus.pid
      processusItem = ProcessusItem(pid, categoryItem)
      self.__items[pid] = processusItem
      categoryItem.appendChild(processusItem)
    self.endResetModel()

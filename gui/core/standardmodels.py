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

from dff.ui.gui.core.headeritems import HorizontalHeaderItem


class StandardModel(QtCore.QAbstractItemModel):
  def __init__(self, parent=None):
    super(StandardModel, self).__init__(parent)
    self._rootItem = None
    self.__columns = []


  def flags(self, index):
    if not index.isValid():
      return 0
    # QtCore.Qt.ItemIsUserCheckable is disabled and is managed by delegate
    return QtCore.Qt.ItemIsEnabled
    

  def data(self, index, role):
    if not index.isValid():
      return QtCore.QVariant()
    item = index.internalPointer()
    if item is not None and index.column() < len(self.__columns):
      column = self.__columns[index.column()]
      attribute = column.rawData(HorizontalHeaderItem.AttributeNameRole)
      return self.customData(item, role, attribute)
    return QtCore.QVariant()


  def customData(self, item, role, attribute):
    return item.data(role, attribute)


  def setData(self, index, value, role):
    if not index.isValid():
      return False
    item = index.internalPointer()
    if index.column() < len(self.__columns) and item is not None:
      column = self.__columns[index.column()]
      attribute = column.rawData(HorizontalHeaderItem.AttributeNameRole)
      success, signal = self.setCustomData(item, attribute, value, role)
      if success:
        topLeft = self.createIndex(index.row(), 0, item)
        bottomRight = self.createIndex(index.row(), index.column(), item)
        self.dataChanged.emit(topLeft, bottomRight)
        if signal is not None:
          self.emit(QtCore.SIGNAL(signal))
      return success
    return False


  def setCustomData(self, item, attribute, value, role):
    return item.setData(attribute, value, role)


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
      if success:
        if signal is not None:
          if signal == "sortChanged(int, int)":
            self.sort(*args)
          if args is not None and len(args) > 0:
            self.emit(QtCore.SIGNAL(signal), *args)
          else:
            self.emit(QtCore.SIGNAL(signal))
      return success
    return False


  # descending order == reverse on
  # python stable sort average performance is O(n log n)
  def sort(self, column, order):
    if self._rootItem is None:
      return
    if column < 0 or column > len(self.__columns):
      return
    self.beginResetModel()
    self.__sort(column, order)
    self.endResetModel()


  def __sort(self, columnIndex, order):
    if columnIndex == len(self.__columns):
      for column in self.__columns:
        attribute = column.rawData(HorizontalHeaderItem.AttributeNameRole)
        datatype = column.rawData(HorizontalHeaderItem.DataTypeRole)
        sortOrder = column.rawData(HorizontalHeaderItem.SortOrderRole)
        if sortOrder != -1:
          self._rootItem.sort(attribute, datatype, bool(sortOrder))
    else:
      column = self.__columns[columnIndex]
      datatype = column.rawData(HorizontalHeaderItem.DataTypeRole)
      attribute = column.rawData(HorizontalHeaderItem.AttributeNameRole)
      self._rootItem.sort(attribute, datatype, bool(order))


  def index(self, row, column, parent=QtCore.QModelIndex()):
    if self._rootItem is None or parent is None \
       or not self.hasIndex(row, column, parent):
      return QtCore.QModelIndex()
    if not parent.isValid():
      parentItem = self._rootItem
    else:
      parentItem = parent.internalPointer()
    childItem = parentItem.child(row)
    if childItem is not None:
      return self.createIndex(row, column, childItem)
    else:
      return QtCore.QModelIndex()


  def parent(self, index):
    if self._rootItem is None:
      return QtCore.QModelIndex()
    if not index.isValid():
      return QtCore.QModelIndex()
    childItem = index.internalPointer()
    if childItem is None:
      return QtCore.QModelIndex()
    parentItem = childItem.parent()
    if parentItem is None:
      return QtCore.QModelIndex()
    if parentItem == self._rootItem:
      return QtCore.QModelIndex()
    return self.createIndex(parentItem.row(), 0, parentItem)
      
  
  def rowCount(self, parent):
    if self._rootItem is None:
      return 0
    if not parent.isValid():
      parentItem = self._rootItem
    else:
      parentItem = parent.internalPointer()
    return parentItem.childCount()


  def columnCount(self, parent=QtCore.QModelIndex()):
    return len(self.__columns)


  def pinnedColumnCount(self, parent=QtCore.QModelIndex()):
    pinned = 0
    for column in self.__columns:
      pinState = column.rawData(HorizontalHeaderItem.PinRole)
      if pinState == HorizontalHeaderItem.ForcePinned \
         or pinState == HorizontalHeaderItem.Pinned:
        pinned += 1
    return pinned


  def addColumn(self, column, index=-1):
    if index == -1 or index > len(self.__columns):
      index = len(self.__columns)
    self.__columns.insert(index, column)
    self.headerDataChanged.emit(QtCore.Qt.Horizontal, index, index)
    return True
    

class StandardTreeModel(StandardModel):
  def __init__(self, parent, displayChildrenCount=True):
    super(StandardTreeModel, self).__init__(parent)
    self.__displayChildrenCount = displayChildrenCount


  def customData(self, item, role, attribute):
    if role != QtCore.Qt.DisplayRole:
      return item.data(role, attribute)
    display = item.display(attribute)
    if self.__displayChildrenCount:
      count = item.displayChildrenCount(attribute)
      if count.isValid():
        displayCount = display.toString() + " (" + count.toString() + ")"
        display = QtCore.QVariant(displayCount)
    return display

    
  def setChildrenCountDisplay(self, enable):
    self.__displayChildrenCount = enable
    if self._rootItem is None:
        return
    topLeft = self.createIndex(self._rootItem.row(), 0, self._rootItem)
    bottomRight = self.createIndex(self._rootItem.row(), 1, self._rootItem)
    self.dataChanged.emit(topLeft, bottomRight)


class HorizontalHeaderProxyModel(object):
  def __init__(self, model):
    self.__model = model


  def setData(self, section, value, role):
    return self.__model.setHeaderData(section, QtCore.Qt.Horizontal, value, role)


  def data(self, section, role):
    return self.__model.setHeaderData(QtCore.Qt.Horizontal, value, role)

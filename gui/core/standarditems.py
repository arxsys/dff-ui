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

#from dff.api.filters.libfilters import Filter

# XXX_XXX Mock Class
class Filter():
  def __init__(self, name):
    self.name = name

class StandardItem(object):
  """
  StandardItem class provides the following primitives:
    - parent / children management
    - sorting
    - checkstate
    - recursion role for tree models
  """

  RecursionRole = QtCore.Qt.UserRole
  TagRole = QtCore.Qt.UserRole + 1
  UserRole = QtCore.Qt.UserRole + 2
  
  def __init__(self, parent):
    self._children = []
    self.__parent = parent
    self.__checkState = QtCore.Qt.Unchecked
    self.__isRecursive = False
    # cachedAttribute is reset when setData, appendChild and insertChild are
    # called. Otherwise, rawData won't return most recent values.
    self.__cachedAttribute = ("", None)


  def parent(self):
    return self.__parent


  def children(self):
    return self._children

  
  def appendChild(self, child):
    self.resetCachedAttribute()
    self._children.append(child)


  # ToDo : instead of list and sorted() calls, test with the following container
  # http://code.activestate.com/recipes/577197-sortedcollection/
  # http://www.grantjenks.com/docs/sortedcontainers/sortedlistwithkey.html#SortedListWithKey
  def insertChild(self, idx, child):
    self.resetCachedAttribute()
    self._children.insert(idx, child)
    

  def child(self, row):
    if row < len(self._children):
      return self._children[row]
    else:
      return None


  def childCount(self):
    return len(self._children)


  def row(self):
    if self.__parent is not None:
      return self.__parent.indexOf(self)
    return 0
  

  def indexOf(self, item):
    return self._children.index(item)


  def sort(self, attribute, attributeType, order):
    if attributeType == HorizontalHeaderItem.StringType:
      #XXX check behaviour of strcoll on unicode
      self._children.sort(cmp=locale.strcoll, key=lambda item: item.rawData(attribute), reverse=order)
    else:
      self._children.sort(key=lambda item: item.rawData(attribute), reverse=order)


  def data(self, role, attribute=""):
    if role == QtCore.Qt.CheckStateRole:
      return self.checkState(attribute)
    if role == StandardItem.RecursionRole:
      return self.__isRecursive
    if role == QtCore.Qt.DisplayRole:
      return self.display(attribute)
    if role == QtCore.Qt.DecorationRole:
      return self.decoration(attribute)
    if role == QtCore.Qt.ToolTipRole:
      return self.toolTip(attribute)
    if role == QtCore.Qt.ForegroundRole:
      return self.foreground(attribute)
    if role == QtCore.Qt.ForegroundRole:
      return self.foreground(attribute)
    if role == QtCore.Qt.BackgroundRole:
      return self.background(attribute)
    if role == QtCore.Qt.SizeHintRole:
      return self.sizeHint(attribute)
    return None
  

  def setData(self, attribute, value, role):
    self.__cachedAttributeName = ""
    if role == QtCore.Qt.CheckStateRole:
      success = self.setCheckState(attribute)
      return (success, None)
    if role == StandardItem.TagRole:
      return self.setTag(str(value))
    if role == StandardItem.RecursionRole:
      self.__isRecursive = value
      if self.__isRecursive:
        return (True, "recursionEnabled")
      else:
        return (True, "recursionDisabled")
    return (False, None)


  def cachedAttribute(self, cachedAttributeName, cachedAttributeValue):
    return self.__cachedAttribute


  def setCachedAttribute(self, cachedAttributeName, cachedAttributeValue):
    self.__cachedAttribute = (cachedAttributeName, cachedAttributeValue)

    
  def resetCachedAttribute(self):
    self.__cachedAttribute = ("", None)


  def cachedAttributeName(self):
    return self.__cachedAttribute[0]


  def cachedAttributeValue(self):
    return self.__cachedAttribute[1]

  
  def setTag(self, value):
    return (False, None)


  def tags(self):
    return None


  def properties(self):
    return None


  def checkState(self, attribute):
    if attribute != self.checkableAttribute():
      return None
    return self.__checkState
    
  
  def setCheckState(self, attribute):
    if attribute != self.checkableAttribute():
      return False
    if self.__checkState == QtCore.Qt.Unchecked:
      self.__checkState = QtCore.Qt.PartiallyChecked
      return True
    if self.__checkState == QtCore.Qt.PartiallyChecked:
      self.__checkState = QtCore.Qt.Checked
      return True
    if self.__checkState == QtCore.Qt.Checked:
      self.__checkState = QtCore.Qt.Unchecked
      return True


  def sizeHint(self, attribute):
    return None


  def display(self, attribute):
    return None


  def displayChildrenCount(self, attribute):
    return None


  def decoration(self, attribute):
    return None
  

  def toolTip(self, attribute):
    return None


  def foreground(self, attribute):
    return None  


  def background(self, attribute):
    return None


  def checkableAttribute(self):
    raise NotImplementedError


  def rawData(self, attribute):
    raise NotImplementedError
    #if attribute == "row":
    #  value = self.row()
    #  self.setCachedAttribute(attribute, value)
    #  return value
    #return None


  def _displaySize(self, size):
    kb = 1024
    mb = 1024 * kb
    gb = 1024 * mb
    tb = 1024 * gb
    pb = 1024 * tb
    eb = 1024 * pb
    qobj = QtCore.QObject()
    if size == 0:
      displaySize = qobj.tr("%1 byte").arg(QtCore.QLocale().toString(size))
    elif size >= eb:
      displaySize = qobj.tr("%1 EiB").arg(QtCore.QLocale().toString(float(size) / eb, 'f', 5))
    elif size >= pb:
      displaySize = qobj.tr("%1 PiB").arg(QtCore.QLocale().toString(float(size) / pb, 'f', 4))
    elif size >= tb:
      displaySize = qobj.tr("%1 TiB").arg(QtCore.QLocale().toString(float(size) / tb, 'f', 3))
    elif size >= gb:
      displaySize = qobj.tr("%1 GiB").arg(QtCore.QLocale().toString(float(size) / gb, 'f', 2))
    elif size >= mb:
      displaySize = qobj.tr("%1 MiB").arg(QtCore.QLocale().toString(float(size) / mb, 'f', 1))
    elif size >= kb:
      displaySize = qobj.tr("%1 KiB").arg(QtCore.QLocale().toString(size / kb))
    else:
      displaySize = qobj.tr("%1 bytes").arg(QtCore.QLocale().toString(size))
    return displaySize


class HorizontalHeaderItem(object):

  AliasRole = QtCore.Qt.UserRole
  AttributeNameRole = QtCore.Qt.UserRole + 1
  DataTypeRole = QtCore.Qt.UserRole + 2
  PinRole = QtCore.Qt.UserRole + 3
  FilteredRole = QtCore.Qt.UserRole + 4
  FilterDataRole = QtCore.Qt.UserRole + 5
  SortOrderRole = QtCore.Qt.UserRole + 6
  VisualIndexRole = QtCore.Qt.UserRole + 7
  ResizeRole = QtCore.Qt.UserRole + 8
  
  NumberType = 0
  BooleanType = 1
  SizeType = 2
  StringType = 3
  NumberType = 4
  TimeType = 5
  DataType = 6
  TagType = 7
  CheckedType = 8
  
  ForcePinned = 0
  Pinned = 1
  Unpinned = 2

  def __init__(self, index, attributeName, dataType,
               pinState=2, resizable=True, alias=""):
    self.__index = index
    self.__visualIndex = -1
    self.__attributeName = attributeName
    self.__dataType = dataType
    self.__pinState = pinState
    self.__resizable = resizable
    self.__aliasName = alias
    self.__filterString = ""
    self.__filter = Filter("columnFilter")
    self.__filtered = False
    self.__sortOrder = -1


  def rawData(self, role):
    if role == QtCore.Qt.DisplayRole:
      if len(self.__aliasName):
        return self.__aliasName
      else:
        return self.__attributeName
    if role == HorizontalHeaderItem.AliasRole:
      return self.__aliasName
    if role == HorizontalHeaderItem.AttributeNameRole:
      return self.__attributeName
    if role == HorizontalHeaderItem.DataTypeRole:
      return self.__dataType
    if role == HorizontalHeaderItem.PinRole:
      return self.__pinState
    if role == HorizontalHeaderItem.FilteredRole:
      return self.__filtered
    if role == HorizontalHeaderItem.FilterDataRole:
      return self.__filterString
    if role == HorizontalHeaderItem.SortOrderRole:
      return self.__sortOrder
    return None


  def data(self, role=QtCore.Qt.DisplayRole):
    if role == QtCore.Qt.DisplayRole or \
       role == HorizontalHeaderItem.AttributeNameRole:
      if self.__dataType == HorizontalHeaderItem.CheckedType:
        name = ""
      else:
        name = self.rawData(role)
      return name
    if role == QtCore.Qt.SizeHintRole:
      return self.sizeHint()
    if role == HorizontalHeaderItem.DataTypeRole:
      return self.__dataType
    if role == HorizontalHeaderItem.PinRole:
      return self.__pinState
    if role == HorizontalHeaderItem.FilteredRole:
      return self.__filtered
    if role == HorizontalHeaderItem.FilterDataRole:
      return self.__filterString
    if role == HorizontalHeaderItem.SortOrderRole:
      return self.__sortOrder
    if role == HorizontalHeaderItem.ResizeRole:
      return self.__resizable
    if role == HorizontalHeaderItem.VisualIndexRole:
      return self.__visualIndex
    return None


  def setData(self, value, role):
    if role == HorizontalHeaderItem.AliasRole:
      self.__aliasName = value
      args = (self.__index)
      return (True, "aliasNameChanged()", args)
    if role == HorizontalHeaderItem.PinRole:
      pinState = value
      if pinState is not None:
        self.__pinState = pinState
        args = (self.__index, self.__pinState)
        return (True, "columnPinStateChanged(int, int)", args)
    if role == HorizontalHeaderItem.FilterDataRole:
      self.__filterString = value
      try:
        self.__filter.compile(self.__filterString)
        self.__filtered = True
        args = (self.__index, self.__filterString)
        return (True, "filterEnabled(int, QString)", args)
      except Exception as e:
        self.__filtered = False
        args = (self.__index, self.__filterString)
        return (True, "filterChanged(int, QString)", args)
    if role == HorizontalHeaderItem.SortOrderRole:
      sortOrder = value
      if sortOrder:
        self.__sortOrder = sortOrder
        args = (self.__index, self.__sortOrder)
        return (True, "sortChanged(int, int)", args)
    if role == HorizontalHeaderItem.VisualIndexRole:
      visualIndex = value
      if value is not None:
        self.__visualIndex = visualIndex
        return (True, None, None)
    return (False, None, None)


  def sizeHint(self):
    data = self.data(QtCore.Qt.DisplayRole)
    if data is not None:
      fm = QtWidgets.QApplication.instance().fontMetrics()
      if self.__dataType == HorizontalHeaderItem.CheckedType:
        width = 15
      else:
        width = fm.width(str(data)) + fm.averageCharWidth() * 5 + 60
      sizeHint = QtCore.QSize(width, fm.height()+10)
      return sizeHint
    return None

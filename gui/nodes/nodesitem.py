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

from dff.api.vfs.libvfs import VFS


class NodeItem():

  UidRole = QtCore.Qt.UserRole
  SortRole = UidRole + 1
  RecursionRole = SortRole + 1
  TagViewedRole = RecursionRole + 1
  
  def __init__(self, uid, parent):
    self.__uid = uid
    self.__parent = parent
    self.__children = []
    self.__checkState = QtCore.Qt.Unchecked
    self.__isRecursive = False
    # XXX cachedAttribute is removed when setData
    # appendChild and insertChild are called.
    self.__cachedAttributeName = ""
    self.__cachedAttributeValue = None
    

  def uid(self):
    return self.__uid
  

  def setData(self, attribute, value, role):
    self.__cachedAttributeName = ""
    if role == NodeItem.RecursionRole:
      if attribute == "name":
        self.__isRecursive = value
        if self.__isRecursive:
          return (True, "recursionEnabled")
        else:
          return (True, "recursionDisabled")
    if role == NodeItem.TagViewedRole:
      node = VFS.Get().getNodeById(self.__uid)
      if node.isFile():
        node.setTag("viewed")
        return (True, None)
      return (False, None)
    if role == QtCore.Qt.CheckStateRole and attribute == "checked":
      return (self.__setCheckState(), None)
    return (False, None)
  

  def parent(self):
    return self.__parent

  
  def appendChild(self, child):
    self.__cachedAttributeName = ""
    self.__children.append(child)


  # ToDo : instead of list and sorted() calls, test with the following container
  # http://code.activestate.com/recipes/577197-sortedcollection/
  # http://www.grantjenks.com/docs/sortedcontainers/sortedlistwithkey.html#SortedListWithKey
  # 
  def insertChild(self, idx, child):
    self.__cachedAttributeName = ""
    self.__children.insert(idx, child)
    

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


  def sort(self, attribute, order):
    if attribute == "name":
      #XXX check behaviour of strcoll on unicode
      self.__children.sort(cmp=locale.strcoll, key=lambda item: item.rawData(attribute), reverse=order)
    else:
      self.__children.sort(key=lambda item: item.rawData(attribute), reverse=order)

    
  def data(self, role, attribute, childrenCount=False):
    if self.__uid == -1:
      return QtCore.QVariant()
    if role == QtCore.Qt.SizeHintRole:
      return self.__sizeHintRole(attribute, childrenCount)
    if role == NodeItem.RecursionRole:
      return QtCore.QVariant(self.__isRecursive)
    if role == NodeItem.UidRole:
      return QtCore.QVariant(self.__uid)
    if role == NodeItem.SortRole:
      return self.__sortRole(attribute)
    if role == QtCore.Qt.DisplayRole:
      return self.__displayRole(attribute, childrenCount)
    if role == QtCore.Qt.DecorationRole and attribute == "name":
      return self.__createIconPixmap()
    if role == QtCore.Qt.ForegroundRole:
      return self.__foregroundRole()
    if role == QtCore.Qt.CheckStateRole and attribute == "checked":
      return QtCore.QVariant(self.__checkState)
    if role == QtCore.Qt.ToolTipRole:
      return self.__toolTip()
    return QtCore.QVariant()


  def rawData(self, attribute):
    value = None
    if attribute == self.__cachedAttributeName:
      return self.__cachedAttributeValue
    if attribute == "row":
      value = self.row()
    elif attribute == "uid":
      value = self.__uid
    else:
      try:
        node = VFS.Get().getNodeById(self.__uid)
      except:
        node = None
      if node is None:
        return None
      if attribute == "size":
        value = long(node.size())
      if attribute == "name":
        return node.name()
      if attribute == "type":
        value = node.dataType()
    self.__cachedAttributeName = attribute
    self.__cachedAttributeValue = value
    return value


  def __displayRole(self, attribute, childrenCount):
    if attribute == "checked":
      return QtCore.QVariant("")
    if attribute == "row":
      return QtCore.QVariant(self.row())
    if attribute == "name":
      return self.__displayName(childrenCount)
    if attribute == "uid":
      return QtCore.QVariant(self.__uid)
    if attribute == "size":
      return self.__displaySize()
    else:
      return self.__displayAttribute(attribute)
    return QtCore.QVariant()


  def __sizeHintRole(self, attribute, childrenCount):
    data = self.__displayRole(attribute, childrenCount)
    if data.isValid():
      fm = QtGui.QApplication.instance().fontMetrics()
      width = fm.width(data.toString())
      if attribute == "checked":
        sizeHint = QtCore.QSize(10, fm.height())
      elif attribute == "name":
        sizeHint = QtCore.QSize(width+100, fm.height())
      else:
        sizeHint = QtCore.QSize(width+20, fm.height())
      return QtCore.QVariant(sizeHint)
    return QtCore.QVariant()


  def __toolTip(self):
    node = VFS.Get().getNodeById(self.__uid)
    if node is None:
      return QtCore.QVariant()
    absolute = QtCore.QString.fromUtf8(node.absolute())
    return QtCore.QVariant(absolute)
  
  
  def __createIconPixmap(self):
    node = VFS.Get().getNodeById(self.__uid)
    if node is None:
      return QtCore.QVariant()
    pixmap = QtGui.QPixmap(node.icon())
    if node.hasChildren():
      fso = node.fsobj()
      fsoUid = -1
      if fso != None:
        fsoUid = fso.uid()
      children = node.children()
      childFso = children[0].fsobj()
      childFsoUid = -1
      if childFso:
        childFsoUid = childFso.uid()
      if fsoUid != -1 and childFsoUid != -1 and fsoUid != childFsoUid:
        pixmap = pixmap.scaled(QtCore.QSize(128, 128), QtCore.Qt.KeepAspectRatio)
        painter = QtGui.QPainter(pixmap)
        rootPixmap = QtGui.QPixmap(":root")
        painter.drawPixmap(0, 0, rootPixmap)
        painter.end()
    return QtCore.QVariant(QtGui.QIcon(pixmap))


  def __displaySize(self):
    node = VFS.Get().getNodeById(self.__uid)
    if node is None:
      return QtCore.QVariant()
    if not node.isFile():
      return QtCore.QVariant()
    kb = 1024
    mb = 1024 * kb
    gb = 1024 * mb
    tb = 1024 * gb
    pb = 1024 * tb
    eb = 1024 * pb
    size = node.size()
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
    return QtCore.QVariant(displaySize)
  

  def __displayAttribute(self, attribute):
    # It would be more practical to overload node.__getattr__ method to remove
    # all the following conditions.
    node = VFS.Get().getNodeById(self.__uid)
    if node is None:
      return QtCore.QVariant()
    if attribute == "type":
      datatype = QtCore.QString.fromUtf8(node.dataType())
      return QtCore.QVariant(datatype)
    elif attribute == "extension":
      extention = QtCore.QString.fromUtf8(node.extension())
      return QtCore.QVariant(extension)
    elif attribute == "path":
      if isinstance(node, VLink):
        path = QtCore.QString.fromUtf8(node.linkPath())
      else:
        path = QtCore.QString.fromUtf8(node.path())
      return QtCore.QVariant(path)
    elif attribute == "deleted":
      return QtCore.QVariant(node.isDeleted())
    return QtCore.QVariant()
    
  
  def __displayName(self, childrenCount):
    node = VFS.Get().getNodeById(self.__uid)
    if node is None:
      return QtCore.QVariant()
    name = QtCore.QString.fromUtf8(node.name())
    if childrenCount:
      info = " (" + str(node.totalChildrenCount()) + ")"
      name += QtCore.QString(info)
    return QtCore.QVariant(name)


  def __foregroundRole(self):
    node = VFS.Get().getNodeById(self.__uid)
    if node is None:
      return QtCore.QVariant()
    if node.isDeleted():
      return  QtCore.QVariant(QtGui.QColor(QtCore.Qt.red))
    return QtCore.QVariant()


  def __setCheckState(self):
    if self.__checkState == QtCore.Qt.Unchecked:
      self.__checkState = QtCore.Qt.PartiallyChecked
      return True
    if self.__checkState == QtCore.Qt.PartiallyChecked:
      self.__checkState = QtCore.Qt.Checked
      return True
    if self.__checkState == QtCore.Qt.Checked:
      self.__checkState = QtCore.Qt.Unchecked
      return True
    

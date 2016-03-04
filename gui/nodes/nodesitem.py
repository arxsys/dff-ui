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

from dff.api.vfs.libvfs import VFS

class NodeItem():
  def __init__(self, uid):
    self.__uid = uid
    self.__checked = False


  def uid(self):
    return self.__uid
  

  #def setData(self, role):
  #  pass

  
  def data(self, role, attribute, childrenCount=False):
    if self.__uid == -1:
      return QtCore.QVariant()
    if role == QtCore.Qt.DisplayRole:
      if attribute == "name":
        return self.__displayName(childrenCount)
      if attribute == "uid":
        return QtCore.QVariant(self.__uid)
      if attribute == "size":
        return self.__displaySize()
      else:
        return self.__displayAttribute(attribute)
    if role == QtCore.Qt.DecorationRole:
      return self.__createIconPixmap()
    if role == QtCore.Qt.ForegroundRole:
      return self.__foregroundRole()
    if role == QtCore.Qt.CheckStateRole:
      if attribute == "name":
        return self.__checkStateRole()
      else:
        return QtCore.QVariant()
    if role == QtCore.Qt.ToolTipRole:
      return self.__toolTip()
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
    kb = 1024
    mb = 1024 * kb
    gb = 1024 * mb
    tb = 1024 * gb
    pb = 1024 * tb
    eb = 1024 * pb
    size = node.size()
    qobj = QtCore.QObject()
    if size == 0:
      return qobj.tr("%1 byte").arg(QtCore.QLocale().toString(size))
    if size >= eb:
      return qobj.tr("%1 EiB").arg(QtCore.QLocale().toString(float(size) / eb, 'f', 5))
    if size >= pb:
      return qobj.tr("%1 PiB").arg(QtCore.QLocale().toString(float(size) / pb, 'f', 4))
    if size >= tb:
      return qobj.tr("%1 TiB").arg(QtCore.QLocale().toString(float(size) / tb, 'f', 3))
    if size >= gb:
      return qobj.tr("%1 GiB").arg(QtCore.QLocale().toString(float(size) / gb, 'f', 2))
    if size >= mb:
      return qobj.tr("%1 MiB").arg(QtCore.QLocale().toString(float(size) / mb, 'f', 1))
    if size >= kb:
      return qobj.tr("%1 KiB").arg(QtCore.QLocale().toString(size / kb))
    return qobj.tr("%1 bytes").arg(QtCore.QLocale().toString(size))


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


  def __checkStateRole(self):
    # update selection
    if self.__checked:
      return QtCore.Qt.Checked
    else:
      return QtCore.Qt.Unchecked

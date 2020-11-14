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

from core.standarditems import StandardItem
#from dff.api.vfs.libvfs import VFS, VLink

# XXX move it nodes?
#from dff.ui.gui.api.thumbnail import ThumbnailManager, ScaleConfig


class NodeItem(StandardItem):

  UidRole = StandardItem.UserRole
  PropertiesRole = StandardItem.UserRole + 1
  NameRole = StandardItem.UserRole + 2
  PathRole = StandardItem.UserRole + 3
  
  def __init__(self, uid, parent):
    super(NodeItem, self).__init__(parent)
    self.__uid = uid
    if self.__uid >= 0:
      fm = QtGui.QApplication.fontMetrics()
      self.__displayNameSize = fm.width(self.rawData("name"))


  def data(self, role, attribute=""):
    if role == NodeItem.UidRole:
      return self.__uid
    if role == NodeItem.NameRole:
      node = VFS.Get().getNodeById(self.__uid)
      if node is None:
        None
      return node.name()
    if role == NodeItem.PropertiesRole:
      size, files, folders = self.properties()
      properties = QtCore.QString("Size: ")
      properties.append(self._displaySize(size))
      contains = "|Contains: {} Files, {} Folders".format(files, folders)
      properties.append(contains)
      return properties
    if role == NodeItem.PathRole:
      node = VFS.Get().getNodeById(self.__uid)
      if node is None:
        return None
      return node.path()
    return super(NodeItem, self).data(role, attribute)


  def setTag(self, tag):
    node = VFS.Get().getNodeById(self.__uid)
    if node.isFile() or node.size() > 0:
      node.setTag(tag)
      return (True, None)
    return (False, None)


  def tags(self):
    node = VFS.Get().getNodeById(self.__uid)
    tags = node.tags()
    return tags


  def __recursiveProperties(self, node):
    size = 0
    files = 0
    folders = 0
    if node.size() > 0 or node.isFile():
      size += node.size()
      files += 1
    if node.hasChildren() or node.isDir():
      folders += 1
      children = node.children()
      for child in children:
        rsize, rfiles, rfolders = self.__recursiveProperties(child)
        size += rsize
        files += rfiles
        folders += rfolders
    return size, files, folders


  def properties(self):
    node = VFS.Get().getNodeById(self.__uid)
    children = node.children()
    size = 0
    files = 0
    folders = 0
    for child in children:
      rsize, rfiles, rfolders = self.__recursiveProperties(child)
      size += rsize
      files += rfiles
      folders += rfolders
    return size, files, folders


  def rawData(self, attribute):
    if attribute == self.cachedAttributeName():
      return self.cachedAttributeValue()
    value = None
    if attribute == "uid":
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
    self.setCachedAttribute(attribute, value)
    return value

  
  def checkableAttribute(self):
    return "checked"

  
  def display(self, attribute):
    if attribute == "row":
      return self.row()
    if attribute == "uid":
      return self.__uid
    if attribute == "checked":
      return ""
    else:
      return self._displayAttribute(attribute)
    return None


  def toolTip(self, attribute):
    node = VFS.Get().getNodeById(self.__uid)
    if node is None:
      return None
    absolute = node.absolute()
    return absolute


  def decoration(self, attribute):
    if attribute != "name":
      return None
    node = VFS.Get().getNodeById(self.__uid)
    if node is None:
      return None
    datatype = node.dataType()
    if datatype.find("image/") != -1 or datatype.find("video/") != -1:
      config = ScaleConfig(node, 512)
      pixmap = ThumbnailManager().generate(config)
      if pixmap is None:
        pixmap = QtGui.QPixmap(":file_temporary.png")
      icon = QtGui.QIcon()
      icon.addPixmap(pixmap, QtGui.QIcon.Active)
      icon.addPixmap(pixmap, QtGui.QIcon.Selected)
      return icon
    pixmap = self.__defaultIcon(node)
    if isinstance(node, VLink):
      painter = QtCore.QPainter(pixmap)
      linkPixmap = QPixmap(":vlink")
      painter.drawPixmap(0, 0, linkPixmap)
      painter.end()
    elif node.hasChildren():
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
        painter = QtGui.QPainter(pixmap)
        rootPixmap = QtGui.QPixmap(8, 8)
        rootPixmap.load(":root")
        painter.drawPixmap(0, 0, rootPixmap)
        painter.end()
    icon = QtGui.QIcon()
    icon.addPixmap(pixmap, QtGui.QIcon.Active)
    icon.addPixmap(pixmap, QtGui.QIcon.Selected)
    return icon


  def __defaultIcon(self, node):
    datatype = node.dataType()
    if datatype.find("image/") != -1:
      return QtGui.QPixmap(":image.png")
    elif datatype.find("audio/") != -1:
      return QtGui.QPixmap(":sound.png")
    elif datatype.find("document/pdf") != -1:
      return QtGui.QPixmap(":pdf.png")
    elif datatype.find("document/xls") != -1:
      return QtGui.QPixmap(":spreadsheet.png")
    elif datatype.find("document") != -1:
      return QtGui.QPixmap(":document.png")
    elif datatype.find("video/") != -1:
      return QtGui.QPixmap(":video.png")
    elif datatype.find("archive/") != -1:
      return QtGui.QPixmap(":zip.png")
    return QtGui.QPixmap(node.icon())

  
  def foreground(self, attribute):
    node = VFS.Get().getNodeById(self.__uid)
    if node is None:
      return None
    if node.isDeleted():
      return  QtGui.QColor(QtCore.Qt.red)
    return None
  

  def _displayAttribute(self, attribute):
    # It would be more practical to overload node.__getattr__ method to remove
    # all the following conditions.
    node = VFS.Get().getNodeById(self.__uid)
    if node is None:
      return None
    if attribute == "name":
      name = node.name()
      return name
    if attribute == "size":
      if node.isDir():
        return None
      size = node.size()
      return self._displaySize(size)
    if attribute == "type":
      datatype = node.dataType()
      return datatype
    elif attribute == "extension":
      extention = node.extension()
      return extension
    elif attribute == "path":
      if isinstance(node, VLink):
        path = node.linkPath()
      else:
        path = node.path()
      return path
    elif attribute == "deleted":
      return node.isDeleted()
    return None


  def sizeHint(self, attribute):
    if attribute == "name":
      return QtCore.QSize(self.__displayNameSize, 16)
    data = self.display(attribute)
    if data.isValid():
      width = QtGui.QApplication.fontMetrics().width(data)
      sizeHint = QtCore.QSize(width, 16)
      return sizeHint
    return QtCore.QSize()


  def uid(self):
    return self.__uid


class NodeTreeItem(NodeItem):
  def __init__(self, uid, parent):
    super(NodeTreeItem, self).__init__(uid, parent)


  def displayChildrenCount(self, attribute):
    if attribute == "name":
      node = VFS.Get().getNodeById(self.uid())
      if node is not None:
        return node.totalChildrenCount()
    return None


  def checkableAttribute(self):
    return "name"


  def sizeHint(self, attribute):
    if attribute == "name":
      data = self.display(attribute)
      if data.isValid():
        fm = QtGui.QApplication.instance().fontMetrics()
        width = fm.width(data)
        sizeHint = QtCore.QSize(width+100, 20)
        return sizeHint
    return super(NodeTreeItem, self).sizeHint(attribute)

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


from qtpy import QtCore, QtGui

#from dff.api.vfs.libvfs import TagsManager
from core.standarditems import StandardItem


class TagItem(StandardItem):
  def __init__(self, tagId, parent):
    super(TagItem, self).__init__(parent)
    self.__tagId = tagId


  def tagId(self):
    return self.__tagId

    
  def checkableAttribute(self):
    return "name"


  def sizeHint(self, attribute):
    if attribute == "name":
      data = self.display(attribute)
      if data is not None:
        fm = QtGui.QApplication.instance().fontMetrics()
        width = fm.width(data)
        sizeHint = QtCore.QSize(width+100, 16)
        return sizeHint
    return None


  def display(self, attribute):
    if attribute == "name":
      tag = TagsManager.get().tag(self.__tagId)
      if tag is not None:
        name = QtCore.QString.fromUtf8(tag.name())
        return name
    return None


  def foreground(self, attribute):
    if attribute == "name":
      tag = TagsManager.get().tag(self.__tagId)
      if tag is not None:
        color = tag.color()
        # calculate gray brightness
        g = color.r * 0.299 + color.g * 0.587 + color.b * 0.114
        if g < 128:
          return QtGui.QColor(QtCore.Qt.white)
        else:
          return QtGui.QColor(QtCore.Qt.black)
    return None

  
  def background(self, attribute):
    if attribute == "name":
      tag = TagsManager.get().tag(self.__tagId)
      if tag is not None:
        color = tag.color()
        return QtGui.QColor(color.r, color.g, color.b)
    return None

  
  def displayChildrenCount(self, attribute):
    count = TagsManager.get().nodesCount(self.__tagId)
    return count

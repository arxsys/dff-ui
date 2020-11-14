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

#from dff.api.datatype.libdatatype import DataTypeManager
from core.standarditems import StandardItem


class DatatypeItem(StandardItem):
  def __init__(self, name, parent, isRootCategory=False):
    super(DatatypeItem, self).__init__(parent)
    self.__name = name
    self.__queryType = None


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
      return self.__name
    return None


  def displayChildrenCount(self, attribute):
    if self.childCount() > 0:
      count = 0
      for child in self._children:
        count += child.nodesCount()
    else:
      count = self.nodesCount()
    return count


  def name(self):
    return self.__name


  def absolute(self):
    parent = self.parent()
    if parent is None:
      return self.__name
    path = self.__name
    while parent is not None:
      if len(parent.name()) > 0:
        path = parent.name() + "/" + path
      parent = parent.parent()
    return path


  def setQueryType(self, datatype):
    self.__queryType = datatype


  def queryType(self):
    return self.__queryType


  def nodesCount(self):
    if self.__queryType is not None:
      queryType = self.__queryType
    else:
      queryType = self.absolute()
    return DataTypeManager.Get().nodesCount(queryType)


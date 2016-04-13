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

from dff.ui.gui.core.standarditems import StandardItem, HorizontalHeaderItem


class StandardDelegate(QtGui.QStyledItemDelegate):
  def __init__(self, parent=None):
    super(StandardDelegate, self).__init__(parent)
    self.__frozen = False
    self.__tagOffset = 10
    self.__tagBorderWidth = 10


  def setFrozen(self, frozen):
    self.__frozen = frozen

    
  def paint(self, painter, option, index):
    if index.isValid():
      data = index.model().headerData(index.column(), QtCore.Qt.Horizontal,
                                      HorizontalHeaderItem.VisualIndexRole)
      if data.isValid():
        visualIndex, success = data.toInt()
        if success:
          pinnedColumns = index.model().pinnedColumnCount()-1
          painter.save()
          if self.__frozen and visualIndex == pinnedColumns:
            pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine)
          else:
            pen = QtGui.QPen(QtCore.Qt.black, 0.5, QtCore.Qt.DotLine)
          painter.setPen(pen)
          painter.drawLine(option.rect.topRight(), option.rect.bottomRight())
          painter.restore()
      data = index.model().headerData(index.column(),
                                      QtCore.Qt.Horizontal,
                                      HorizontalHeaderItem.DataTypeRole)
      if data.isValid():
        headerType, success = data.toInt()
        if success and headerType == HorizontalHeaderItem.TagType:
          self._drawTags(painter, option, index)
    super(StandardDelegate, self).paint(painter, option, index)


  def _drawTags(self, painter, option, index):
    # logical way to obtain tags is by calling data. But since tag carries
    # several information (name, color) and PyQt does not manage QMap or QList
    # we have to use internalPointer to access tags
    item = index.internalPointer()
    tags = item.tags()
    if tags is not None and len(tags):
      painter.save()
      self.initStyleOption(option, index)
      painter.setClipRect(option.rect)
      option.rect.setX(self.__tagBorderWidth + option.rect.x())
      for tag in tags:
        flags = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        textRect = painter.boundingRect(option.rect, flags, tag.name())
        #space inside drawing rect to center text
        textRect.setWidth(textRect.width() + self.__tagBorderWidth)
        oldBrush = painter.brush()
        color = tag.color()
        oldPen = painter.pen()
        painter.setPen(QtGui.QPen(QtGui.QColor(color.r, color.g, color.b)))
        painter.setBrush(QtGui.QColor(color.r, color.g, color.b))
        painter.drawRect(textRect)
        painter.setPen(oldPen)
        textCenter = option.rect
        #space to center text
        textCenter.setX(textCenter.x() + (self.__tagBorderWidth / 2))
        alignFlags = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        painter.drawText(textCenter, alignFlags, tag.name())
        #space between tag
        option.rect.setX(option.rect.x() + textRect.width() + self.__tagOffset)
      painter.restore()


class StandardTreeDelegate(StandardDelegate):
  def __init__(self, parent=None):
    super(StandardTreeDelegate, self).__init__(parent)
    self.__displayRecursion = False


  def displayRecursion(self, enable):
    self.__displayRecursion = enable


  def paint(self, painter, option, index):
    if index.isValid() and index.column() == 0 and self.__displayRecursion:
        self.__drawRecursionArrow(painter, option, index)
    super(StandardTreeDelegate, self).paint(painter, option, index)


  # editorEvent has to handle recursion but also checkbox
  def editorEvent(self, event, model, option, index):
    if index.isValid() and index.column() == 0 and self.__displayRecursion:
      position = event.pos().x()
      rectx = option.rect.x()
      stateEnabled = option.state & QtGui.QStyle.State_Enabled
      validEvent = event.type() not in [QtCore.QEvent.MouseMove,
                                        QtCore.QEvent.MouseButtonRelease]
      if validEvent and stateEnabled:
        # check if dealing with recursive icon
        if position >= rectx and position <= rectx + 16:
          isRecursive = model.data(index, StandardItem.RecursionRole).toBool()
          model.setData(index, not isRecursive, StandardItem.RecursionRole)
          return True
        elif position >= rectx + 16 and position <= rectx + 32:
          model.setData(index, 0, QtCore.Qt.CheckStateRole)
          return True
    return super(StandardTreeDelegate, self).editorEvent(event, model,
                                                         option, index)


  def __drawRecursionArrow(self, painter, option, index):
    painter.save()
    isRecursive = index.model().data(index, StandardItem.RecursionRole)
    if isRecursive.toBool():
      icon = QtGui.QPixmap(":rectree_on").scaled(QtCore.QSize(16, 16),
                                                 QtCore.Qt.KeepAspectRatio)
    else:
      icon = QtGui.QPixmap(":rectree_off").scaled(QtCore.QSize(16, 16),
                                                  QtCore.Qt.KeepAspectRatio)
    zx = option.rect.x()
    zy = option.rect.y()
    painter.drawPixmap(QtCore.QRect(zx, zy + 2, icon.width(),
                                    icon.height()), icon)
    painter.restore()
    option.rect.setX(option.rect.x() + icon.width())


class StandardIconDelegate(QtGui.QStyledItemDelegate):
  def __init__(self, parent=None):
    super(StandardIconDelegate, self).__init__(parent)


  def paint(self, painter, option, index):
    if index.isValid():
      self._drawTags(painter, option, index)
    super(StandardIconDelegate, self).paint(painter, option, index)

    
  def sizeHint(self, option, index):
    return QtCore.QSize(128+30, 128+30)


  def _drawTags(self, painter, option, index):
    item = index.internalPointer()
    tags = item.tags()
    if tags is not None and len(tags):
      painter.save()
      #self.initStyleOption(option, index)
      painter.setClipRect(option.rect)
      xpos = option.rect.x()
      ypos = option.rect.y()
      for tag in tags:
        color = tag.color()
        oldPen = painter.pen()
        painter.setBrush(QtGui.QColor(color.r, color.g, color.b))
        painter.drawRect(xpos, ypos, 10, 10)
        ypos += 10
      painter.restore()


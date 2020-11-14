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

from qtpy import QtCore, QtWidgets

from core.standarditems import StandardItem, HorizontalHeaderItem


class StandardDelegate(QtWidgets.QStyledItemDelegate):
  def __init__(self, parent=None):
    super(StandardDelegate, self).__init__(parent)
    self.__frozen = False
    self.__tagOffset = 10
    self.__tagBorderWidth = 10
    self.__iconSize = QtCore.QSize(16, 16)


  def setFrozen(self, frozen):
    self.__frozen = frozen


  def tags(self, index):
    return []


  def setIconSize(self, size):
    self.__iconSize = size


  def initStyleOption(self, option, index):
    super(StandardDelegate, self).initStyleOption(option, index)
    cname = index.model().headerData(index.column(), QtCore.Qt.Horizontal,
                                     QtCore.Qt.DisplayRole)
    if cname == "name":
      option.decorationSize.setWidth(self.__iconSize.width())
      option.decorationSize.setHeight(self.__iconSize.height())
      option.decorationAlignment = QtCore.Qt.AlignCenter
      option.displayAlignment = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
      return
    datatype = HorizontalHeaderItem.NumberType
    data = index.model().headerData(index.column(), QtCore.Qt.Horizontal,
                                    HorizontalHeaderItem.DataTypeRole)
    if data.isValid():
      datatype = data
    if datatype == HorizontalHeaderItem.SizeType:
      option.displayAlignment = QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
    else:
      option.displayAlignment = QtCore.Qt.AlignCenter


  def sizeHint(self, option, index):
    if not index.isValid():
      return QtCore.QSize()
    datatype = HorizontalHeaderItem.NumberType
    data = index.model().headerData(index.column(), QtCore.Qt.Horizontal,
                                    HorizontalHeaderItem.DataTypeRole)
    if data.isValid():
      datatype = data
      if datatype == HorizontalHeaderItem.CheckedType:
        return QtCore.QSize(16, 16)
    else:
      return QtCore.QSize()
    cname = index.model().headerData(index.column(), QtCore.Qt.Horizontal,
                                     QtCore.Qt.DisplayRole)
    data = index.model().data(index, QtCore.Qt.SizeHintRole)
    if data.isValid():
      textSize = data.toSize()
      if textSize.isValid():
        textWidth = textSize.width()
      else:
        textWidth = self._displayTextWidth(option, index)
    else:
      textWidth = self._displayTextWidth(option, index)
    size = QtCore.QSize()
    if option.decorationSize.isValid() and cname == "name":
      size.setWidth(self.__iconSize.width() + textWidth + 30)
      if option.decorationSize.height() > self.__iconSize.height():
        size.setHeight(self.__iconSize.height())
      else:
        size.setHeight(option.decorationSize.height())
    else:
      option.displayAlignment = QtCore.Qt.AlignLeft
      size.setWidth(textWidth + 30)
      size.setHeight(16)
    return size


  def paint(self, painter, option, index):
    if index.isValid():
      if index.model().columnCount() > 1:
        data = index.model().headerData(index.column(), QtCore.Qt.Horizontal,
                                        HorizontalHeaderItem.VisualIndexRole)
        if data.isValid():
          visualIndex = data
          if visualIndex:
            pinnedColumns = index.model().pinnedColumnCount()-1
            painter.save()
            if self.__frozen and visualIndex == pinnedColumns:
              pen = QtWidgets.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine)
            else:
              pen = QtWidgets.QPen(QtCore.Qt.black, 0.5, QtCore.Qt.DotLine)
            painter.setPen(pen)
            painter.drawLine(option.rect.topRight(), option.rect.bottomRight())
            painter.restore()
      data = index.model().headerData(index.column(),
                                      QtCore.Qt.Horizontal,
                                      HorizontalHeaderItem.DataTypeRole)
      if data.isValid():
        headerType = data
        if headerType and headerType == HorizontalHeaderItem.TagType:
          self._drawTags(painter, option, index)
    super(StandardDelegate, self).paint(painter, option, index)


  def _displayTextWidth(self, option, index):
    fm = QtWidgets.QFontMetrics(option.font)
    data = index.model().data(index, QtCore.Qt.DisplayRole)
    if data.isValid():
      return fm.width(data)
    return 0


  def _drawTags(self, painter, option, index):
    # logical way to obtain tags is by calling data. But since tag carries
    # several information (name, color) and PyQt does not manage QMap or QList
    # we have to use internalPointer to access tags
    tags = self.tags(index)
    if len(tags):
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
        painter.setPen(QtWidgets.QPen(QtWidgets.QColor(color.r, color.g, color.b)))
        painter.setBrush(QtWidgets.QColor(color.r, color.g, color.b))
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
      stateEnabled = option.state & QtWidgets.QStyle.State_Enabled
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
      icon = QtWidgets.QPixmap(":rectree_on").scaled(QtCore.QSize(16, 16),
                                                 QtCore.Qt.KeepAspectRatio)
    else:
      icon = QtWidgets.QPixmap(":rectree_off").scaled(QtCore.QSize(16, 16),
                                                  QtCore.Qt.KeepAspectRatio)
    zx = option.rect.x()
    zy = option.rect.y()
    painter.drawPixmap(QtCore.QRect(zx, zy + 2, icon.width(),
                                    icon.height()), icon)
    painter.restore()
    option.rect.setX(option.rect.x() + icon.width())


class StandardIconDelegate(QtWidgets.QStyledItemDelegate):
  def __init__(self, parent=None):
    super(StandardIconDelegate, self).__init__(parent)
    self.__iconSize = QtCore.QSize(128, 128)


  def paint(self, painter, option, index):
    if index.isValid():
      self._drawTags(painter, option, index)
    super(StandardIconDelegate, self).paint(painter, option, index)


  def setIconSize(self, size):
    self.__iconSize = size


  def initStyleOption(self, option, index):
    super(StandardIconDelegate, self).initStyleOption(option, index)
    option.decorationSize.setWidth(self.__iconSize.width())
    option.displayAlignment = QtCore.Qt.AlignCenter
    option.showDecorationSelected = True
    if option.decorationSize.height()  < self.__iconSize.height():
      option.decorationSize.setHeight(self.__iconSize.height())
      option.decorationAlignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter
    else:
      option.decorationAlignment = QtCore.Qt.AlignCenter

    
  def sizeHint(self, option, index):
    size = QtCore.QSize()
    size.setWidth(self.__iconSize.width())
    size.setHeight(self.__iconSize.height() + 30)
    return size


  def tags(self, index):
    return []


  def _drawTags(self, painter, option, index):
    tags = self.tags(index)
    if tags is not None and len(tags):
      painter.save()
      self.initStyleOption(option, index)
      painter.setClipRect(option.rect)
      xpos = option.rect.x()
      ypos = option.rect.y()
      for tag in tags:
        color = tag.color()
        oldPen = painter.pen()
        painter.setBrush(QtWidgets.QColor(color.r, color.g, color.b))
        painter.drawRect(xpos, ypos, 10, 10)
        ypos += 10
      painter.restore()


class StandardListDelegate(QtWidgets.QStyledItemDelegate):
  def __init__(self, parent=None):
    super(StandardListDelegate, self).__init__(parent)
    self.__iconSize = QtCore.QSize(32, 32)


  def paint(self, painter, option, index):
    #if index.isValid():
    #  self._drawTags(painter, option, index)
    super(StandardListDelegate, self).paint(painter, option, index)


  def setIconSize(self, size):
    self.__iconSize = size


  def initStyleOption(self, option, index):
    super(StandardListDelegate, self).initStyleOption(option, index)
    option.decorationSize.setWidth(self.__iconSize.width())
    option.decorationSize.setHeight(self.__iconSize.height())


  def _displayTextWidth(self, option, index):
    fm = QtWidgets.QFontMetrics(option.font)
    data = index.model().data(index, QtCore.Qt.DisplayRole)
    if data.isValid():
      fm.width(data)
    return textWidth


  def sizeHint(self, option, index):
    if not index.isValid():
      return QtCore.QSize()
    cname = index.model().headerData(index.column(), QtCore.Qt.Horizontal,
                                     QtCore.Qt.DisplayRole)
    data = index.model().data(index, QtCore.Qt.SizeHintRole)
    if data.isValid():
      textSize = data.toSize()
      if textSize.isValid():
        textWidth = textSize.width()
      else:
        textWidth = self._displayTextWidth(option, index)
    else:
      textWidth = self._displayTextWidth(option, index)
    size = QtCore.QSize()
    size.setWidth(self.__iconSize.width() + textWidth + 30)
    size.setHeight(self.__iconSize.height())
    return size


  def tags(self, index):
    return []


  def _drawTags(self, painter, option, index):
    tags = self.tags(index)
    if tags is not None and len(tags):
      painter.save()
      self.initStyleOption(option, index)
      painter.setClipRect(option.rect)
      xpos = option.rect.x()
      ypos = option.rect.y()
      for tag in tags:
        color = tag.color()
        oldPen = painter.pen()
        painter.setBrush(QtWidgets.QColor(color.r, color.g, color.b))
        painter.drawRect(xpos, ypos, 10, 10)
        ypos += 10
      painter.restore()

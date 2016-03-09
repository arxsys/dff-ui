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

from dff.ui.gui.nodes.nodesitem import NodeItem


class NodesTreeDelegate(QtGui.QStyledItemDelegate):
  def __init__(self, parent=None):
      QtGui.QStyledItemDelegate.__init__(self, parent)

      
  def paint(self, painter, options, index):
    if index.isValid():
        if index.column() == 0:
            painter.save()
            isRecursive = index.model().data(index, NodeItem.RecursionRole)
            if isRecursive.toBool():
                icon = QtGui.QPixmap(":rectree_on").scaled(QtCore.QSize(16, 16), QtCore.Qt.KeepAspectRatio)
            else:
                icon = QtGui.QPixmap(":rectree_off").scaled(QtCore.QSize(16, 16), QtCore.Qt.KeepAspectRatio)
            zx = options.rect.x()
            zy = options.rect.y()
            painter.drawPixmap(QtCore.QRect(zx, zy + 2, icon.width(), icon.height()), icon)
            painter.restore()
            options.rect.setX(options.rect.x() + icon.width())
    QtGui.QStyledItemDelegate.paint(self, painter, options, index)


  # editorEvent has to handle recursion but also checkbox
  def editorEvent(self, event, model, option, index):
    if index.isValid():
        position = event.pos().x()
        rectx = option.rect.x()
        if event.type() not in [QtCore.QEvent.MouseMove, QtCore.QEvent.MouseButtonRelease] or not (option.state & QtGui.QStyle.State_Enabled):
            # check if dealing with recursive icon
            if position >= rectx and position <= rectx + 16:
              isRecursive = model.data(index, NodeItem.RecursionRole).toBool()
              model.setData(index, not isRecursive, NodeItem.RecursionRole)
              #uid = model.uidFromIndex(index)
              # state just changed so if recursive is set, recursion is disabled
              #self.emit(QtCore.SIGNAL("recursionStateChanged(bool, int)"), not isRecursive, uid)
              return True
            elif position >= rectx + 16 and position <= rectx + 32:
              model.setData(index, 0, QtCore.Qt.CheckStateRole)
              return True
    return QtGui.QStyledItemDelegate.editorEvent(self, event, model, option, index)

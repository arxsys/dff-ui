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

import time

from PyQt4 import QtCore, QtGui

from dff.ui.gui.nodes.nodestablemodel import NodesTableModel, NodesTableFilterModel, NodesTableHeaderItem
from dff.ui.gui.nodes.nodesitem import NodeItem
from dff.ui.gui.nodes.nodesfilterwidgets import FilterWidgetFactory


class NodesTableHeaderProxyModel():
    def __init__(self, model):
        self.__model = model


    def setData(self, section, value, role):
        return self.__model.setHeaderData(section, QtCore.Qt.Horizontal, value, role)


    def data(self, section, role):
        return self.__model.setHeaderData(QtCore.Qt.Horizontal, value, role)


class NodesTableDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, frozen=False, parent=None):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.__frozen = frozen
        self.__tagOffset = 10
        self.__tagBorderWidth = 10


    def paint(self, painter, option, index):
        painter.save()
        visualIndex = self.parent().horizontalHeader().visualIndex(index.column())
        if self.__frozen and visualIndex == index.model().pinnedColumnCount()-1:
            pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine)
        else:
            pen = QtGui.QPen(QtCore.Qt.black, 0.5, QtCore.Qt.DotLine)
        painter.setPen(pen)
        painter.drawLine(option.rect.topRight(), option.rect.bottomRight())
        painter.restore()
        self.__drawTags(painter, option, index)
        super(NodesTableDelegate, self).paint(painter, option, index)


    def __drawTags(self, painter, option, index):
        tags = self.__getTags(index)
        if len(tags):
            painter.save()
            self.initStyleOption(option, index)
            painter.setClipRect(option.rect)
            option.rect.setX(self.__tagBorderWidth + option.rect.x())
            for tag in tags:
                textRect = painter.boundingRect(option.rect,
                                                QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
                                                tag.name())
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
                painter.drawText(textCenter,
                                 QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
                                 QtCore.QString.fromUtf8(tag.name()))
                #space between tag
                option.rect.setX(option.rect.x() + textRect.width() + self.__tagOffset)
            painter.restore()


    def __getTags(self, index):
        tags = []
        if index.isValid():
            _type = index.model().headerData(index.column(),
                                             QtCore.Qt.Horizontal,
                                             NodesTableHeaderItem.DataTypeRole)
            node = index.model().nodeFromIndex(index)
            if _type == NodesTableHeaderItem.TagType and node is not None:
                tags = node.tags()
        return tags


class NodesTableHeaderSettingMenu(QtGui.QMenu):
    def __init__(self, model, index, parent=None):
        QtGui.QMenu.__init__(self, parent)
        self.__model = model
        self.__index = index
        pinState, success = self.__model.headerData(self.__index, QtCore.Qt.Horizontal,
                                           NodesTableHeaderItem.PinRole).toInt()
        if not success:
            return
        if pinState != NodesTableHeaderItem.ForcePinned:
            self.__pinAction = self.addAction(self.tr("Pin"), self.__pin)
            self.__pinAction.setCheckable(True)
            self.__unpinAction = self.addAction(self.tr("Unpin"), self.__unpin)
            self.__unpinAction.setCheckable(True)
            if pinState == NodesTableHeaderItem.Pinned:
                self.__pinAction.setChecked(True)
                self.__unpinAction.setChecked(False)
            else:
                self.__unpinAction.setChecked(True)
                self.__pinAction.setChecked(False)
            self.addSeparator()
            self.addAction(self.tr("Autosize this column"), self.__autosizeColumn)
            self.addAction(self.tr("Autosize all columns"), self.__autosizeColumns)
            self.addSeparator()
            self.addAction(self.tr("Remove this column"), self.__removeColumn)
            self.addAction(self.tr("Add column"), self.__addColumn)
            self.addSeparator()
            self.addAction(self.tr("Reset columns"), self.__resetColumn)
        else:
            self.addAction(self.tr("Autosize all columns"), self.__autosizeColumns)
            self.addAction(self.tr("Add column"), self.__addColumn)
            self.addAction(self.tr("Reset columns"), self.__resetColumn)


    # It is used to update pin status graphically. Model is not updated
    # It is mainly used when model emits columnPinStateChanged and parent
    # is connected to this signal to refresh children.
    def setPinState(self, pinState):
        if pinState == NodesTableHeaderItem.Pinned \
           or pinState == NodesTableHeaderItem.ForcePinned:
            self.__pinAction.setChecked(True)
            self.__unpinAction.setChecked(False)
        else:
            self.__pinAction.setChecked(False)
            self.__unpinAction.setChecked(True)
        

    def __pin(self):
        hdata = self.__model.headerData(self.__index,
                                        QtCore.Qt.Horizontal,
                                        NodesTableHeaderItem.PinRole)
        pinState, success = hdata.toInt()
        if success and pinState == NodesTableHeaderItem.Unpinned and self.__unpinAction.isChecked():
            self.__model.setHeaderData(self.__index, QtCore.Qt.Horizontal,
                                       QtCore.QVariant(NodesTableHeaderItem.Pinned),
                                       NodesTableHeaderItem.PinRole)
        self.__pinAction.setChecked(True)
        self.__unpinAction.setChecked(False)
        self.emit(QtCore.SIGNAL("settingClicked()"))


    def __unpin(self):
        hdata = self.__model.headerData(self.__index,
                                        QtCore.Qt.Horizontal,
                                        NodesTableHeaderItem.PinRole)
        pinState, success = hdata.toInt()
        if success and pinState == NodesTableHeaderItem.Pinned and self.__pinAction.isChecked():
            self.__model.setHeaderData(self.__index, QtCore.Qt.Horizontal,
                                       QtCore.QVariant(NodesTableHeaderItem.Unpinned),
                                       NodesTableHeaderItem.PinRole)
        self.__unpinAction.setChecked(True)
        self.__pinAction.setChecked(False)
        self.emit(QtCore.SIGNAL("settingClicked()"))


    def __autosizeColumn(self):
        self.emit(QtCore.SIGNAL("settingClicked()"))


    def __autosizeColumns(self):
        self.emit(QtCore.SIGNAL("settingClicked()"))


    def __removeColumn(self):
        self.emit(QtCore.SIGNAL("settingClicked()"))


    def __addColumn(self):
        self.emit(QtCore.SIGNAL("settingClicked()"))


    def __resetColumn(self):
        self.emit(QtCore.SIGNAL("settingClicked()"))



class NodesTableHeaderMenuTabBar(QtGui.QTabBar):
    def __init__(self, parent):
        QtGui.QTabBar.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)


    def mousePressEvent(self, event):
        index = self.tabAt(event.pos())
        if index == -1 or index == self.currentIndex():
            self.emit(QtCore.SIGNAL("close()"))
        super(NodesTableHeaderMenuTabBar, self).mousePressEvent(event)


# Todo: Implement proxies for FilterWidget which uses a model.
# These proxies set data on the model which will then emit a signal
# This aims to enable refresh on others HeaderMenus

class NodesTableHeaderMenu(QtGui.QTabWidget):
    def __init__(self, model, index, parent=None):
        QtGui.QTabWidget.__init__(self, parent)
        self.__index = index
        self.__model = model
        self.__filterWidget = None
        self.__settingsMenu = None
        self.setWindowFlags(QtCore.Qt.Popup)
        self.setStyleSheet("QTabWidget::pane { "
                           " margin: 0px,0px,0px,0px;"
                           " border: 0px;"
                           " border-top: 0px;"
                           "}")
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,
                           QtGui.QSizePolicy.Preferred)
        tabBar = NodesTableHeaderMenuTabBar(self)
        self.setTabBar(tabBar)
        self.__initSettingsMenu()
        self.__initFilterWidget()
        self.connect(tabBar, QtCore.SIGNAL("close()"), self.hide)
        self.connect(self.__model,
                     QtCore.SIGNAL("columnPinStateChanged(int, int)"),
                     self.__updatePinState)
        self.connect(self.__model,
                     QtCore.SIGNAL("filterChanged(int, QString)"),
                     self.__filterChanged)
        self.connect(self.__settingsMenu, QtCore.SIGNAL("settingClicked()"),
                     self.hide)
        self.currentChanged.connect(self.__updateTabSize)
        self.hide()


    def __initFilterWidget(self):
        columnType, success = self.__model.headerData(self.__index,
                                                      QtCore.Qt.Horizontal,
                                                      NodesTableHeaderItem.DataTypeRole).toInt()
        if not success:
            return
        attributeName = self.__model.headerData(self.__index,
                                                QtCore.Qt.Horizontal,
                                                NodesTableHeaderItem.AttributeNameRole).toString()
        proxyModel = NodesTableHeaderProxyModel(self.__model)
        self.__filterWidget = FilterWidgetFactory(columnType, attributeName,
                                                  model=proxyModel, index=self.__index,
                                                  parent=self)
        if self.__filterWidget is not None:
            self.addTab(self.__filterWidget, QtGui.QIcon(":column_filter"), "")


    def __initSettingsMenu(self):
        self.__settingsMenu = NodesTableHeaderSettingMenu(self.__model,
                                                          self.__index, self)
        self.__settingsMenu.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                          QtGui.QSizePolicy.Ignored)
        self.addTab(self.__settingsMenu, QtGui.QIcon(":column_settings"), "")


    def mousePressEvent(self, event):
        super(NodesTableHeaderMenu, self).mousePressEvent(event)
        self.__updateTabSize(self.currentIndex())
        self.emit(QtCore.SIGNAL("menuClosed()"))
        self.hide()
        
        
    def show(self):
        super(NodesTableHeaderMenu, self).show()
        self.__updateTabSize(self.currentIndex())


    def __updatePinState(self, index, pinState):
        if index != self.__index:
            return
        self.__settingsMenu.setPinState(pinState)


    def __filterChanged(self, index, _filter):
        if self.isVisible():
            self.__updateTabSize(self.currentIndex())
            return
        if self.__filterWidget is None or index != self.__index:
            return
        self.__filterWidget.setFilter(str(_filter.toUtf8()))


    def __updateTabSize(self, index):
        for idx in xrange(0, self.count()):
            if idx != index:
                _widget = self.widget(idx)
                _widget.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                      QtGui.QSizePolicy.Ignored)
        widget = self.widget(index)
        if widget is None:
            return
        widget.setSizePolicy(QtGui.QSizePolicy.Preferred,
                             QtGui.QSizePolicy.Preferred)
        widget.resize(widget.minimumSizeHint())
        widget.adjustSize()
        self.resize(widget.size())
        self.adjustSize()
        

class NodesTableHeaderView(QtGui.QHeaderView):
    def __init__(self, model, frozen=False, parent=None):
        QtGui.QHeaderView.__init__(self, QtCore.Qt.Horizontal, parent)
        self.setModel(model)
        self.__frozen = frozen
        self.connect(model, QtCore.SIGNAL("columnPinStateChanged(int, int)"),
                     self.__columnPinStateChanged)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setMouseTracking(True)
        self.setMovable(True)
        self.setClickable(True)
        self.__menus = {}
        self.__previousIndex = -1
        self.__mousePressed = False
        self.__resizing = False
        self.__moving = False
        self.__leaved = True
        self.__pinnedColumns = []
        self.__icons = {}
        self.__createDefaultIcons()
        for column in xrange(0, model.columnCount()):
            self.addColumn(column)
        self.setResizeMode(0, QtGui.QHeaderView.Fixed)
        fm = QtGui.QApplication.instance().fontMetrics()
        width = fm.averageCharWidth() * 5
        self.resizeSection(0, width)


    def __createDefaultIcons(self):
        flags = QtCore.Qt.DiffuseAlphaDither|QtCore.Qt.DiffuseDither|QtCore.Qt.AutoColor
        pixmap = QtGui.QPixmap(":column_settings")
        icon = pixmap.scaled(QtCore.QSize(16, 16), QtCore.Qt.KeepAspectRatio)
        self.__icons[":column_settings"] = icon
        pixmap = QtGui.QPixmap(":column_filtered")
        icon = pixmap.scaled(QtCore.QSize(16, 16), QtCore.Qt.KeepAspectRatio)
        self.__icons[":column_filtered"] = icon
        pixmap = QtGui.QPixmap(":column_sorted_09", flags=flags)
        icon = pixmap.scaled(QtCore.QSize(16, 16), QtCore.Qt.KeepAspectRatio)
        self.__icons[":column_sorted_09"] = icon
        pixmap = QtGui.QPixmap(":column_sorted_az")
        icon = pixmap.scaled(QtCore.QSize(16, 16), QtCore.Qt.KeepAspectRatio)
        self.__icons[":column_sorted_az"] = icon
        pixmap = QtGui.QPixmap(":column_sorted_90")
        icon = pixmap.scaled(QtCore.QSize(16, 16), QtCore.Qt.KeepAspectRatio)
        self.__icons[":column_sorted_90"] = icon
        pixmap = QtGui.QPixmap(":column_sorted_za")
        icon = pixmap.scaled(QtCore.QSize(16, 16), QtCore.Qt.KeepAspectRatio)
        self.__icons[":column_sorted_za"] = icon


    def addColumn(self, column):
        pinState, success = self.model().headerData(column, QtCore.Qt.Horizontal,
                                                    NodesTableHeaderItem.PinRole).toInt()
        if not success:
            return
        if pinState == NodesTableHeaderItem.ForcePinned or pinState == NodesTableHeaderItem.Pinned:
            self.__pinnedColumns.append(column)
        self.__menus[len(self.__menus)] =  NodesTableHeaderMenu(self.model(), column, self)


    def removeColumn(self, column):
        if self.__menus.has_key(column):
            del self.__menus[column]


    def enterEvent(self, event):
        self.__leaved = False
        self.viewport().update()
        super(NodesTableHeaderView, self).enterEvent(event)


    def leaveEvent(self, event):
        self.__leaved = True
        self.viewport().update()
        super(NodesTableHeaderView, self).leaveEvent(event)


    def __getSortIcon(self, sortOrder, _type):
        if sortOrder == -1:
            return None
        elif sortOrder == QtCore.Qt.AscendingOrder:
            if _type == NodesTableHeaderItem.NumberType \
               or _type == NodesTableHeaderItem.SizeType:
                return self.__icons[":column_sorted_09"]
            elif _type == NodesTableHeaderItem.StringType:
                return self.__icons[":column_sorted_az"]
            else:
                return None
        elif sortOrder == QtCore.Qt.DescendingOrder:
            if _type == NodesTableHeaderItem.NumberType \
               or _type == NodesTableHeaderItem.SizeType:
                return self.__icons[":column_sorted_90"]
            elif _type == NodesTableHeaderItem.StringType:
                return self.__icons[":column_sorted_za"]
            else:
                return None
        return None


    def __paintDefaultSection(self, painter, rect, logicalIndex):
        name = self.model().headerData(logicalIndex,
                                       QtCore.Qt.Horizontal,
                                       QtCore.Qt.DisplayRole)
        _type = self.model().headerData(logicalIndex,
                                        QtCore.Qt.Horizontal,
                                        NodesTableHeaderItem.DataTypeRole)
        sortOrder = self.model().headerData(logicalIndex,
                                          QtCore.Qt.Horizontal,
                                          NodesTableHeaderItem.SortOrderRole)
        _filter = self.model().headerData(logicalIndex,
                                          QtCore.Qt.Horizontal,
                                          NodesTableHeaderItem.FilterRole)
        sortOrder, success = sortOrder.toInt()
        if not success:
            sortOrder = -1
        sortIcon = self.__getSortIcon(sortOrder, _type)
        filterIcon = None
        if not _filter.toString().isEmpty():
            filterIcon = self.__icons[":column_filtered"]
        textWidth = rect.width() - 20
        textX = rect.x()
        painter.save()
        if sortIcon is not None and sortIcon.width() < rect.width() - 20:
            painter.drawPixmap(QtCore.QRect(rect.x(), 5, sortIcon.width(),
                                            sortIcon.height()), sortIcon)
        if filterIcon is not None:
            if sortIcon is not None and filterIcon.width() < rect.width()-40:
                    painter.drawPixmap(QtCore.QRect(rect.x()+20, 5, filterIcon.width(),
                                                    filterIcon.height()), filterIcon)
                    textX += 36
                    textWidth -= 20
            elif sortIcon is None and filterIcon.width() < rect.width()-20:
                painter.drawPixmap(QtCore.QRect(rect.x()+2, 5, filterIcon.width(),
                                                filterIcon.height()), filterIcon)
        painter.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.black), 1))
        painter.drawLine(QtCore.QLine(rect.bottomLeft(), rect.bottomRight()))
        painter.drawLine(QtCore.QLine(rect.topRight(), rect.bottomRight()))
        textRect = QtCore.QRect(rect)
        textRect.setWidth(textWidth)
        textRect.setX(textX)
        fm = QtGui.QApplication.instance().fontMetrics()
        name = fm.elidedText(name.toString(), QtCore.Qt.ElideLeft, textWidth)
        align = QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
        painter.drawText(textRect, align, name)
        painter.restore()


    def paintSection(self, painter, rect, logicalIndex):
        topLeft = self.mapToGlobal(rect.topLeft())
        bottomRight = self.mapToGlobal(rect.bottomRight())
        cursor = QtGui.QCursor.pos()
        self.__paintDefaultSection(painter, rect, logicalIndex)
        if not self.__leaved and \
           cursor.x() >= topLeft.x() and cursor.x() <= bottomRight.x() \
           and cursor.y() >= topLeft.y() and cursor.y() <= bottomRight.y():
            painter.save()
            icon = self.__icons[":column_settings"]
            painter.drawPixmap(QtCore.QRect(rect.x() + rect.width()-20, 5,
                                            icon.width(), icon.height()), icon)
            painter.restore()


    def mouseReleaseEvent(self, event):
        logicalIndex = self.logicalIndexAt(event.pos())
        if not self.__moving and not self.__resizing \
           and (logicalIndex != -1 and not self.isSectionHidden(logicalIndex)):
            sortOrder = self.model().headerData(logicalIndex,
                                                QtCore.Qt.Horizontal,
                                                NodesTableHeaderItem.SortOrderRole)
            sortOrder, success = sortOrder.toInt()
            if not success:
                sortOrder = -1
            newSortOrder = -1
            if sortOrder == -1:
                newSortOrder = QtCore.Qt.AscendingOrder
            elif sortOrder == QtCore.Qt.AscendingOrder:
                newSortOrder = QtCore.Qt.DescendingOrder
            elif sortOrder == QtCore.Qt.DescendingOrder:
                newSortOrder = -1
            self.model().setHeaderData(logicalIndex,
                                       QtCore.Qt.Horizontal,
                                       QtCore.QVariant(newSortOrder),
                                       NodesTableHeaderItem.SortOrderRole)
        self.__mousePressed = False
        self.__resizing = False
        self.__moving = False
        super(NodesTableHeaderView, self).mouseReleaseEvent(event)


    def mousePressEvent(self, event):
        self.__mousePressed = True
        logicalIndex = self.logicalIndexAt(event.pos())
        if logicalIndex == -1 or self.isSectionHidden(logicalIndex):
            super(NodesTableHeaderView, self).mousePressEvent(event)
            return
        sectionSize = self.sectionSize(logicalIndex)
        sectionPosition = self.sectionPosition(logicalIndex)
        position = event.pos()
        if position.x() >= sectionPosition+5\
           and position.x() <= sectionPosition+sectionSize-25:
            pass
        elif position.x() >= sectionPosition+sectionSize-20 \
             and position.x() <= sectionPosition+sectionSize-4:
            if self.__previousIndex != -1:
                menu = self.__menus[self.__previousIndex]
                menu.hide()
            self.__mousePressed = False
            menu = self.__menus[logicalIndex]
            position.setX(sectionPosition+sectionSize-20)
            position.setY(0)
            globalPosition = self.mapToGlobal(position)
            menu.move(globalPosition.x()-10, globalPosition.y())
            menu.show()
        elif position.x() <= sectionPosition+3 or position.x() >= sectionPosition+sectionSize-3:
            self.__resizing = True
        super(NodesTableHeaderView, self).mousePressEvent(event)


    def mouseDoubleClickEvent(self, event):
        index = self.logicalIndexAt(event.pos())
        if index == 0:
            return
        super(NodesTableHeaderView, self).mouseDoubleClickEvent(event)


    def mouseMoveEvent(self, event):
        logicalIndex = self.logicalIndexAt(event.pos())
        visualIndex = self.visualIndexAt(event.pos().x())
        if not self.__mousePressed:
            if logicalIndex == -1 or self.isSectionHidden(logicalIndex):
                self.__previousIndex = -1
            # Check if it is the same section or another one.
            # If the same section, just return.
            elif self.__previousIndex != logicalIndex:
                self.__previousIndex = logicalIndex
                self.viewport().update()
        elif not self.__frozen and not self.__resizing and visualIndex < len(self.__pinnedColumns):
            return
        elif self.__frozen and not self.__resizing \
             and (visualIndex > len(self.__pinnedColumns) or visualIndex == 0):
            return
        else:
            self.__moving = True
        super(NodesTableHeaderView, self).mouseMoveEvent(event)


    def pinnedColumnsCount(self):
        return len(self.__pinnedColumns)


    # Logical indexes are more stable than visual indexes. Methods only work
    # with logical indexes and call visualIndex to move section
    def __columnPinStateChanged(self, logicalIndex, pinState):
        visualIndex = self.visualIndex(logicalIndex)
        if pinState == NodesTableHeaderItem.Pinned:
            if logicalIndex in self.__pinnedColumns:
                return
            # pinned columns is append to existing ones
            self.moveSection(visualIndex, len(self.__pinnedColumns))
            self.__pinnedColumns.append(logicalIndex)
        elif pinState == NodesTableHeaderItem.Unpinned:
            if logicalIndex not in self.__pinnedColumns:
                return
            # pinned columns is append to existing ones
            self.moveSection(visualIndex, len(self.__pinnedColumns)-1)
            self.__pinnedColumns.remove(logicalIndex)
        else:
            return


class FrozenTableView(QtGui.QTableView):
    def __init__(self, model, parent):
        QtGui.QTableView.__init__(self, parent)
        self.connect(parent.verticalScrollBar(),
                     QtCore.SIGNAL("valueChanged(int)"),
                     self.__updateVerticalScrollBar)
        self.setModel(model)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.setFrameShape(QtGui.QFrame.Box)
        delegate = NodesTableDelegate(frozen=True, parent=self)
        self.setItemDelegate(delegate)
        self.setLineWidth(0)
        self.setMidLineWidth(0)
        highlight = QtGui.QColor(70, 178, 234)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Highlight, highlight)
        self.setPalette(palette)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        headers = NodesTableHeaderView(model, frozen=True)
        self.setHorizontalHeader(headers)
        self.verticalHeader().hide()
        self.__frozenColumns = 0
        for column in xrange(0, self.model().columnCount()):
            pinState, success = self.model().headerData(column, QtCore.Qt.Horizontal,
                                               NodesTableHeaderItem.PinRole).toInt()
            if not success:
                continue
            if pinState == NodesTableHeaderItem.ForcePinned or pinState == NodesTableHeaderItem.Pinned:
                self.setColumnHidden(column, False)
                self.__frozenColumns += 1
            else:
                self.setColumnHidden(column, True)


    def addColumn(self, menu):
        self.horizontalHeader().addColumn(menu)


    def removeColumn(self, index):
        self.horizontalHeader().removeColumn(index)


    def pinColumn(self, logicalIndex):
        self.setColumnHidden(logicalIndex, False)
        self.horizontalHeader().update()
        self.__frozenColumns += 1

        
    def unpinColumn(self, logicalIndex):
        self.setColumnHidden(logicalIndex, True)
        self.__frozenColumns -= 1


    def __updateVerticalScrollBar(self, value):
        self.verticalScrollBar().setValue(value)


class NodesTableView(QtGui.QTableView):
    def __init__(self, parent=None):
        QtGui.QTableView.__init__(self, parent)
        self.__baseModel = NodesTableModel()
        self.__filterModel = NodesTableFilterModel(self.__baseModel)
        self.connect(self.__baseModel, QtCore.SIGNAL("filterChanged(int, QString)"),
                     self.__filterChanged)
        #self.resizeColumnsToContents()
        self.setModel(self.__baseModel)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        highlight = QtGui.QColor(70, 178, 234)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Highlight, highlight)
        self.setPalette(palette)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.__viewedTimer = QtCore.QTimer(self)
        self.__viewedTimer.timeout.connect(self.__manageViewedTag)
        self.__viewedTagInterval = 3
        self.__previousIndex = None
        headers = NodesTableHeaderView(self.__baseModel)
        self.setHorizontalHeader(headers)
        self.verticalHeader().hide()

        delegate = NodesTableDelegate(parent=self)
        self.setItemDelegate(delegate)
        
        self.__frozenTableView = FrozenTableView(self.__baseModel, self)
        self.__frozenTableView.setSelectionModel(self.selectionModel())
        self.__frozenTableView.show()
        self.__updateFrozenTableGeometry()
        self.viewport().stackUnder(self.__frozenTableView)

        self.horizontalHeader().sectionResized.connect(self.__updateFrozenSectionWidth)
        self.__frozenTableView.horizontalHeader().sectionResized.connect(self.__frozenSectionResized)
        self.connect(self.__baseModel,
                     QtCore.SIGNAL("columnPinStateChanged(int, int)"),
                     self.__columnPinStateChanged)
        self.verticalHeader().sectionResized.connect(self.__updateSectionHeight)
        self.verticalScrollBar().valueChanged.connect(self.__updateVerticalScrollBar)
        self.__frozenTableView.verticalScrollBar().valueChanged.connect(self.__frozenVScrollBarChanged)


    def __filterChanged(self, column, query):
        self.setModel(self.__filterModel)
        #if self.__frozenTableView.
        self.__frozenTableView.setModel(self.__filterModel)

        
    def currentChanged(self, current, previous):
        self.__viewedTimer.stop()
        self.__previousIndex = current
        super(NodesTableView, self).currentChanged(current, previous)
        self.__viewedTimer.start(self.__viewedTagInterval*1000)        

        
    def __manageViewedTag(self):
        index = self.currentIndex()
        if not index.isValid():
            return
        if self.__previousIndex is None:
            return
        elif self.__previousIndex == index:
            self.model().setData(index, "viewed", NodeItem.TagViewedRole)
        return


    def setViewedTagInterval(self, seconds):
        self.__viewedTagInterval = seconds
        

    def resizeEvent(self, event):
        super(NodesTableView, self).resizeEvent(event)
        self.__updateFrozenTableGeometry()


    def __columnPinStateChanged(self, logicalIndex, pinState):
        if pinState == NodesTableHeaderItem.Pinned:
            self.__frozenTableView.pinColumn(logicalIndex)
            width = self.columnWidth(logicalIndex)
            self.__frozenTableView.setColumnWidth(logicalIndex, width)
        elif pinState == NodesTableHeaderItem.Unpinned:
            width = self.__frozenTableView.columnWidth(logicalIndex)
            self.__frozenTableView.unpinColumn(logicalIndex)
            self.setColumnWidth(logicalIndex, width)
        self.__updateFrozenTableGeometry()


    def __frozenVScrollBarChanged(self, value):
        self.verticalScrollBar().setValue(value)

    
    def __updateVerticalScrollBar(self, value):
        self.verticalScrollBar().setValue(value)


    def __updateFrozenSectionWidth(self, logicalIndex, oldSize, newSize):
        self.__frozenTableView.setColumnWidth(logicalIndex, newSize)
        self.__updateFrozenTableGeometry()


    def __frozenSectionResized(self, logicalIndex, oldSize, newSize):
        self.setColumnWidth(logicalIndex, newSize)
        self.__updateFrozenTableGeometry()


    def __updateSectionHeight(self, logicalIndex, oldSize, newSize):
        self.__tableView.setRowHeight(logicalIndex, newsize)


    def __updateFrozenTableGeometry(self):
        width = 0
        width2 = 0
        pinnedColumns = self.horizontalHeader().pinnedColumnsCount()
        for column in xrange(0, pinnedColumns):
            logicalIndex = self.horizontalHeader().logicalIndex(column)
            width += self.columnWidth(logicalIndex)
        x = self.verticalHeader().width() + self.frameWidth()
        #width += self.frameWidth()
        height = self.viewport().height() + self.horizontalHeader().height()
        self.__frozenTableView.setGeometry(x, self.frameWidth(), width, height)
                                           
            
        
    def setRootUid(self, uid, isRecursive=False):
        start = time.time()
        self.__viewedTimer.stop()
        self.__baseModel.setRootUid(uid, isRecursive)
        #self.resizeColumnsToContents()
        #self.__frozenTableView.resizeColumnsToContents()
        self.__previousIndex = None
        end = time.time()


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


class NodesTableDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent=None):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.__tagOffset = 10
        self.__tagBorderWidth = 10


    def paint(self, painter, option, index):
        painter.save()
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
    def __init__(self, index, parent=None):
        QtGui.QMenu.__init__(self, parent)
        self.__index = index
        self.__pinAction = self.addAction(self.tr("Pin"), self.__pin)
        self.__pinAction.setCheckable(True)
        self.__unpinAction = self.addAction(self.tr("No pin"), self.__unpin)
        self.__unpinAction.setCheckable(True)
        self.addSeparator()
        self.addAction(self.tr("Autosize this column"), self.__autosizeColumn)
        self.addAction(self.tr("Autosize all columns"), self.__autosizeColumns)
        self.addSeparator()
        self.addAction(self.tr("Reset columns"), self.__resetColumn)


    def __pin(self):
        isChecked = self.__pinAction.isChecked()
        if isChecked:
            self.__unpinAction.setChecked(False)
        else:
            self.__unpinAction.setChecked(True)
        self.emit(QtCore.SIGNAL("columnPinned(int, bool)"), self.__index, isChecked)
        self.emit(QtCore.SIGNAL("settingClicked()"))

        
    def __unpin(self):
        isChecked = self.__unpinAction.isChecked()
        if isChecked:
            self.__pinAction.setChecked(False)
        else:
            self.__pinAction.setChecked(True)
        self.emit(QtCore.SIGNAL("columnPinned(int, bool)"), self.__index, not isChecked)
        self.emit(QtCore.SIGNAL("settingClicked()"))

        
    def __resetColumn(self):
        self.emit(QtCore.SIGNAL("settingClicked()"))


    def __autosizeColumn(self):
        self.emit(QtCore.SIGNAL("settingClicked()"))


    def __autosizeColumns(self):
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



class NodesTableHeaderMenu(QtGui.QTabWidget):
    def __init__(self, model, index, parent=None):
        QtGui.QTabWidget.__init__(self, parent)
        self.__index = index
        self.__model = model
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
        self.connect(tabBar, QtCore.SIGNAL("close()"), self.hide)
        self.__settingsMenu = NodesTableHeaderSettingMenu(index, self)
        self.__settingsMenu.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                          QtGui.QSizePolicy.Ignored)
        self.connect(self.__settingsMenu, QtCore.SIGNAL("settingClicked()"),
                     self.hide)
        self.connect(self.__settingsMenu,
                     QtCore.SIGNAL("columnPinned(int, bool)"),
                     self.__columnPinned)
        self.currentChanged.connect(self.__updateTabSize)
        self.addTab(self.__settingsMenu, QtGui.QIcon(":filter"), "")
        columnType = model.headerData(index, QtCore.Qt.Horizontal,
                                      NodesTableHeaderItem.DataTypeRole)
        attributeName = model.headerData(index, QtCore.Qt.Horizontal,
                                         NodesTableHeaderItem.AttributeNameRole)
        widget = FilterWidgetFactory(columnType, attributeName, parent=self)
        if widget is not None:
            self.connect(widget, QtCore.SIGNAL("filterChanged(QString)"),
                         self.__filterChanged)
            self.addTab(widget, QtGui.QIcon(":filter"), "")
        self.hide()


    def mousePressEvent(self, event):
        super(NodesTableHeaderMenu, self).mousePressEvent(event)
        self.__updateTabSize(self.currentIndex())
        self.hide()
        
        
    def show(self):
        super(NodesTableHeaderMenu, self).show()
        self.__updateTabSize(self.currentIndex())


    def __updateTabSize(self, index):
        for idx in xrange(0, self.count()):
            if idx != index:
                _widget = self.widget(idx)
                _widget.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                      QtGui.QSizePolicy.Ignored)
        widget = self.widget(index)
        widget.setSizePolicy(QtGui.QSizePolicy.Preferred,
                             QtGui.QSizePolicy.Preferred)
        widget.resize(widget.minimumSizeHint())
        widget.adjustSize()
        self.resize(widget.size())
        self.adjustSize()


    def __columnPinned(self, index, state):
        self.__model.setHeaderData(self.__index, QtCore.Qt.Horizontal,
                                   QtCore.QVariant(state),
                                   NodesTableHeaderItem.PinRole)


    def __filterChanged(self, _filter):
        self.__model.setHeaderData(self.__index, QtCore.Qt.Horizontal,
                                   QtCore.QVariant(_filter),
                                   NodesTableHeaderItem.FilterRole)


class NodesTableHeaderButton(QtGui.QPushButton):
    def __init__(self, parent):
        QtGui.QPushButton.__init__(self, QtGui.QIcon(":filter"), "", parent)
        self.setFlat(True)
        self.__menuWidget = None
        self.clicked.connect(self.__clicked)

        
    def setMenuWidget(self, widget):
        self.__menuWidget = widget
        
        
    def __clicked(self, checked):
        if self.__menuWidget is None:
            return
        globalPosition = self.mapToGlobal(self.parent().pos())
        self.__menuWidget.move(globalPosition.x()-8, globalPosition.y()-2)
        self.__menuWidget.show()
        


class NodesTableHeaderView(QtGui.QHeaderView):
    def __init__(self, model, parent=None):
        QtGui.QHeaderView.__init__(self, QtCore.Qt.Horizontal, parent)
        self.setModel(model)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setMouseTracking(True)
        self.setMovable(True)
        self.__buttons = {}
        self.__previousIndex = -1
        self.__mousePressed = False
        self.setClickable(True)
        for column in xrange(0, model.columnCount()):
            menuButton = NodesTableHeaderButton(self)
            menu = NodesTableHeaderMenu(model, column)
            menuButton.setMenuWidget(menu)
            menuButton.hide()
            self.__buttons[column] = (menuButton, menu)
        fm = QtGui.QApplication.instance().fontMetrics()
        width = 100 + fm.averageCharWidth() * 5
        self.setMinimumSectionSize(width)


    def leaveEvent(self, event):
        if self.__previousIndex != -1:
            button, menu = self.__buttons[self.__previousIndex]
            button.hide()
            self.__previousIndex = -1
        super(NodesTableHeaderView, self).leaveEvent(event)

            
    def mousePressEvent(self, event):
        self.setMouseTracking(False)
        self.__mousePressed = True
        if self.__previousIndex != -1:
            button, menu = self.__buttons[self.__previousIndex]
            button.hide()
        super(NodesTableHeaderView, self).mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        super(NodesTableHeaderView, self).mouseReleaseEvent(event)
        self.__mousePressed = False
        self.setMouseTracking(True)
        
        
    def mouseMoveEvent(self, event):
        index = self.logicalIndexAt(event.pos())
        if index == -1 or self.isSectionHidden(index):
            super(NodesTableHeaderView, self).mouseMoveEvent(event)
            return
        sectionLeftPos = self.sectionViewportPosition(index)
        sectionWidth = self.sectionSize(index)
        sectionRightPos = sectionLeftPos + sectionWidth
        # Check if it is the same section or another one.
        # If the same section, just return.
        # if it's another one hide previous section's button
        if self.__previousIndex != -1:
            if self.__previousIndex == index:
                super(NodesTableHeaderView, self).mouseMoveEvent(event)
                return
            else:
                button, menu = self.__buttons[self.__previousIndex]
                button.hide()
        if not self.__mousePressed:
            self.__previousIndex = index
            button, menu = self.__buttons[index]
            button.show()
            button.move(sectionLeftPos+5, 0)
        else:
            self.__previousIndex = -1
        super(NodesTableHeaderView, self).mouseMoveEvent(event)
        

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
        headers = NodesTableHeaderView(model)
        self.setHorizontalHeader(headers)
        self.setSortingEnabled(True)
        self.verticalHeader().hide()
        self.__frozenColumns = 0
        for column in xrange(0, self.model().columnCount()):
            self.setColumnHidden(column, True)


    def isColumnFrozen(self, index):
        visualIndex = self.horizontalHeader().visualIndex(index)
        if visualIndex == -1:
            return False
        return not self.isColumnHidden(visualIndex)
    

    def frozenColumnsCount(self):
        return self.__frozenColumns
    

    def frozenColumnsWidth(self):
        width = 0
        for column in xrange(0, self.__frozenColumns):
            print column
            width += self.columnWidth(column)
        return width

    
    def frozenVisualIndex(self, index):
        visualIndex = self.horizontalHeader().visualIndex(index)
        if visualIndex == -1:
            return -1
        return visualIndex


    def printIndexes(self):
        for i in xrange(0, self.model().columnCount()):
            visualIdx = self.horizontalHeader().visualIndex(i)
            visualData = self.model().headerData(visualIdx, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole).toString()
            logicalData = self.model().headerData(i, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole).toString()
            print("columns[{}]: logical: {}  -- visual: {}".format(i, logicalData, visualData))


    # Working with visual indexes
    def __printMove(self, _from, to):
        fromLogicalIndex = self.horizontalHeader().logicalIndex(_from)
        toLogicalIndex = self.horizontalHeader().logicalIndex(to)
        fromData = self.model().headerData(fromLogicalIndex,
                                           QtCore.Qt.Horizontal,
                                           QtCore.Qt.DisplayRole).toString()
        toData = self.model().headerData(toLogicalIndex,
                                           QtCore.Qt.Horizontal,
                                           QtCore.Qt.DisplayRole).toString()
        print "moving visual index {} to {}".format(fromData, toData)


        
    # Logical indexes are more stable than visual indexes. Methods only work
    # with logical indexes and call visualIndex to move section
    # __frozenColumns corresponds to the maximum visual index
    # horizontalHeader.moveSection works with visual index
    # tableview.setColumnHidden works with logical index...
    def setColumnFrozen(self, index, freeze):
        visualIndex = self.horizontalHeader().visualIndex(index)
        if visualIndex == -1:
            return
        if freeze:
            self.__printMove(visualIndex, self.__frozenColumns)
            self.horizontalHeader().moveSection(visualIndex, self.__frozenColumns)
            self.setColumnHidden(visualIndex, False)
            self.__frozenColumns += 1
        else:
            self.setColumnHidden(visualIndex, True)
            self.__frozenColumns -= 1
    
    
    def __updateVerticalScrollBar(self, value):
        self.verticalScrollBar().setValue(value)

      
        
class NodesTableView(QtGui.QTableView):
    def __init__(self, parent=None):
        QtGui.QTableView.__init__(self, parent)
        self.__baseModel = NodesTableModel()
        self.__filterModel = NodesTableFilterModel(self.__baseModel)
        self.connect(self.__baseModel, QtCore.SIGNAL("filterChanged(int)"),
                     self.__filterChanged)
        self.connect(self.__baseModel, QtCore.SIGNAL("columnPinStateChanged(int, bool)"),
                     self.__columnPinStateChanged)
        self.resizeColumnsToContents()
        self.setModel(self.__baseModel)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.__viewedTimer = QtCore.QTimer(self)
        self.__viewedTimer.timeout.connect(self.__manageViewedTag)
        self.__viewedTagInterval = 3
        self.__previousIndex = None
        headers = NodesTableHeaderView(self.__baseModel)
        self.setHorizontalHeader(headers)
        self.setSortingEnabled(True)
        self.verticalHeader().hide()

        delegate = NodesTableDelegate()
        self.setItemDelegate(delegate)
        
        self.__frozenTableView = FrozenTableView(self.__baseModel, self)
        self.__frozenTableView.setSelectionModel(self.selectionModel())
        #self.__frozenTableView.setColumnWidth(0, self.columnWidth(0))
        self.__frozenTableView.setItemDelegate(delegate)
        self.__frozenTableView.show()
        self.__updateFrozenTableGeometry()
        self.viewport().stackUnder(self.__frozenTableView)
        self.horizontalHeader().sectionResized.connect(self.__updateSectionWidth)
        self.horizontalHeader().sectionMoved.connect(self.__updateSection)
        self.verticalHeader().sectionResized.connect(self.__updateSectionHeight)
        self.verticalScrollBar().valueChanged.connect(self.__updateVerticalScrollBar)
        

    def __filterChanged(self):
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


    # Logical indexes are more stable than visual indexes. Methods only work
    # with logical indexes and call visualIndex to move section
    def __columnPinStateChanged(self, index, isPinned):
        if isPinned == True:
            if self.__frozenTableView.isColumnFrozen(index):
                return
            self.__frozenTableView.setColumnFrozen(index, True)
            frozenVisualIndex = self.__frozenTableView.frozenVisualIndex(index)
            visualIndex = self.horizontalHeader().visualIndex(index)
            self.horizontalHeader().moveSection(visualIndex, frozenVisualIndex)
            frozenColumns = self.__frozenTableView.frozenColumnsCount()
            self.horizontalHeader().moveSection(frozenVisualIndex,
                                                frozenColumns)
        else:
            if not self.__frozenTableView.isColumnFrozen(index):
                return
            frozenColumns = self.__frozenTableView.frozenColumnsCount()
            self.__frozenTableView.setColumnFrozen(index, False)
            self.horizontalHeader().moveSection(index, frozenColumns+1)
        for i in xrange(0, self.__baseModel.columnCount()):
            visualIdx = self.horizontalHeader().visualIndex(i)
            visualData = self.__baseModel.headerData(visualIdx, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole).toString()
            logicalData = self.__baseModel.headerData(i, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole).toString()
            print("columns[{}]: logical: {}  -- visual: {}".format(i, logicalData, visualData))
        self.__frozenTableView.printIndexes()
        self.__updateFrozenTableGeometry()
        

    def resizeEvent(self, event):
        super(NodesTableView, self).resizeEvent(event)
        self.__updateFrozenTableGeometry()


    def moveCursor(self, cursorAction, modifiers):
        current = super(NodesTableView, self).moveCursor(cursorAction, modifiers)
        width = self.__frozenTableView.frozenColumnsWidth()
        if cursorAction == self.MoveLeft and current.column > 0 and self.visualRect(current).topLeft().x() < width:
            value = self.horizontalScrollBar().value() + self.visualRect(current).topLeft().x() - width
            self.horizontalScrollBar().setValue(value)
        return current


    def __updateSection(self, logicalIndex, oldVisualIndex, newVisualIndex):
        print "updateSection"
        frozenColumns = self.__frozenTableView.frozenColumnsCount()
        if newVisualIndex <= frozenColumns:
            self.horizontalHeader().moveSection(newVisualIndex, frozenColumns)
            self.__updateFrozenTableGeometry()
            
    
    def __updateVerticalScrollBar(self, value):
        self.verticalScrollBar().setValue(value)
    

    def __updateSectionWidth(self, logicalIndex, oldSize, newSize):
        frozenColumns = self.__frozenTableView.frozenColumnsCount()
        visualIndex = self.horizontalHeader().visualIndex(logicalIndex)
        print "update section width: ", logicalIndex, visualIndex
        if visualIndex <= frozenColumns:
            self.__frozenTableView.setColumnWidth(logicalIndex, newSize)
            self.__updateFrozenTableGeometry()


    def __updateSectionHeight(self, logicalIndex, oldSize, newSize):
        self.__tableView.setRowHeight(logicalIndex, newsize)


    def __updateFrozenTableGeometry(self):
        frozenColumns = self.__frozenTableView.frozenColumnsCount()
        print frozenColumns
        width = 0
        for column in xrange(0, frozenColumns):
            visualIndex = self.horizontalHeader().visualIndex(column)
            width += self.columnWidth(visualIndex)
        print width
        x = self.verticalHeader().width() + self.frameWidth()
        height = self.viewport().height() + self.horizontalHeader().height()
        self.__frozenTableView.setGeometry(x, self.frameWidth(), width, height)
                                           
            
        
    def setRootUid(self, uid, isRecursive=False):
        start = time.time()
        self.__viewedTimer.stop()
        self.model().setRootUid(uid, isRecursive)
        self.resizeColumnsToContents()
        self.__frozenTableView.resizeColumnsToContents()
        self.__previousIndex = None
        end = time.time()
        print end - start



# class NodeTableView(QTableView):
#     def __init__(self, tablewidget):
#         QTableView.__init__(self)
#         self.tablewidget = tablewidget
#         self.headerorder = {}
#         self.delegate = CheckStateDelegate(self)
#         self.setItemDelegate(self.delegate)
#         self.factor = 1
#         self.configure()

#     def configure(self):
#         self.verticalHeader().setDefaultSectionSize(DEFAULT_SIZE * self.factor)
#         self.setIconSize(QSize(DEFAULT_SIZE * self.factor, DEFAULT_SIZE * self.factor))
#         self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         self.setShowGrid(False)
#         self.setAutoScroll(False)
#         self.setSelectionMode(QAbstractItemView.NoSelection)
#         self.configureHeaders()

#     def configureHeaders(self):
#         self.horizontalHeader().setStretchLastSection(True)
# 	self.horizontalHeader().setMovable(True)
#         self.connect(self.horizontalHeader(), SIGNAL("sectionClicked(int)"), self.headerClicked)
#         self.verticalHeader().hide()

#     def refreshVisible(self):
#         height = self.factor * DEFAULT_SIZE
#         if height < self.rowHeight(0):
#             heigth = self.rowHeight(0)
#         try:
#             visible = self.viewport().height() / height
#             if visible > 0:
#                 self.model().setVisibleRows(visible)
#         except:
#             return

#     def resizeEvent(self, event):
#       self.refreshVisible()

#     def wheelEvent(self, event):
#         currentrow = self.model().currentRow()
#         if self.model().size() <= self.model().visibleRows():
#             return
#         if event.delta() < 0:
#             if currentrow + 3 >= (self.model().size() - self.model().visibleRows()):
#                 v = self.model().seek(self.model().size())
#                 return
#         if event.delta() > 0:
#             v = self.model().seek(-3, 1)
#             return
#         else:
#             v = self.model().seek(3, 1)
#             return


#     def mouseDoubleClickEvent(self, event):
#         index = self.indexAt(event.pos())
#         self.model().select(index.row())
#         node = self.model().getNode(self.model().currentRow() + index.row())
#         if node != None:
#         # This is a directory
#             if isinstance(node, VLink):
#               node = node.linkNode()
#             if node.isDir() or node.hasChildren():
#                 self.emit(SIGNAL("enterDirectory"), node)
#             else:
#                 self.emit(SIGNAL("nodeListDoubleClicked"), node)


#     def keyPressEvent(self, event):
#         node = self.model().currentNode()
#         if node != None:
#             if isinstance(node, VLink):
#                 node = node.linkNode()
#         if event.key() == Qt.Key_Backspace:
#             node = self.model().currentRoot()
#             if node:
#                 self.emit(SIGNAL("enterDirectory"), node.parent())
#         if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
#             if node != None:
#                 if node.isDir() or node.hasChildren():
#                     self.emit(SIGNAL("enterDirectory"), node)
#                 else:
#                     self.emit(SIGNAL("nodeListDoubleClicked"), node)              
#         if event.key() == Qt.Key_Space:
#             if node != None:
#                 if not self.model().selection.isChecked(node):
#                     self.model().selection.add(node)
#                 else:
#                     self.model().selection.rm(node)
#         if event.matches(QKeySequence.MoveToNextLine):
#             if self.model().activeSelection() + 1 >= self.model().visibleRows():
#                 self.model().seek(1, 1)
#                 self.model().select(self.model().visibleRows() - 1)
#             else:
#                 self.model().select(self.model().activeSelection() + 1)
#         elif event.matches(QKeySequence.MoveToPreviousLine):
#             if self.model().activeSelection() - 1 <= 0:
#                 self.model().seek(-1, 1)
#                 self.model().select(0)
#             else:
#                 self.model().select(self.model().activeSelection() - 1)
#         elif event.matches(QKeySequence.MoveToPreviousPage):
#             self.model().seek(-(self.model().visibleRows() - 1), 1)
#             self.model().select(0)
#         elif event.matches(QKeySequence.MoveToNextPage):
#             self.model().seek(self.model().visibleRows() - 1, 1)
#             self.model().select(0)


#     def headerClicked(self, col):
#       self.horizontalHeader().setSortIndicatorShown(True)
#       if col in self.headerorder:
#         if self.headerorder[col] == Qt.DescendingOrder:
#           order = Qt.AscendingOrder
#         else:
#           order = Qt.DescendingOrder
#       else:
#         order = Qt.DescendingOrder
#       self.headerorder[col] = order
#       self.model().sort(col, order)

# class TimeLineNodeTableView(NodeTableView):
#   def __init__(self, tableWidget):
#     NodeTableView.__init__(self, tableWidget)

# class HeaderView(QHeaderView):
#     def __init__(self, view):
#         QHeaderView.__init__(self, Qt.Horizontal)
#         self.isOn = False
#         self.view = view
#         self.setStretchLastSection(True)
#         self.setClickable(True)

#     def paintSection(self, painter, rect, logicalIndex):
#         painter.save()
#         QHeaderView.paintSection(self, painter, rect, logicalIndex)
#         painter.restore()
#         option = QStyleOptionButton()
#         if logicalIndex == 0:
#             option.rect = QRect(3,2,20,20)
#             model = self.view.model()
#             if (self.isOn):
#                 option.state = QStyle.State_On|QStyle.State_Enabled
#             else:
#                 option.state = QStyle.State_Off|QStyle.State_Enabled
#         self.setSortIndicator(logicalIndex, True)
#         self.style().drawPrimitive(QStyle.PE_IndicatorCheckBox, option, painter)
        
#     def mousePressEvent(self, event):
#         option = QStyleOptionButton()
#         option.rect = QRect(3,2,20,20)
#         element = self.style().subElementRect(QStyle.SE_CheckBoxIndicator, option)
#         if element.contains(event.pos()):
#             if self.isOn:
#                 self.isOn = False
#                 self.emit(SIGNAL("headerSelectionClicked"), False)
#             else:
#                 self.emit(SIGNAL("headerSelectionClicked"), True)
#                 self.isOn = True
#             self.update()
#             self.headerDataChanged(Qt.Horizontal, 0, 0)
#         else:
#             index = self.logicalIndexAt(event.pos())
#             if self.cursor().shape() != Qt.SplitHCursor:
#                 self.view.headerClicked(index)
#         QHeaderView.mousePressEvent(self, event)


# class CheckStateDelegate(QStyledItemDelegate):
#   def __init__(self, parent):
#     QStyledItemDelegate.__init__(self, parent) 
#     self.view = parent
#     self.tagSpacement = 10	
#     self.tagBorderSpacement = 10

#   def paint(self, painter, options, index):
#       QStyledItemDelegate.paint(self, painter, options, index)
#       if index.isValid():
# 	  try:
# 	    attrname = self.view.model().availableAttributes()[index.column()]
# 	  except KeyError:
# 	    attrname == None
#           if attrname == "tags": 
#               absrow = self.view.model().currentRow() + index.row()
#               node = self.view.model().getNode(absrow)
#               tags = node.tags()
#               if len(tags) and node != None:
#                   painter.save()
#                   self.initStyleOption(options, index)
#                   painter.setClipRect(options.rect)
#                   options.rect.setX(self.tagBorderSpacement + options.rect.x())
#                   for tag in tags:
#                       textRect = painter.boundingRect(options.rect, Qt.AlignLeft | Qt.AlignVCenter, tag.name())
#                       textRect.setWidth(textRect.width() + self.tagBorderSpacement) #space inside drawing rect for cented text
                      
#                       oldBrush = painter.brush()
#                       color = tag.color()
                      
#                       oldPen = painter.pen()
#                       painter.setPen(QPen(QColor(color.r, color.g, color.b)))
#                       painter.setBrush(QColor(color.r, color.g, color.b))
#                       painter.drawRect(textRect)
#                       painter.setPen(oldPen)
                      
#                       textCenter = options.rect
#                       #space to center text
#                       textCenter.setX(textCenter.x() + (self.tagBorderSpacement / 2))
                                      
#                       painter.drawText(textCenter, Qt.AlignLeft | Qt.AlignVCenter, QString.fromUtf8(tag.name()))
#                       #space between tag
#                       options.rect.setX(options.rect.x() + textRect.width() + self.tagSpacement) 
                      
#                   painter.restore()
 
#   def editorEvent(self, event, model, option, index):
#       if event.type() == QEvent.MouseButtonPress and index.isValid():
#           model.select(index.row())
#           self.view.emit(SIGNAL("nodeListClicked"), event.button())
#           # Detect checkbox click in order to avoid column style detection
#           element = self.view.style().subElementRect(QStyle.SE_CheckBoxIndicator, option)
#           if element.contains(event.pos()) and index.column() == 0:
#               node = model.currentNode()
#               if node != None:
#                   if not model.selection.isChecked(node):
#                       model.selection.add(node)
#                   else:
#                       model.selection.rm(node)
#                   self.view.refreshVisible()
#           return QStyledItemDelegate.editorEvent(self, event, model, option, index)
#       else:
#           return False



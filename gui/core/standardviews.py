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


# Implement BaseItem / BaseModel / BaseView / BaseTreeModel / BaseTreeView
# class BaseItem / BaseModel / BaseView / BaseTreeModel / BaseTreeView
# BaseItem provides primitive for : recursion and checkstate
# BaseModel provides
# Add maintain state for each TreeView / SearchView
#   if enabled, save associated model for each tree item / searches


from qtpy import QtCore, QtGui, QtWidgets

from core.standarditems import StandardItem, HorizontalHeaderItem
from core.standardmenus import HorizontalHeaderMenu, ViewAppearanceMenu, ScreenshotMenu
from core.standarddelegates import StandardDelegate, StandardTreeDelegate, StandardIconDelegate, StandardListDelegate


class StandardTreeView(QtWidgets.QTreeView):
  def __init__(self, parent=None):
    super(StandardTreeView, self).__init__(parent)
    self.expanded.connect(self.__itemExpanded)
    self.setIndentation(10)
    self.setUniformRowHeights(True)
    #self.collapsed.connect(self.__updateColumnsSize)
    self.setAlternatingRowColors(True)
    highlight = QtGui.QColor(70, 178, 234)
    palette = self.palette()
    palette.setColor(QtGui.QPalette.Highlight, highlight)
    self.setPalette(palette)
    self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
    self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    self.__treeDelegate = StandardTreeDelegate()
    self.setItemDelegate(self.__treeDelegate)
    self.__createDefaultContextMenu()
    self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    self.setAutoScroll(True)


  def currentActions(self):
    return self.actions()


  def __createDefaultContextMenu(self):
    expandAction = QtWidgets.QAction(self.tr("Expand all"), self)
    expandAction.setShortcuts(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Right))
    expandAction.setShortcutContext(QtCore.Qt.WidgetShortcut)
    expandAction.triggered.connect(self.expandAll)
    self.addAction(expandAction)
    collapseAction = QtWidgets.QAction(self.tr("Collapse all"), self)
    collapseAction.setShortcuts(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Left))
    collapseAction.setShortcutContext(QtCore.Qt.WidgetShortcut)
    collapseAction.triggered.connect(self.collapseAll)
    self.addAction(collapseAction)
    self.__childrenCountAction = QtWidgets.QAction(self.tr("Display children count"), self)
    self.__childrenCountAction.setCheckable(True)
    self.__childrenCountAction.triggered.connect(self.__childrenCountDisplay)
    self.addAction(self.__childrenCountAction)
    screenshotAction = QtWidgets.QAction(self.tr("Screenshot"), self)
    screenshotMenu = ScreenshotMenu(self)
    screenshotAction.setMenu(screenshotMenu)
    self.addAction(screenshotAction)


  def __itemExpanded(self, index):
    self.resizeColumnToContents(0)
    rect = self.visualRect(index)
    if rect.isValid() and self.horizontalScrollBar().isVisible():
      value = ((rect.x()) * self.horizontalScrollBar().maximum()) / self.viewport().width()
      self.horizontalScrollBar().setValue(value)


  def __childrenCountDisplay(self, checked):
    self.__childrenCountAction.setChecked(checked)
    self.model().setChildrenCountDisplay(checked)


  def setFrozen(self, frozen):
    self.__treeDelegate.setFrozen(frozen)

    
  def displayRecursion(self, enable):
    self.__treeDelegate.displayRecursion(enable)


  def setHorizontalHeader(self, header):
    self.setHeader(header)


  def horizontalHeader(self):
    return self.header()


  def showEvent(self, event):
    super(StandardTreeView, self).showEvent(event)
    self.resizeColumnToContents(0)


  def setModel(self, model):
    if model is None:
      return
    if model == self.model():
      return
    super(StandardTreeView, self).setModel(model)
    self.header().setModel(model)
    self.setChildrenCountDisplay(True)
    self.__childrenCountAction.setChecked(True)


  def setChildrenCountDisplay(self, enable):
    if self.model() is None:
      return
    self.model().setChildrenCountDisplay(enable)


  def addColumn(self, column, index=-1):
    if self.model() is None:
      return None
    return self.model().addColumn(column, index)


  def addColumns(self, columns, index=-1):
    if self.model() is None:
      return
    if index == -1:
      index = self.model().columnCount()
    for column in columns:
      if self.addColumn(column, index):
        index += 1


class StandardTableView(QtWidgets.QTableView):

  MinimumIconSize = QtCore.QSize(16, 16)
  DefaultIconSize = QtCore.QSize(128, 128)
  MaximumIconSize = QtCore.QSize(256, 256)

  def __init__(self, parent=None):
    super(StandardTableView, self).__init__(parent)
    self.__frozen = False
    self.__tableDelegate = StandardDelegate()
    self.setItemDelegate(self.__tableDelegate)
    self.setIconSize(QtCore.QSize(16, 16))
    self.setShowGrid(False)
    self.setAlternatingRowColors(True)
    self.verticalHeader().hide()
    #self.verticalHeader().setResizeMode(QtWidgets.QHeaderView.Fixed)
    highlight = QtGui.QColor(70, 178, 234)
    palette = self.palette()
    palette.setColor(QtGui.QPalette.Highlight, highlight)
    self.setPalette(palette)
    self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    screenshotAction = QtWidgets.QAction(self.tr("Screenshot"), self)
    screenshotMenu = ScreenshotMenu(self)
    screenshotAction.setMenu(screenshotMenu)
    self.addAction(screenshotAction)


  def currentActions(self):
    return self.actions()


  def wheelEvent(self, event):
    if event.modifiers() == QtCore.Qt.ControlModifier:
      if event.delta() > 0:
        self.zoomIn()
      if event.delta() < 0:
        self.zoomOut()
    else:
      super(StandardTableView, self).wheelEvent(event)


  def zoomIn(self):
    size = QtCore.QSize(self.iconSize().width() + 32,
                        self.iconSize().height() + 32)
    self.setIconSize(size)
    self.resizeColumnsToContents()


  def zoomOut(self):
    size = QtCore.QSize(self.iconSize().width() - 32,
                        self.iconSize().height() - 32)
    self.setIconSize(size)
    self.resizeColumnsToContents()


  #def viewOptions(self):
    #options = super(StandardTableView, self).viewOptions()
    #options.displayAlignment = QtCore.Qt.AlignCenter
    #options.showDecorationSelected = False
    #return options


  def setItemDelegate(self, delegate):
    if not isinstance(delegate, StandardDelegate):
      return
    self.__tableDelegate = delegate
    self.__tableDelegate.setIconSize(self.iconSize())
    self.__tableDelegate.setFrozen(self.__frozen)
    super(StandardTableView, self).setItemDelegate(delegate)


  def setIconSize(self, size):
    if size.width() > StandardTableView.MaximumIconSize.width()\
       or size.height() > StandardTableView.MaximumIconSize.height()\
       or size.width() < StandardTableView.MinimumIconSize.width()\
       or size.height() < StandardTableView.MinimumIconSize.height():
      return
    self.__tableDelegate.setIconSize(size)
    super(StandardTableView, self).setIconSize(size)
    self.verticalHeader().setDefaultSectionSize(size.height())
    #self.emit(QtCore.SIGNAL("iconSizeChanged(QSize&)"), size)


  def setFrozen(self, frozen):
    self.__frozen = True
    self.__tableDelegate.setFrozen(frozen)

    
  def showEvent(self, event):
    super(StandardTableView, self).showEvent(event)
    self.resizeColumnToContents(0)


  def setModel(self, model):
    if model is None:
      return
    if model == self.model():
      return
    if self.model() is not None:
      self.model().modelReset.disconnect(self.resizeColumnsToContents)
    super(StandardTableView, self).setModel(model)
    self.model().modelReset.connect(self.resizeColumnsToContents)


  def addColumn(self, column, index=-1):
    if self.model() is None:
      return None
    return self.model().addColumn(column, index)


  def addColumns(self, columns, index=-1):
    if self.model() is None:
      return
    if index == -1:
      index = self.model().columnCount()
    for column in columns:
      if self.addColumn(column, index):
        index += 1


class StandardIconView(QtWidgets.QListView):

  MinimumIconSize = QtCore.QSize(64, 64)
  DefaultIconSize = QtCore.QSize(128, 128)
  MaximumIconSize = QtCore.QSize(512, 512)

  def __init__(self, modelColumn=0, parent=None):
    super(StandardIconView, self).__init__(parent)
    self.__iconDelegate = StandardIconDelegate()
    self.setItemDelegate(self.__iconDelegate)
    self.setIconSize(StandardIconView.DefaultIconSize)
    self.__modelColumn = modelColumn
    self.setModelColumn(modelColumn)
    self.setViewMode(QtWidgets.QListView.IconMode)
    self.setMovement(QtWidgets.QListView.Static)
    self.setFlow(QtWidgets.QListView.LeftToRight)
    self.setLayoutMode(QtWidgets.QListView.Batched)
    self.setUniformItemSizes(True)
    self.setResizeMode(QtWidgets.QListView.Adjust)
    self.setSpacing(10)
    self.setBatchSize(256)
    self.setWordWrap(True)
    self.setSelectionRectVisible(False)
    self.setWrapping(True)
    screenshotAction = QtWidgets.QAction(self.tr("Screenshot"), self)
    screenshotMenu = ScreenshotMenu(self)
    screenshotAction.setMenu(screenshotMenu)
    self.addAction(screenshotAction)


  def currentActions(self):
    return self.actions()


  def wheelEvent(self, event):
    if event.modifiers() == QtCore.Qt.ControlModifier:
      if event.delta() > 0:
        self.zoomIn()
      if event.delta() < 0:
        self.zoomOut()
    else:
      super(StandardIconView, self).wheelEvent(event)


  def zoomIn(self):
    size = QtCore.QSize(self.iconSize().width() + 32,
                        self.iconSize().height() + 32)
    self.setIconSize(size)


  def zoomOut(self):
    size = QtCore.QSize(self.iconSize().width() - 32,
                        self.iconSize().height() - 32)
    self.setIconSize(size)


  def viewOptions(self):
    options = super(StandardIconView, self).viewOptions()
    options.displayAlignment = QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter
    options.showDecorationSelected = False
    return options


  def setItemDelegate(self, delegate):
    if not isinstance(delegate, StandardIconDelegate):
      return
    self.__iconDelegate = delegate
    self.__iconDelegate.setIconSize(self.iconSize())
    super(StandardIconView, self).setItemDelegate(delegate)


  def setIconSize(self, size):
    if size.width() > StandardIconView.MaximumIconSize.width()\
       or size.height() > StandardIconView.MaximumIconSize.height()\
       or size.width() < StandardIconView.MinimumIconSize.width()\
       or size.height() < StandardIconView.MinimumIconSize.height():
      return
    self.__iconDelegate.setIconSize(size)
    super(StandardIconView, self).setIconSize(size)
    return


  def setModel(self, model):
    if model == self.model():
      return
    super(StandardIconView, self).setModel(model)
    self.setModelColumn(self.__modelColumn)


class StandardListView(QtWidgets.QListView):

  MinimumIconSize = QtCore.QSize(16, 16)
  DefaultIconSize = QtCore.QSize(16, 16)
  MaximumIconSize = QtCore.QSize(512, 512)

  def __init__(self, modelColumn=0, parent=None):
    super(StandardListView, self).__init__(parent)
    self.__listDelegate = StandardListDelegate()
    self.setItemDelegate(self.__listDelegate)
    self.setIconSize(StandardListView.DefaultIconSize)
    self.setFlow(QtWidgets.QListView.TopToBottom)
    self.__modelColumn = modelColumn
    self.setModelColumn(modelColumn)
    self.setViewMode(QtWidgets.QListView.IconMode)
    self.setMovement(QtWidgets.QListView.Static)
    self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)
    self.setLayoutMode(QtWidgets.QListView.Batched)
    self.setResizeMode(QtWidgets.QListView.Adjust)
    self.setBatchSize(256)
    self.setWrapping(True)
    self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)
    self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)
    screenshotAction = QtWidgets.QAction(self.tr("Screenshot"), self)
    screenshotMenu = ScreenshotMenu(self)
    screenshotAction.setMenu(screenshotMenu)
    self.addAction(screenshotAction)


  def currentActions(self):
    return self.actions()


  def wheelEvent(self, event):
    if event.modifiers() == QtCore.Qt.ControlModifier:
      if event.delta() > 0:
        self.zoomIn()
      if event.delta() < 0:
        self.zoomOut()
    else:
      super(StandardListView, self).wheelEvent(event)


  def zoomIn(self):
    size = QtCore.QSize(self.iconSize().width() + 32,
                        self.iconSize().height() + 32)
    self.setIconSize(size)


  def zoomOut(self):
    size = QtCore.QSize(self.iconSize().width() - 32,
                        self.iconSize().height() - 32)
    self.setIconSize(size)
    

  def viewOptions(self):
    options = super(StandardListView, self).viewOptions()
    options.displayAlignment = QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft
    options.decorationPosition = QtWidgets.QStyleOptionViewItem.Left
    options.decorationAlignment = QtCore.Qt.AlignCenter
    options.showDecorationSelected = True
    return options


  def setItemDelegate(self, delegate):
    if not isinstance(delegate, StandardListDelegate):
      return
    self.__listDelegate = delegate
    self.__listDelegate.setIconSize(self.iconSize())
    super(StandardListView, self).setItemDelegate(delegate)


  def setIconSize(self, size):
    if size.width() > StandardListView.MaximumIconSize.width()\
       or size.height() > StandardListView.MaximumIconSize.height()\
       or size.width() < StandardListView.MinimumIconSize.width()\
       or size.height() < StandardListView.MinimumIconSize.height():
      return
    self.__listDelegate.setIconSize(size)
    super(StandardListView, self).setIconSize(size)
    return


  def setModel(self, model):
    if model is None:
      return
    if model == self.model():
      return
    super(StandardListView, self).setModel(model)
    self.setModelColumn(self.__modelColumn)

    
class StandardFrozenView(QtWidgets.QWidget):
  def __init__(self, viewFactory, parent=None):
    super(StandardFrozenView, self).__init__(parent)
    self.setLayout(QtWidgets.QHBoxLayout(self))
    self.layout().setContentsMargins(0, 0, 0, 0)
    self.__frozenColumns = 0
    self.__previousIndex = None
    self.__viewedTagEnable = True
    self.__viewedTimer = QtCore.QTimer(self)
    self.__viewedTimer.timeout.connect(self.__manageViewedTag)
    self.__viewedTagInterval = 3
    self._baseView = viewFactory()
    self.__baseModel = self._baseView.model()
    self.__configureBaseView()
    self.addActions(self._baseView.actions())
    self.layout().addWidget(self._baseView)
    self._frozenView = viewFactory(self._baseView)
    self.__configureFrozenView()
    if self.__frozenColumns != 0:
      self._frozenView.show()
    else:
      self._frozenView.hide()
    self.__updateFrozenViewGeometry()
    self._baseView.viewport().stackUnder(self._frozenView)

    baseWidthResized = self._baseView.horizontalHeader().sectionResized
    baseWidthResized.connect(self.__updateFrozenSectionWidth)
    frozenWidthResized = self._frozenView.horizontalHeader().sectionResized
    frozenWidthResized.connect(self.__updateBaseSectionWidth)

    # self.connect(self.__baseModel,
    #              QtCore.SIGNAL("columnPinStateChanged(int, int)"),
    #              self.__columnPinStateChanged)

    # self.connect(self._baseView, QtCore.SIGNAL("iconSizeChanged(QSize&)"),
    #              self.__updateFrozenIconSize)
    # self.connect(self._frozenView, QtCore.SIGNAL("iconSizeChanged(QSize&)"),
    #              self.__updateBaseIconSize)

    valueChanged = self._baseView.verticalScrollBar().valueChanged
    valueChanged.connect(self._frozenView.verticalScrollBar().setValue)
    valueChanged = self._frozenView.verticalScrollBar().valueChanged
    valueChanged.connect(self._baseView.verticalScrollBar().setValue)

    self._baseView.clicked.connect(self.__clicked)
    self._frozenView.clicked.connect(self.__clicked)
    self._baseView.doubleClicked.connect(self.__doubleClicked)
    self._frozenView.doubleClicked.connect(self.__doubleClicked)
    

  def model(self):
    return self.__baseModel


  def currentActions(self):
    return self._baseView.currentActions()


  def setModel(self, model):
    if model is None:
      return
    # if self.__baseModel is not None:
      # self.disconnect(self.__baseModel,
      #              QtCore.SIGNAL("columnPinStateChanged(int, int)"),
      #              self.__columnPinStateChanged)
    self.__baseModel = model
    self._baseView.setModel(self.__baseModel)
    self._frozenView.setModel(self.__baseModel)
    # self.connect(self.__baseModel,
    #                 QtCore.SIGNAL("columnPinStateChanged(int, int)"),
    #                 self.__columnPinStateChanged)
    self._baseView.horizontalHeader().setModel(self.__baseModel)
    self._frozenView.horizontalHeader().setModel(self.__baseModel)
    for column in range(0, self.__baseModel.columnCount()):
      data = self.__baseModel.headerData(column, QtCore.Qt.Horizontal,
                                         HorizontalHeaderItem.PinRole)
      if data is None:
        continue
      pinState = data
      if pinState == HorizontalHeaderItem.ForcePinned or \
         pinState == HorizontalHeaderItem.Pinned:
        self._frozenView.setColumnHidden(column, False)
        self.__frozenColumns += 1
      else:
        self._frozenView.setColumnHidden(column, True)
    self._frozenView.setSelectionModel(self._baseView.selectionModel())
    if self.__frozenColumns != 0:
      self._frozenView.show()
    else:
      self._frozenView.hide()
    self.__updateFrozenViewGeometry()


  def __updateFrozenIconSize(self, baseSize):
    frozenSize = self._frozenView.iconSize()
    if frozenSize.width() != baseSize.width() or \
       frozenSize.height() != baseSize.height():
      self._frozenView.setIconSize(baseSize)


  def __updateBaseIconSize(self, frozenSize):
    baseSize = self._baseView.iconSize()
    if baseSize.width() != frozenSize.width() or \
       baseSize.height() != frozenSize.height():
      self._baseView.setIconSize(frozenSize)


  def enableViewedTag(self, enable):
    self.__viewedTagEnable = enable


  def setViewedTagInterval(self, seconds):
    self.__viewedTagInterval = seconds


  def setCurrentIndex(self, index):
    self._baseView.setCurrentIndex(index)
    self._frozenView.setCurrentIndex(index)


  def __configureBaseView(self):
    self._baseView.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
    self._baseView.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
    header = StandardHeaderView(self.__baseModel)
    self._baseView.setHorizontalHeader(header)

    
  def __configureFrozenView(self):
    self._frozenView.setModel(self.__baseModel)
    self._frozenView.setFrozen(True)
    self._frozenView.setFocusPolicy(QtCore.Qt.NoFocus)
    self._frozenView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    self._frozenView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    self._frozenView.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
    self._frozenView.setFrameShape(QtWidgets.QFrame.Box)
    self._frozenView.setLineWidth(0)
    self._frozenView.setMidLineWidth(0)
    header = StandardHeaderView(self.__baseModel, frozen=True)
    self._frozenView.setHorizontalHeader(header)
    for column in range(0, self.__baseModel.columnCount()):
      data = self.__baseModel.headerData(column, QtCore.Qt.Horizontal,
                                         HorizontalHeaderItem.PinRole)
      if data is None:
        continue
      pinState = data
      if pinState == HorizontalHeaderItem.ForcePinned or \
         pinState == HorizontalHeaderItem.Pinned:
        self._frozenView.setColumnHidden(column, False)
        self.__frozenColumns += 1
      else:
        self._frozenView.setColumnHidden(column, True)
    self._frozenView.setSelectionModel(self._baseView.selectionModel())


  def __pinColumn(self, logicalIndex):
    self._frozenView.setColumnHidden(logicalIndex, False)
    self._frozenView.horizontalHeader().update()
    self.__frozenColumns += 1
    width = self._baseView.columnWidth(logicalIndex)
    self._frozenView.setColumnWidth(logicalIndex, width)
    

  def __unpinColumn(self, logicalIndex):
    width = self._frozenView.columnWidth(logicalIndex)
    self._frozenView.setColumnHidden(logicalIndex, True)
    self.__frozenColumns -= 1
    self._baseView.setColumnWidth(logicalIndex, width)
    self.__updateFrozenViewGeometry()


  def __doubleClicked(self, index):
    self.emit(QtCore.SIGNAL("doubleClicked(const QModelIndex&)"), index)


  def __clicked(self, index):
    if self.__viewedTagEnable:
      self.__viewedTimer.stop()
      self.__previousIndex = index
    if self.sender() == self._baseView:
      self._frozenView.setCurrentIndex(index)
    if self.__viewedTagEnable:
      self.__viewedTimer.start(self.__viewedTagInterval*1000)
    self.emit(QtCore.SIGNAL("clicked(const QModelIndex&)"), index)
    

  def __columnPinStateChanged(self, logicalIndex, pinState):
    if pinState == HorizontalHeaderItem.Pinned:
      self.__pinColumn(logicalIndex)
    elif pinState == HorizontalHeaderItem.Unpinned:
      self.__unpinColumn(logicalIndex)
    if self.__frozenColumns != 0:
      self._frozenView.show()
    else:
      self._frozenView.hide()


  def __updateFrozenVerticalScrollBar(self, value):
    self._frozenView.verticalScrollBar().setValue(value)


  def __updateBaseVerticalScrollBar(self, value):
    self._baseView.verticalScrollBar().setValue(value)


  def __updateFrozenSectionWidth(self, logicalIndex, oldSize, newSize):
    if self._frozenView.columnWidth(logicalIndex) != newSize:
      self._frozenView.setColumnWidth(logicalIndex, newSize)
    self.__updateFrozenViewGeometry()


  def __updateBaseSectionWidth(self, logicalIndex, oldSize, newSize):
    if self._baseView.columnWidth(logicalIndex) != newSize:
      self._baseView.setColumnWidth(logicalIndex, newSize)
    self.__updateFrozenViewGeometry()


  def __updateFrozenSectionHeight(self, logicalIndex, oldSize, newSize):
    if self._frozenView.verticalHeader().sectionSize(logicalIndex) != newSize:
      self._frozenView.verticalHeader().sectionResize(logicalIndex, newSize)
    #self.__updateFrozenViewGeometry()


  def __updateBaseSectionHeight(self, logicalIndex, oldSize, newSize):
    if self._baseView.verticalHeader().sectionSize(logicalIndex) != newSize:
      self._baseView.verticalHeader().sectionResize(logicalIndex, newSize)
    #self.__updateFrozenViewGeometry()


  def __updateFrozenViewGeometry(self):
    width = 0
    pinnedColumns = self._baseView.horizontalHeader().pinnedColumnsCount()
    for column in range(0, pinnedColumns):
      logicalIndex = self._baseView.horizontalHeader().logicalIndex(column)
      width += self._baseView.columnWidth(logicalIndex)
    x = self._baseView.frameWidth()
    height = self._baseView.viewport().height() + self._baseView.horizontalHeader().height()
    self._frozenView.setGeometry(x, self._baseView.frameWidth(), width, height)


  def __manageViewedTag(self):
    if not self.__viewedTagEnable:
      return
    index = self._baseView.currentIndex()
    if not index.isValid():
      return
    if self.__previousIndex is None:
      return
    elif self.__previousIndex == index:
      self._baseView.model().setData(index, "viewed", StandardItem.TagRole)
    return


class StandardFrozenTreeView(StandardFrozenView):
  def __init__(self, viewFactory, parent=None):
    super(StandardFrozenTreeView, self).__init__(viewFactory, parent)
    self._baseView.collapsed.connect(self._frozenView.collapse)
    self._frozenView.collapsed.connect(self._baseView.collapse)
    self._baseView.expanded.connect(self._frozenView.expand)
    self._frozenView.expanded.connect(self._baseView.expand)


  def displayRecursion(self, display):
    self._baseView.displayRecursion(display)
    self._frozenView.displayRecursion(display)


class StandardHeaderView(QtWidgets.QHeaderView):
  def __init__(self, model, frozen=False, parent=None):
    super(StandardHeaderView, self).__init__(QtCore.Qt.Horizontal, parent)
    self.setModel(model)
    self.__frozen = frozen
    #self.connect(model, QtCore.SIGNAL("columnPinStateChanged(int, int)"),
    #             self.__columnPinStateChanged)
    self.sectionMoved.connect(self.__sectionMoved)
    self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.setMouseTracking(True)
    #self.setMovable(True)
    self.__menus = {}
    self.__previousIndex = -1
    self.__mousePressed = False
    self.__resizing = False
    self.__moving = False
    self.__leaved = True
    self.__pinnedColumns = []
    self.__icons = {}
    self.__createDefaultIcons()
    for column in range(0, model.columnCount()):
      self.addColumn(column)


  def setModel(self, model):
    if model is None:
      return
    if model == self.model():
      return
    # if self.model() is not None:
    #   self.disconnect(self.model(), QtCore.SIGNAL("columnPinStateChanged(int, int)"),
    #                   self.__columnPinStateChanged)
    #self.connect(model, QtCore.SIGNAL("columnPinStateChanged(int, int)"),
    #             self.__columnPinStateChanged)
    super(StandardHeaderView, self).setModel(model)
    self.__menus = {}
    self.__pinnedColumns = []
    for column in range(0, model.columnCount()):
      self.addColumn(column)


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
    visualIndex = self.visualIndex(column)
    self.model().setHeaderData(column, QtCore.Qt.Horizontal, visualIndex,
                               HorizontalHeaderItem.VisualIndexRole)
    resizable = self.model().headerData(column, QtCore.Qt.Horizontal,
                                        HorizontalHeaderItem.ResizeRole)
    if not resizable:
      pass
      #self.setResizeMode(column, QtWidgets.QHeaderView.Fixed)
    pinState = self.model().headerData(column, QtCore.Qt.Horizontal,
                                                HorizontalHeaderItem.PinRole)
    if pinState is not None:
      if pinState == HorizontalHeaderItem.ForcePinned or pinState == HorizontalHeaderItem.Pinned:
        self.__pinnedColumns.append(column)
    self.__menus[len(self.__menus)] = HorizontalHeaderMenu(self.model(), column, self)


  def removeColumn(self, column):
    if self.__menus.has_key(column):
      del self.__menus[column]


  def enterEvent(self, event):
    self.__leaved = False
    self.viewport().update()
    super(StandardHeaderView, self).enterEvent(event)


  def leaveEvent(self, event):
    self.__leaved = True
    self.viewport().update()
    super(StandardHeaderView, self).leaveEvent(event)


  def __getSortIcon(self, sortOrder, _type):
    if sortOrder == -1:
      return None
    elif sortOrder == QtCore.Qt.AscendingOrder:
      if _type == HorizontalHeaderItem.NumberType \
         or _type == HorizontalHeaderItem.SizeType:
        return self.__icons[":column_sorted_09"]
      elif _type == HorizontalHeaderItem.StringType:
        return self.__icons[":column_sorted_az"]
      else:
        return None
    elif sortOrder == QtCore.Qt.DescendingOrder:
      if _type == HorizontalHeaderItem.NumberType \
         or _type == HorizontalHeaderItem.SizeType:
        return self.__icons[":column_sorted_90"]
      elif _type == HorizontalHeaderItem.StringType:
        return self.__icons[":column_sorted_za"]
      else:
        return None
    return None


  def __paintDefaultSection(self, painter, rect, logicalIndex):
    if not rect.isValid():
      return
    if self.isSectionHidden(logicalIndex):
      return
    name = self.model().headerData(logicalIndex,
                                   QtCore.Qt.Horizontal,
                                   QtCore.Qt.DisplayRole)
    _type = self.model().headerData(logicalIndex,
                                    QtCore.Qt.Horizontal,
                                    HorizontalHeaderItem.DataTypeRole)
    sortOrder = self.model().headerData(logicalIndex,
                                        QtCore.Qt.Horizontal,
                                        HorizontalHeaderItem.SortOrderRole)
    filtered = self.model().headerData(logicalIndex,
                                       QtCore.Qt.Horizontal,
                                       HorizontalHeaderItem.FilteredRole)
    pinState = self.model().headerData(logicalIndex,
                                       QtCore.Qt.Horizontal,
                                       HorizontalHeaderItem.PinRole)
    if sortOrder is None:
      sortOrder = -1
    painter.save()
    option = QtWidgets.QStyleOptionHeader()
    self.initStyleOption(option)
    state = QtWidgets.QStyle.State_None
    if self.isEnabled():
      state = state | QtWidgets.QStyle.State_Enabled
    if self.window().isActiveWindow():
      state = state | QtWidgets.QStyle.State_Active
    if pinState == HorizontalHeaderItem.Pinned \
       or pinState == HorizontalHeaderItem.ForcePinned:
      state = state | QtWidgets.QStyle.State_Sunken
    option.rect = rect
    option.section = logicalIndex
    option.state = option.state | state
    visualIndex = self.visualIndex(logicalIndex)
    if self.count() == 1:
      option.position = QtWidgets.QStyleOptionHeader.OnlyOneSection
    elif visualIndex == 0:
      option.position = QtWidgets.QStyleOptionHeader.Beginning
    elif visualIndex == self.count() - 1:
      option.position = QtWidgets.QStyleOptionHeader.End
    else:
      option.position = QtWidgets.QStyleOptionHeader.Middle
    option.orientation = QtCore.Qt.Horizontal
    self.style().drawControl(QtWidgets.QStyle.CE_HeaderSection, option, painter, self)
    painter.restore()
    sortIcon = self.__getSortIcon(sortOrder, _type)
    filterIcon = None
    if filtered:
      filterIcon = self.__icons[":column_filtered"]
    textWidth = rect.width() - 20
    textX = rect.x()
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
    textRect = QtCore.QRect(rect)
    textRect.setWidth(textWidth)
    textRect.setX(textX)
    fm = QtWidgets.QApplication.instance().fontMetrics()
    name = fm.elidedText(str(name), QtCore.Qt.ElideLeft, textWidth)
    align = QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
    painter.drawText(textRect, align, name)


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
                                          HorizontalHeaderItem.SortOrderRole)
      print("{}\n{}\n".format(sortOrder, type(sortOrder), dir(sortOrder)))
      if sortOrder is None:
        sortOrder = -1
        newSortOrder = -1
      if sortOrder == -1:
        newSortOrder = QtCore.Qt.AscendingOrder
      elif sortOrder == QtCore.Qt.AscendingOrder:
        newSortOrder = QtCore.Qt.DescendingOrder
      elif sortOrder == QtCore.Qt.DescendingOrder:
        newSortOrder = -1
      print(newSortOrder)
      self.model().setHeaderData(logicalIndex,
                                 QtCore.Qt.Horizontal,
                                 newSortOrder,
                                 HorizontalHeaderItem.SortOrderRole)
    self.__mousePressed = False
    self.__resizing = False
    self.__moving = False
    super(StandardHeaderView, self).mouseReleaseEvent(event)


  def __sectionMoved(self, logicalIndex, oldVisualIndex, newVisualIndex):
    for column in xrange(0, self.model().columnCount()):
      visualIndex = self.visualIndex(column)
      self.model().setHeaderData(column, QtCore.Qt.Horizontal,
                                 visualIndex,
                                 HorizontalHeaderItem.VisualIndexRole)
    

  def mousePressEvent(self, event):
    self.__mousePressed = True
    logicalIndex = self.logicalIndexAt(event.pos())
    if logicalIndex == -1 or self.isSectionHidden(logicalIndex):
      super(StandardHeaderView, self).mousePressEvent(event)
      return
    sectionSize = self.sectionSize(logicalIndex)
    position = event.pos()
    sectionPosition = self.sectionViewportPosition(logicalIndex)
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
    super(StandardHeaderView, self).mousePressEvent(event)


  def mouseDoubleClickEvent(self, event):
    index = self.logicalIndexAt(event.pos())
    if index == 0:
      return
    super(StandardHeaderView, self).mouseDoubleClickEvent(event)


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
    elif not self.__frozen and not self.__resizing and visualIndex <= len(self.__pinnedColumns):
      return
    elif self.__frozen and not self.__resizing:
      headerType = self.model().headerData(logicalIndex,
                                            QtCore.Qt.Horizontal,
                                            HorizontalHeaderItem.DataTypeRole)
      if visualIndex > len(self.__pinnedColumns):
        return
      elif headerType == HorizontalHeaderItem.CheckedType:
        return
      else:
        self.__moving = True
    else:
      self.__moving = True
    super(StandardHeaderView, self).mouseMoveEvent(event)


  def pinnedColumnsCount(self):
    return len(self.__pinnedColumns)


  # Logical indexes are more stable than visual indexes. Methods only work
  # with logical indexes and call visualIndex to move section
  def __columnPinStateChanged(self, logicalIndex, pinState):
    visualIndex = self.visualIndex(logicalIndex)
    if pinState == HorizontalHeaderItem.Pinned:
      if logicalIndex in self.__pinnedColumns:
        return
      # pinned columns is append to existing ones
      self.moveSection(visualIndex, len(self.__pinnedColumns))
      self.__pinnedColumns.append(logicalIndex)
    elif pinState == HorizontalHeaderItem.Unpinned:
      if logicalIndex not in self.__pinnedColumns:
        return
      # pinned columns is append to existing ones
      self.moveSection(visualIndex, len(self.__pinnedColumns)-1)
      self.__pinnedColumns.remove(logicalIndex)
    else:
      return

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


from qtpy import QtCore, QtGui, QtWidgets
from core.standarditems import HorizontalHeaderItem
from core.standardmodels import HorizontalHeaderProxyModel
from core.standardwidgets import FilterWidgetFactory


class SelectionMenu(QtWidgets.QMenu):

  SelectAll = 0
  DeselectAll = 1
  ClearAll = 2

  def __init__(self, parent=None):
    super(SelectionMenu, self).__init__(parent)
    selectAllAction = QtWidgets.QAction(self.tr("Select all items"), self)
    selectAllAction.setData(SelectionMenu.SelectAll)
    self.addAction(selectAllAction)
    deselectAllAction = QtWidgets.QAction(self.tr("Deselect all items"), self)
    deselectAllAction.setData(SelectionMenu.DeselectAll)
    self.addAction(deselectAllAction)
    clearSelectionAction = QtWidgets.QAction(self.tr("Clear all selected items"), self)
    clearSelectionAction.setData(SelectionMenu.ClearAll)
    self.addAction(clearSelectionAction)


class ScreenshotMenu(QtWidgets.QMenu):
  def __init__(self, parent):
    super(ScreenshotMenu, self).__init__(parent)
    screenshotToClipboard = QtWidgets.QAction(self.tr("To clipboard"), self)
    keySequence = QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.ALT + QtCore.Qt.Key_C)
    screenshotToClipboard.setShortcuts(keySequence)
    screenshotToClipboard.setShortcutContext(QtCore.Qt.WidgetShortcut)
    screenshotToClipboard.triggered.connect(self.__screenshotToClipboard)
    self.addAction(screenshotToClipboard)

    screenshotToFile = QtWidgets.QAction(self.tr("To file"), self)
    keySequence = QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.ALT + QtCore.Qt.Key_S)
    screenshotToFile.setShortcuts(keySequence)
    screenshotToFile.setShortcutContext(QtCore.Qt.WidgetShortcut)
    screenshotToFile.triggered.connect(self.__screenshotToFile)
    self.addAction(screenshotToFile)

    screenshotToReport = QtWidgets.QAction(self.tr("To report"), self)
    keySequence = QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.ALT + QtCore.Qt.Key_P)
    screenshotToReport.setShortcuts(keySequence)
    screenshotToReport.setShortcutContext(QtCore.Qt.WidgetShortcut)
    screenshotToReport.triggered.connect(self.__screenshotToReport)
    screenshotToReport.setEnabled(False)
    self.addAction(screenshotToReport)

  def __screenshot(self):
    pixmap = QtGui.QPixmap(self.parent().size())
    self.parent().render(pixmap)
    return pixmap.toImage()

  def __screenshotToClipboard(self):
    pixmap = self.__screenshot()
    QtWidgets.QApplication.clipboard().setImage(pixmap)

  # XXX Get temp path on Windows platform
  def __screenshotToFile(self):
    screenshot = self.__screenshot()
    imageFile = QtWidgets.QFileDialog.getSaveFileName(self, self.tr("Save screenshot to file"),
                                                  "/tmp/screenshot.jpg",
                                                  self.tr("Images (*.png *.jpg)"))
    screenshot.save(imageFile[0])

  def __screenshotToReport(self):
    pass


class ExportMenu(QtWidgets.QMenu):
  def __init__(self, parent=None):
    super(ExportMenu, self).__init__(parent)
    exportDataAction = QtWidgets.QAction(self.tr("data"), self)
    self.addAction(exportDataAction)
    exportCsvAction = QtWidgets.QAction(self.tr("csv"), self)
    self.addAction(exportCsvAction)


class StandardTreeMenu(QtWidgets.QMenu):
  def __init__(self, parent=None):
    super(StandardTreeMenu, self).__init__(parent)
    self.addAction(expandAction)
    self.addAction(collapseAction)
    selectionActions = QtWidgets.QAction(self.tr("Selection"), self)
    selectionMenu = SelectionMenu(self)
    selectionActions.setMenu(selectionMenu)
    self.addAction(selectionActions)
    exportActions = QtWidgets.QAction(self.tr("Export"), self)
    exportMenu = ExportMenu(self)
    exportActions.setMenu(exportMenu)
    self.addAction(exportActions)
    self.addAction(childrenCountAction)


class ViewAppearanceMenu(QtWidgets.QMenu):

  Details = 1
  List = 2
  Icon64 = 64
  Icon128 = 128
  Icon256 = 256
  Icon512 = 512

  viewActionChanged = QtCore.Signal(int)
  
  def __init__(self, parent=None):
    super(ViewAppearanceMenu, self).__init__(parent)
    action = self.addAction(self.tr("Extra large icons"))
    action.setData(ViewAppearanceMenu.Icon512)
    action = self.addAction(self.tr("Large icons"))
    action.setData(ViewAppearanceMenu.Icon256)
    action = self.addAction(self.tr("Medium icons"))
    action.setData(ViewAppearanceMenu.Icon128)
    action = self.addAction(self.tr("Small icons"))
    action.setData(ViewAppearanceMenu.Icon64)
    self.addSeparator()
    action = self.addAction(self.tr("List"))
    action.setData(ViewAppearanceMenu.List)
    self.addSeparator()
    action = self.addAction(self.tr("Details"))
    action.setData(ViewAppearanceMenu.Details)
    self.setActiveAction(action)

  def setCheckable(self, checkable):
    for action in self.actions():
      action.setCheckable(checkable)
    if checkable:
      self.triggered.connect(self.__actionTriggered)
      self.activeAction().setChecked(True)
    else:
      self.triggered.disconnect(self.__actionTriggered)

  def __actionTriggered(self, currentAction):
    for action in self.actions():
        action.setChecked(False)
    currentAction.setChecked(True)

class Slider(QtWidgets.QSlider):

  sliderPositionChanged = QtCore.Signal(int)

  def __init__(self, parent=None):
    super(Slider, self).__init__(parent)
    self.setContentsMargins(0, 0, 0, 0)

  def mouseMoveEvent(self, event):
    self.sliderPositionChanged.emit(event.y())
    

class ViewAppearanceSliderMenu(QtWidgets.QWidget):

  viewActionChanged = QtCore.Signal(int)

  def __init__(self, parent=None):
    super(ViewAppearanceSliderMenu, self).__init__(parent)
    self.__menu = ViewAppearanceMenu()
    self.__menu.setStyleSheet("QMenu {border: 0px;} QMenu::item:selected{background-color: transparent;}")
    self.__menu.triggered.connect(self.__actionTriggered)
    self.__slider = Slider()
    self.__slider.sliderPositionChanged.connect(self.__sliderPositionChanged)
    self.__slider.setInvertedAppearance(True)
    self.__actionIndex = 0
    self.__sliderPosition = 0
    count = 0
    for action in self.__menu.actions():
      if not action.isSeparator():
        count += 1
    self.setContentsMargins(0, 0, 0, 0)
    self.setLayout(QtWidgets.QHBoxLayout())
    self.layout().setContentsMargins(0, 0, 0, 0)
    self.layout().addWidget(self.__slider)
    self.layout().addWidget(self.__menu)

  def __actionAt(self, yPosition):
    actions = self.__menu.actions()
    foundAction = None
    foundGeom = None
    for action in actions:
      geom = self.__menu.actionGeometry(action)
      if yPosition >= geom.top() and yPosition <= geom.bottom():
        foundAction = action
        foundGeom = geom
    if foundAction is None:
      return (None, -1)
    index = actions.index(foundAction)
    if foundAction.isSeparator():
      if index > 0 and index < len(actions) - 1:
        if yPosition < foundGeom.center().y():
          index -= 1
          foundAction = actions[index]
        else:
          index += 1
          foundAction = actions[index]
    return (foundAction, index)

  def __updateSliderPosition(self, action, index):
    if action is None:
      return
    y = self.__menu.actionGeometry(action).center().y()
    self.__slider.setSliderPosition(y)
    self.__menu.setActiveAction(action)
    data = action.data()
    if data is None:
      return
    viewType = data
    if not viewType:
      return
    self.viewActionChanged.emit(viewType)

  def __sliderPositionChanged(self, yPosition):
    action, index = self.__actionAt(yPosition)
    self.__updateSliderPosition(action, index)

  def showEvent(self, event):
    super(ViewAppearanceSliderMenu, self).showEvent(event)
    firstAction = self.__menu.actions()[0]
    lastAction =  self.__menu.actions()[-1]
    firstGeometry = self.__menu.actionGeometry(firstAction)
    lastGeometry = self.__menu.actionGeometry(lastAction)
    self.__slider.setMinimum(firstGeometry.center().y())
    self.__slider.setMaximum(lastGeometry.center().y())
    height = (lastGeometry.center().y() + 3) - (firstGeometry.center().y() - 3)
    self.__slider.setGeometry(self.__slider.x(),
                              firstGeometry.center().y() - 3,
                              self.__slider.width(),
                              height + 3)
    activeAction = self.__menu.activeAction()
    if activeAction is not None:
      sliderPosition = self.__menu.actionGeometry(activeAction).center().y()
      self.__slider.setSliderPosition(sliderPosition)

  def __actionTriggered(self, action):
    if action is None:
      return
    data = action.data()
    if data is None:
      return
    viewType = data
    if not viewType:
      return
    index = self.__menu.actions().index(action)
    self.__updateSliderPosition(action, index)
    self.viewActionChanged.emit(viewType)
    self.hide()

  def setCurrentViewAction(self, viewActionData):
    sliderPosition = -1
    for action in self.__menu.actions():
      if action.data() == viewActionData:
        self.__menu.setActiveAction(action)
        sliderPosition = self.__menu.actionGeometry(action).center().y()
    if sliderPosition != -1:
      self.__slider.setSliderPosition(sliderPosition)


class HorizontalHeaderSettingMenu(QtWidgets.QMenu):
    def __init__(self, model, index, parent=None):
        QtWidgets.QMenu.__init__(self, parent)
        self.__model = model
        self.__index = index
        pinState = self.__model.headerData(self.__index, QtCore.Qt.Horizontal,
                                           HorizontalHeaderItem.PinRole)
        if pinState is None:
            return
        if pinState != HorizontalHeaderItem.ForcePinned:
            self.__pinAction = self.addAction(self.tr("Pin"), self.__pin)
            self.__pinAction.setCheckable(True)
            self.__unpinAction = self.addAction(self.tr("Unpin"), self.__unpin)
            self.__unpinAction.setCheckable(True)
            if pinState == HorizontalHeaderItem.Pinned:
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
        if pinState == HorizontalHeaderItem.Pinned \
           or pinState == HorizontalHeaderItem.ForcePinned:
            self.__pinAction.setChecked(True)
            self.__unpinAction.setChecked(False)
        else:
            self.__pinAction.setChecked(False)
            self.__unpinAction.setChecked(True)
        

    def __pin(self):
        hdata = self.__model.headerData(self.__index,
                                        QtCore.Qt.Horizontal,
                                        HorizontalHeaderItem.PinRole)
        pinState = hdata
        if pinState and pinState == HorizontalHeaderItem.Unpinned and self.__unpinAction.isChecked():
            self.__model.setHeaderData(self.__index, QtCore.Qt.Horizontal,
                                       HorizontalHeaderItem.Pinned,
                                       HorizontalHeaderItem.PinRole)
        self.__pinAction.setChecked(True)
        self.__unpinAction.setChecked(False)
        self.emit(QtCore.SIGNAL("settingClicked()"))


    def __unpin(self):
        hdata = self.__model.headerData(self.__index,
                                        QtCore.Qt.Horizontal,
                                        HorizontalHeaderItem.PinRole)
        pinState = hdata
        if pinState and pinState == HorizontalHeaderItem.Pinned and self.__pinAction.isChecked():
            self.__model.setHeaderData(self.__index, QtCore.Qt.Horizontal,
                                       HorizontalHeaderItem.Unpinned,
                                       HorizontalHeaderItem.PinRole)
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


class HorizontalHeaderMenuTabBar(QtWidgets.QTabBar):
    def __init__(self, parent):
        super(HorizontalHeaderMenuTabBar, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)


    def mousePressEvent(self, event):
        index = self.tabAt(event.pos())
        if index == -1 or index == self.currentIndex():
            self.emit(QtCore.SIGNAL("close()"))
        super(HorizontalHeaderMenuTabBar, self).mousePressEvent(event)


class HorizontalHeaderMenu(QtWidgets.QTabWidget):
    def __init__(self, model, index, parent=None):
        QtWidgets.QTabWidget.__init__(self, parent)
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
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                           QtWidgets.QSizePolicy.Preferred)
        tabBar = HorizontalHeaderMenuTabBar(self)
        self.setTabBar(tabBar)
        self.__initSettingsMenu()
        self.__initFilterWidget()
        # self.connect(tabBar, QtCore.SIGNAL("close()"), self.hide)
        # self.connect(self.__model,
        #              QtCore.SIGNAL("columnPinStateChanged(int, int)"),
        #              self.__updatePinState)
        # self.connect(self.__model,
        #              QtCore.SIGNAL("filterChanged(int, QString)"),
        #              self.__filterChanged)
        # self.connect(self.__model,
        #              QtCore.SIGNAL("filterEnabled(int, QString)"),
        #              self.__filterChanged)
        # self.connect(self.__settingsMenu, QtCore.SIGNAL("settingClicked()"),
        #              self.hide)
        # self.currentChanged.connect(self.__updateTabSize)
        self.hide()


    def __initFilterWidget(self):
        columnType = self.__model.headerData(self.__index,
                                                      QtCore.Qt.Horizontal,
                                                      HorizontalHeaderItem.DataTypeRole)
        if columnType is None:
            return
        attributeName = self.__model.headerData(self.__index,
                                                QtCore.Qt.Horizontal,
                                                HorizontalHeaderItem.AttributeNameRole)
        proxyModel = HorizontalHeaderProxyModel(self.__model)
        self.__filterWidget = FilterWidgetFactory(columnType, attributeName,
                                                  parent=self)
        if self.__filterWidget is not None:
            #self.connect(self.__filterWidget, QtCore.SIGNAL("filterChanged(QString)"),
            #             self.__setFilter)
            self.addTab(self.__filterWidget, QtGui.QIcon(":column_filter"), "")


    def __setFilter(self, queryString):
        self.__model.setHeaderData(self.__index, QtCore.Qt.Horizontal,
                                   queryString,
                                   HorizontalHeaderItem.FilterDataRole)


    def __initSettingsMenu(self):
        self.__settingsMenu = HorizontalHeaderSettingMenu(self.__model,
                                                          self.__index, self)
        self.__settingsMenu.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                                          QtWidgets.QSizePolicy.Ignored)
        self.addTab(self.__settingsMenu, QtGui.QIcon(":column_settings"), "")


    def mousePressEvent(self, event):
        super(HorizontalHeaderMenu, self).mousePressEvent(event)
        self.__updateTabSize(self.currentIndex())
        self.emit(QtCore.SIGNAL("menuClosed()"))
        self.hide()
        
        
    def show(self):
        super(HorizontalHeaderMenu, self).show()
        self.__updateTabSize(self.currentIndex())


    def __updatePinState(self, index, pinState):
        if index != self.__index:
            return
        self.__settingsMenu.setPinState(pinState)


    def __filterChanged(self, index, query):
        if self.isVisible():
            self.__updateTabSize(self.currentIndex())
            return
        if self.__filterWidget is None or index != self.__index:
            return
        self.__filterWidget.setFilter(str(query.toUtf8()))


    def __updateTabSize(self, index):
        for idx in range(0, self.count()):
            if idx != index:
                _widget = self.widget(idx)
                _widget.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                                      QtWidgets.QSizePolicy.Ignored)
        widget = self.widget(index)
        if widget is None:
            return
        widget.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                             QtWidgets.QSizePolicy.Preferred)
        widget.resize(widget.minimumSizeHint())
        widget.adjustSize()
        self.resize(widget.size())
        self.adjustSize()

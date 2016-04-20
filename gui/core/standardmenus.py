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
from dff.ui.gui.core.standarditems import HorizontalHeaderItem
from dff.ui.gui.core.standardmodels import HorizontalHeaderProxyModel
from dff.ui.gui.core.standardwidgets import FilterWidgetFactory


class HorizontalHeaderSettingMenu(QtGui.QMenu):
    def __init__(self, model, index, parent=None):
        QtGui.QMenu.__init__(self, parent)
        self.__model = model
        self.__index = index
        pinState, success = self.__model.headerData(self.__index, QtCore.Qt.Horizontal,
                                           HorizontalHeaderItem.PinRole).toInt()
        if not success:
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
        pinState, success = hdata.toInt()
        if success and pinState == HorizontalHeaderItem.Unpinned and self.__unpinAction.isChecked():
            self.__model.setHeaderData(self.__index, QtCore.Qt.Horizontal,
                                       QtCore.QVariant(HorizontalHeaderItem.Pinned),
                                       HorizontalHeaderItem.PinRole)
        self.__pinAction.setChecked(True)
        self.__unpinAction.setChecked(False)
        self.emit(QtCore.SIGNAL("settingClicked()"))


    def __unpin(self):
        hdata = self.__model.headerData(self.__index,
                                        QtCore.Qt.Horizontal,
                                        HorizontalHeaderItem.PinRole)
        pinState, success = hdata.toInt()
        if success and pinState == HorizontalHeaderItem.Pinned and self.__pinAction.isChecked():
            self.__model.setHeaderData(self.__index, QtCore.Qt.Horizontal,
                                       QtCore.QVariant(HorizontalHeaderItem.Unpinned),
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



class HorizontalHeaderMenuTabBar(QtGui.QTabBar):
    def __init__(self, parent):
        super(HorizontalHeaderMenuTabBar, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)


    def mousePressEvent(self, event):
        index = self.tabAt(event.pos())
        if index == -1 or index == self.currentIndex():
            self.emit(QtCore.SIGNAL("close()"))
        super(HorizontalHeaderMenuTabBar, self).mousePressEvent(event)


class HorizontalHeaderMenu(QtGui.QTabWidget):
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
        tabBar = HorizontalHeaderMenuTabBar(self)
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
        self.connect(self.__model,
                     QtCore.SIGNAL("filterEnabled(int, QString)"),
                     self.__filterChanged)
        self.connect(self.__settingsMenu, QtCore.SIGNAL("settingClicked()"),
                     self.hide)
        self.currentChanged.connect(self.__updateTabSize)
        self.hide()


    def __initFilterWidget(self):
        columnType, success = self.__model.headerData(self.__index,
                                                      QtCore.Qt.Horizontal,
                                                      HorizontalHeaderItem.DataTypeRole).toInt()
        if not success:
            return
        attributeName = self.__model.headerData(self.__index,
                                                QtCore.Qt.Horizontal,
                                                HorizontalHeaderItem.AttributeNameRole).toString()
        proxyModel = HorizontalHeaderProxyModel(self.__model)
        self.__filterWidget = FilterWidgetFactory(columnType, attributeName,
                                                  parent=self)
        if self.__filterWidget is not None:
            self.connect(self.__filterWidget, QtCore.SIGNAL("filterChanged(QString)"),
                         self.__setFilter)
            self.addTab(self.__filterWidget, QtGui.QIcon(":column_filter"), "")


    def __setFilter(self, queryString):
        self.__model.setHeaderData(self.__index, QtCore.Qt.Horizontal,
                                   QtCore.QVariant(queryString),
                                   HorizontalHeaderItem.FilterDataRole)


    def __initSettingsMenu(self):
        self.__settingsMenu = HorizontalHeaderSettingMenu(self.__model,
                                                          self.__index, self)
        self.__settingsMenu.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                          QtGui.QSizePolicy.Ignored)
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

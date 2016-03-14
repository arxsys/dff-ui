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
from dff.ui.gui.nodes.nodestablemodel import NodesTableHeaderItem


def FilterWidgetFactory(attributeType, attributeName, layoutOrientation=QtCore.Qt.Vertical, parent=None):
    if attributeType == NodesTableHeaderItem.NameType:
        return NodesNameFilterWidget(layoutOrientation, parent)
    if attributeType == NodesTableHeaderItem.SizeType:
        return NodesSizeFilterWidget(layoutOrientation, parent)
    if attributeType == NodesTableHeaderItem.DataType:
        return None
    if attributeType == NodesTableHeaderItem.TagType:
        return None
    if attributeType == NodesTableHeaderItem.TimeType:
        return None
    if attributeType == NodesTableHeaderItem.NumberType:
        return NodesNumberFilterWidget(attributeName, layoutOrientation, parent)
    if attributeType == NodesTableHeaderItem.StringType:
        return NodesStringFilterWidget(attributeName, layoutOrientation, parent)
    return None


class NodesAbstractFilterWidget(QtGui.QWidget):
    def __init__(self, layoutOrientation=QtCore.Qt.Vertical, parent=None):
        QtGui.QWidget.__init__(self, parent)
        if layoutOrientation == QtCore.Qt.Vertical:
            layout = QtGui.QVBoxLayout(self)
        else:
            layout = QtGui.QHBoxLayout(self)
        layout.setSpacing(3)
        layout.setContentsMargins(3, 3, 3, 3)
        self.setLayout(layout)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)


class NodesNumberAbstractFilterWidget(NodesAbstractFilterWidget):
    def __init__(self, attributeName, layoutOrientation=QtCore.Qt.Vertical, parent=None):
        NodesAbstractFilterWidget.__init__(self, layoutOrientation, parent)
        self.__attributeName = attributeName
        self.__comparisonOperator = QtGui.QComboBox(self)
        self.__comparisonOperator.insertItem(0, self.tr("Equals to"))
        self.__comparisonOperator.insertItem(1, self.tr("Not equals to"))
        self.__comparisonOperator.insertItem(2, self.tr("Less than to"))
        self.__comparisonOperator.insertItem(3, self.tr("Less than or equals to"))
        self.__comparisonOperator.insertItem(4, self.tr("Greater than to"))
        self.__comparisonOperator.insertItem(5, self.tr("Greater than or equals to"))
        self.layout().addWidget(self.__comparisonOperator)
        self._number = QtGui.QLineEdit(self)
        self._number.setPlaceholderText(self.tr("Number..."))
        self._number.textChanged.connect(self._filterChanged)
        self.connect(self.__comparisonOperator,
                     QtCore.SIGNAL("currentIndexChanged(const QString &)"),
                     self._filterChanged)
        
        
    # Not implemented
    # This method must be overloaded when inherited and called in __init__
    def _manageNumberLayout(self):
        pass 


    def _numberValue(self):
        return self._number.text()
    

    def _comparisonOperator(self):
        comparisonOperator = self.__comparisonOperator.currentText()
        if comparisonOperator == self.tr("Equals to"):
            return "=="
        if comparisonOperator == self.tr("Not equals to"):
            return "!="
        if comparisonOperator == self.tr("Less than"):
            return "<"
        if comparisonOperator == self.tr("Greater than"):
            return ">"
        if comparisonOperator == self.tr("Less than or equals to"):
            return "<="
        if comparisonOperator == self.tr("Greater than or equals to"):
            return ">="


    def _attributeName(self):
        attribute = "@{}@".format(self._attributeName)
        return attribute


    def _filterChanged(self, value):
        query = "{} {} {}".format(self._attributeName(),
                                      self._comparisonOperator(),
                                      self._numberValue())
        print("Number filter: {}".format(query))
        self.emit(QtCore.SIGNAL("filterChanged(QString)"), query) 


class NodesNumberFilterWidget(NodesNumberAbstractFilterWidget):
    def __init__(self, attributeName, layoutOrientation=QtCore.Qt.Vertical, parent=None):
        NodesNumberAbstractFilterWidget.__init__(self, attributeName, layoutOrientation, parent)
        self._manageNumberLayout()


    def _manageNumberLayout(self):
        self.layout().addWidget(self._number)

        
class NodesSizeFilterWidget(NodesNumberAbstractFilterWidget):
    def __init__(self, layoutOrientation=QtCore.Qt.Vertical, parent=None):
        NodesNumberAbstractFilterWidget.__init__(self, "", layoutOrientation, parent)
        self.__sizeUnit = QtGui.QComboBox(self)
        self.__sizeUnit.insertItem(0, self.tr("Bytes"))
        self.__sizeUnit.insertItem(1, self.tr("KiB"))
        self.__sizeUnit.insertItem(2, self.tr("MiB"))
        self.__sizeUnit.insertItem(3, self.tr("GiB"))
        self.__sizeUnit.insertItem(4, self.tr("TiB"))
        self.__sizeUnit.insertItem(5, self.tr("PiB"))
        self.__sizeUnit.insertItem(6, self.tr("EiB"))
        self.connect(self.__sizeUnit,
                     QtCore.SIGNAL("currentIndexChanged(const QString &)"),
                     self._filterChanged)
        self._number.setPlaceholderText(self.tr("Size..."))
        self._manageNumberLayout()


    def _manageNumberLayout(self):
        sizeLayout = QtGui.QHBoxLayout()
        sizeLayout.addWidget(self._number)
        sizeLayout.addWidget(self.__sizeUnit)
        self.layout().addLayout(sizeLayout)


    def _numberValue(self):
        number, success = self._number.text().toULongLong()
        if success:
            sizeUnit = self.__sizeUnit.currentText()
            if sizeUnit == self.tr("Bytes"):
                return number
            if sizeUnit == self.tr("KiB"):
                return number * 1024
            if sizeUnit == self.tr("MiB"):
                return number * (1024**2)
            if sizeUnit == self.tr("GiB"):
                return number * (1024**3)
            if sizeUnit == self.tr("TiB"):
                return number * (1024**4)
            if sizeUnit == self.tr("PiB"):
                return number * (1024**5)
            if sizeUnit == self.tr("EiB"):
                return number * (1024**6)
        return 0

    
    def _filterChanged(self, value):
        query = "size {} {}".format(self._comparisonOperator(),
                                    self._numberValue())
        print("Size filter: {}".format(query))
        self.emit(QtCore.SIGNAL("filterChanged(QString)"), query) 


class NodesStringFilterWidget(NodesAbstractFilterWidget):
    def __init__(self, attributeName, layoutOrientation=QtCore.Qt.Vertical, parent=None):
        NodesAbstractFilterWidget.__init__(self, layoutOrientation, parent)
        self.__attributeName = attributeName
        self.__comparisonOperator = QtGui.QComboBox(self)
        self.__comparisonOperator.insertItem(0, self.tr("Contains"))
        self.__comparisonOperator.insertItem(1, self.tr("Equals"))
        self.__patternType = QtGui.QComboBox(self)
        self.__patternType.insertItem(0, self.tr("Fixed"))
        self.__patternType.insertItem(1, self.tr("RegExp"))
        self.__patternType.insertItem(2, self.tr("Wildcard"))
        self.__pattern = QtGui.QLineEdit(self)
        self.__pattern.setPlaceholderText(self.tr("Filter..."))
        self.__pattern.textChanged.connect(self._filterChanged)
        self.connect(self.__comparisonOperator,
                     QtCore.SIGNAL("currentIndexChanged(const QString &)"),
                     self._filterChanged)
        self.connect(self.__patternType,
                     QtCore.SIGNAL("currentIndexChanged(const QString &)"),
                     self._filterChanged)
        self.layout().addWidget(self.__comparisonOperator)
        self.layout().addWidget(self.__patternType)
        self.layout().addWidget(self.__pattern)


    def _patternDecorator(self):
        patternType = self.__patternType.currentText()
        if patternType == self.tr("Fixed"):
            return '"'
        if patternType == self.tr("RegExp"):
            return '/'
        if patternType == self.tr("Wildcard"):
            return '$'


    def _comparisonOperator(self):
        comparisonOperator = self.__comparisonOperator.currentText()
        if comparisonOperator == self.tr("Contains"):
            return "matches"
        if comparisonOperator == self.tr("Equals"):
            return "=="


    def _attributeName(self):
        attribute = "@{}@".format(self.__attributeName)
        return attribute


    def _pattern(self):
        pattern = self.__pattern.text()
        

    # XXX UTF 8
    def _filterChanged(self, value):
        query = "{} {} {}{}{}".format(self._attributeName(), self._comparisonOperator(),
                                      self._patternDecorator(), self._pattern(),
                                      self._patternDecorator())
        print("String filter: {}".format(query))        
        self.emit(QtCore.SIGNAL("filterChanged(QString)"), query) 


class NodesNameFilterWidget(NodesStringFilterWidget):
    def __init__(self, layoutOrientation=QtCore.Qt.Vertical, parent=None):
        NodesStringFilterWidget.__init__(self, "", layoutOrientation, parent)


    def _filterChanged(self, value):
        query = "name {} {}{}{}".format(self._comparisonOperator(),
                                      self._patternDecorator(), self._pattern(),
                                      self._patternDecorator())
        print("Name filter: {}".format(query))        
        self.emit(QtCore.SIGNAL("filterChanged(QString)"), query)



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


import re

from qtpy import QtCore, QtGui, QtWidgets
from core.standarditems import HorizontalHeaderItem


class ScrollableLabel(QtWidgets.QLabel):
  def __init__(self, text, parent=None):
    super(ScrollableLabel, self).__init__(text, parent)
    self.__pressed = False
    self.__originalText = text
    fm = QtGui.QApplication.instance().fontMetrics()
    self.__textWidth = fm.width(self.__originalText)
    self.__cursorPosition = 0
    self.__textPosition = 0


  def mousePressEvent(self, event):
    self.__pressed = True
    self.__cursorPosition = event.globalPos()


  def mouseReleaseEvent(self, event):
    self.__pressed = False


  def mouseMoveEvent(self, event):
    if self.__pressed:
      position = event.globalPos()
      # going left
      if position.x() < self.__cursorPosition.x():
        if self.__textPosition > 0:
          self.__textPosition -= 1
      # going right
      else:
        subText = self.__originalText.mid(self.__textPosition)
        width = QtGui.QApplication.instance().fontMetrics().width(subText)
        if self.size().width() < width:
          self.__textPosition += 1
      self.setText(self.__originalText.mid(self.__textPosition))


def FilterWidgetFactory(attributeType, attributeName,
                        orientation=QtCore.Qt.Vertical, parent=None):
  if attributeType == HorizontalHeaderItem.NumberType:
    widget = ComparisonFilterWidget(attributeName, orientation, parent)
    widget.setValueWidgets(NumberWidget(widget), NumberWidget(widget))
    return widget
  if attributeType == HorizontalHeaderItem.SizeType:
    widget = ComparisonFilterWidget(attributeName, orientation, parent)
    widget.setValueWidgets(SizeWidget(widget), SizeWidget(widget))
    return widget
  if attributeType == HorizontalHeaderItem.StringType:
    return StringFilterWidget(attributeName, orientation, parent)
  if attributeType == HorizontalHeaderItem.DataType:
    return None
  if attributeType == HorizontalHeaderItem.TagType:
    return None
  if attributeType == HorizontalHeaderItem.TimeType:
    widget = ComparisonFilterWidget(attributeName, orientation, parent)
    #self.setValueWidgets(TimeWidget(widget), TimeWidget(widget))
    #return widget
  return None


class ComparisonWidget(QtWidgets.QComboBox):
  def __init__(self, parent=None):
    super(ComparisonWidget, self).__init__(parent)
    self.setFrame(False)
    self.insertItem(0, self.tr("Equals to"), "==")
    self.insertItem(1, self.tr("Not equals to"), "!=")
    self.insertItem(2, self.tr("Less than"), "<")
    self.insertItem(3, self.tr("Less than or equals to"), "<=")
    self.insertItem(4, self.tr("Greater than"), ">")
    self.insertItem(5, self.tr("Greater than or equals to"), ">=")
    self.insertItem(6, self.tr("Between ... And ..."), "ba")
    self.insertItem(7, self.tr("In the following list"), "in")

        
  def setOperator(self, operator):
    idx = self.findData(operator)
    if idx == -1:
        return
    self.setCurrentIndex(idx)
        

  def operator(self):
    idx = self.currentIndex()
    return self.itemData(idx)


class NumberWidget(QtWidgets.QLineEdit):
  def __init__(self, parent=None):
    super(NumberWidget, self).__init__(parent)
    self.setFrame(False)
    self.__rhs = False
    self.textEdited.connect(self.__numberChanged)
    if self.__rhs:
      self.hide()


  def setRhs(self, rhs):
    self.__rhs = rhs
    if self.__rhs:
      self.hide()


  def isRhs(self):
    return self.__rhs == True


  def setSinglePlaceholder(self):
    if self.__rhs:
      self.clear()
      self.hide()
    else:
      self.setPlaceholderText(self.tr("Number..."))


  def setIntervalPlaceholder(self):
    if self.__rhs:
      self.setPlaceholderText(self.tr("And Number..."))
      self.show()
    else:
      self.setPlaceholderText(self.tr("Between Number..."))


  def setListPlaceholder(self):
    if self.__rhs:
      self.clear()
      self.hide()
    else:
      self.setPlaceholderText(self.tr("Comma separated Numbers..."))


  def __numberChanged(self, text):
    self.emit(QtCore.SIGNAL("valueChanged()"))


  def setValue(self, value):
    self.setText(value)
        

  def value(self):
    return self.text()


class SizeWidget(QtWidgets.QWidget):
  def __init__(self, parent=None):
    super(SizeWidget, self).__init__(parent)
    self.__rhs = False
    self.setContentsMargins(0, 0, 0, 0)
    layout = QtWidgets.QHBoxLayout()
    self.setLayout(layout)
    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)
    self.__size = QtWidgets.QLineEdit()
    self.__size.setFrame(False)
    self.__size.textEdited.connect(self.__sizeChanged)
    self.__sizeUnit = QtWidgets.QComboBox(self)
    self.__sizeUnit.setFrame(False)
    self.__sizeUnit.insertItem(0, self.tr("Bytes"))
    self.__sizeUnit.insertItem(1, self.tr("KiB"))
    self.__sizeUnit.insertItem(2, self.tr("MiB"))
    self.__sizeUnit.insertItem(3, self.tr("GiB"))
    self.__sizeUnit.insertItem(4, self.tr("TiB"))
    self.__sizeUnit.insertItem(5, self.tr("PiB"))
    self.__sizeUnit.insertItem(6, self.tr("EiB"))
    self.__sizeUnit.activated.connect(self.__sizeChanged)
    layout.addWidget(self.__size)
    layout.addWidget(self.__sizeUnit)
    if self.__rhs:
      self.hide()


  def setRhs(self, rhs):
    self.__rhs = rhs
    if self.__rhs:
      self.hide()


  def isRhs(self):
    return self.__rhs == True
    

  def setSinglePlaceholder(self):
    if self.__rhs:
      self.__size.clear()
      self.hide()
    else:
      self.__size.setPlaceholderText(self.tr("Size..."))


  def setIntervalPlaceholder(self):
    if self.__rhs:
      self.__size.setPlaceholderText(self.tr("And Size..."))
      self.show()
    else:
      self.__size.setPlaceholderText(self.tr("Between Size..."))


  def setListPlaceholder(self):
    if self.__rhs:
      self.__size.clear()
      self.hide()
    else:
      self.__size.setPlaceholderText(self.tr("Comma separated Sizes..."))


  def setValue(self, size):
    if not len(size):
      return
    match = re.compile("([0-9]*)(KiB|MiB|GiB|TiB|PiB|EiB)?").match(size)
    size = match.group(1)
    unit = match.group(2)
    if size is None:
      return
    idx = 0
    if unit is not None:
      idx = self.__sizeUnit.findText(unit)
      if idx == -1:
        idx = 0
    self.__sizeUnit.setCurrentIndex(idx)
    self.__size.setText(size)


  def value(self):
    size = str(self.__size.text())
    if not len(size):
      return ""
    sizeUnit = str(self.__sizeUnit.currentText())
    if sizeUnit != self.tr("Bytes"):
      size = size+sizeUnit
    return size


  def __sizeChanged(self, value):
    self.emit(QtCore.SIGNAL("valueChanged()"))


class StringWidget(QtWidgets.QWidget):
  def __init__(self, parent=None):
    super(StringWidget, self).__init__(parent)
    self.setContentsMargins(0, 0, 0, 0)
    layout = QtWidgets.QHBoxLayout()
    self.setLayout(layout)
    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)
    # manage startswith, endswith, contains, equals
    self.__pattern = QtWidgets.QLineEdit()
    self.__pattern.setFrame(False)
    self.__pattern.textEdited.connect(self.__patternChanged)
    self.__pattern.setPlaceholderText("Pattern...")
    self.__patternType = QtWidgets.QComboBox(self)
    self.__patternType.setFrame(False)
    self.__patternType.insertItem(0, self.tr("Fixed"), '"')
    self.__patternType.insertItem(1, self.tr("RegExp"), '/')
    self.__patternType.insertItem(2, self.tr("Wildcard"), '$')
    self.__patternType.insertItem(3, self.tr("Approximative"), ('~'))
    self.__patternType.activated.connect(self.__patternChanged)
    layout.addWidget(self.__pattern)
    layout.addWidget(self.__patternType)


  def setValue(self, pattern):
    if not len(pattern):
      return
    idx = -1
    for decorator in ['"', "/", "$", "~"]:
      if pattern.startswith(decorator) and pattern.endswith(decorator):
        idx = self.__patternType.findText(decorator)
        break
    if idx == -1:
      return
    self.__patternType.setCurrentIndex(idx)
    self.__pattern.setText(pattern[1:-1])


  def value(self):
    text = self.__pattern.text()
    if not len(text):
      return ""
    idx = self.__patternType.currentIndex()
    pattern = "{}{}{}".format(self.__patternType.itemData(idx),
                              self.__pattern.text(),
                              self.__patternType.itemData(idx))
    return pattern


  def __patternChanged(self, value):
    self.emit(QtCore.SIGNAL("valueChanged()"))


class FilterWidget(QtWidgets.QWidget):
  def __init__(self, attributeName, orientation=QtCore.Qt.Vertical, parent=None):
    self.__attributeName = attributeName
    QtWidgets.QWidget.__init__(self, parent)
    if orientation == QtCore.Qt.Vertical:
      layout = QtWidgets.QVBoxLayout(self)
    else:
      layout = QtWidgets.QHBoxLayout(self)
    layout.setSpacing(3)
    layout.setContentsMargins(3, 3, 3, 3)
    self.setLayout(layout)
    self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)


  def _attributeName(self):
    if self.__attributeName in ["time", "year", "type", "size", "deleted",
                                "folder", "file", "extension", "name",
                                "path", "tags", "tagged", "to", "module"]:
      return self.__attributeName
    else:
      return "@{}@".format(self.__attributeName)


  def __splitExpression(self, expression):
    # attributes can have space in their name, manage it first
    attribute = ""
    comparison = ""
    value = ""
    attributeEndIdx = len(expression)
    if expression.startswith("@"):
      attributeEndIdx = expression[1:].find("@")
      if attributeEndIdx == -1:
        return (attribute, comparison, value)
      attributeEndIdx += 2
      attribute = expression[0:attributeEndIdx].strip()
    else:
      attributeEndIdx = expression.find(" ")
      if attributeEndIdx == -1:
        return (attribute, comparison, value)
      attribute = expression[0:attributeEndIdx]
    expression = expression[attributeEndIdx:].strip()
    if not len(expression):
      return (attribute, comparison, value)
    match = re.compile("(=|!)=|>(=)?|<(=)?|matches|in|").match(expression)
    if match is None:
      return (attribute, comparison, value)
    comparison = match.group()
    value = expression[match.end():].strip()
    return (attribute, comparison, value)


  def _splitFilter(self, _filter):
    andIndex = _filter.find(" and ")
    if andIndex != -1:
      lhs = self.__splitExpression(_filter[:andIndex])
      rhs = self.__splitExpression(_filter[andIndex+5:])
    else:
      lhs = self.__splitExpression(_filter)
      rhs = None
    return (lhs, rhs)


  # Must be overloaded
  def setFilter(self, _filter):
    raise NotImplementedError


class ComparisonFilterWidget(FilterWidget):
  def __init__(self, attributeName,
               orientation=QtCore.Qt.Vertical,
               parent=None):
    super(ComparisonFilterWidget, self).__init__(attributeName,
                                                 orientation, parent)
    self.__comparison = ComparisonWidget(self)
    self.layout().addWidget(self.__comparison)
    self.__comparison.activated.connect(self._filterChanged)
    self.__lhs = None
    self.__rhs = None


  def setValueWidgets(self, lhs, rhs):
    self.__setLhsWidget(lhs)
    self.__setRhsWidget(rhs)
    rhs.setRhs(True)


  def __setLhsWidget(self, widget):
    self.__lhsWidget = widget
    #self.connect(self.__lhsWidget, QtCore.SIGNAL("valueChanged()"),
    #             self._filterChanged)
    self.layout().addWidget(self.__lhsWidget)


  def __setRhsWidget(self, widget):
    self.__rhsWidget = widget
    #self.connect(self.__rhsWidget, QtCore.SIGNAL("valueChanged()"),
    #             self._filterChanged)
    self.layout().addWidget(self.__rhsWidget)


  def setFilter(self, _filter):
    lhs, rhs = self._splitFilter(_filter)
    if rhs is not None:
      self.__comparison.setOperator("ba")
      self.__lhsWidget.setValue(lhs[-1])
      self.__lhsWidget.setIntervalPlaceholder()
      self.__rhsWidget.setValue(rhs[-1])
      self.__rhsWidget.setIntervalPlaceholder()
    else:
      attribute, operator, number = lhs
      self.__comparison.setOperator(operator)
      self.__lhsWidget.setValue(number)
      if operator == "in":
        self.__lhsWidget.setListPlaceholder()
        self.__rhsWidget.setListPlaceholder()
      else:
        self.__lhsWidget.setSinglePlaceholder()
        self.__rhsWidget.setSinglePlaceholder()


  def _filterChanged(self):
    query = ""
    operator = self.__comparison.operator()
    if operator == "ba":
      self.__lhsWidget.setIntervalPlaceholder()
      self.__rhsWidget.setIntervalPlaceholder()
      lhs = "{} >= {}".format(self._attributeName(), self.__lhsWidget.value())
      rhs =  "{} <= {}".format(self._attributeName(), self.__rhsWidget.value())
      query = "{} and {}".format(lhs, rhs)
    elif operator == "in":
      self.__lhsWidget.setListPlaceholder()
      self.__rhsWidget.setListPlaceholder()
      query = "{} in [{}]".format(self._attributeName(),
                                  self.__lhsWidget.value())
    else:
      self.__lhsWidget.setSinglePlaceholder()
      self.__rhsWidget.setSinglePlaceholder()
      query = "{} {} {}".format(self._attributeName(), operator,
                                self.__lhsWidget.value())
      self.emit(QtCore.SIGNAL("filterChanged(QString)"),
                QtCore.QString.fromUtf8(query))


class StringFilterWidget(FilterWidget):
  def __init__(self, attributeName,
               orientation=QtCore.Qt.Vertical,
               parent=None):
    super(StringFilterWidget, self).__init__(attributeName, orientation, parent)
    self.__operator = QtWidgets.QComboBox(self)
    self.__operator.insertItem(0, self.tr("Matches"))
    self.__operator.setFrame(False)
    #self.__operator.insertItem(1, self.tr("In"))
    self.__pattern = StringWidget(self)
    #self.connect(self.__operator,
    #             QtCore.SIGNAL("activated(int)"),
    #             self._filterChanged)
    #self.connect(self.__pattern, QtCore.SIGNAL("valueChanged()"),
    #             self._filterChanged)
    self.layout().addWidget(self.__operator)
    self.layout().addWidget(self.__pattern)


  def setFilter(self, _filter):
    (lhs, rhs) = self._splitFilter(_filter)
    attribute, operator, pattern = lhs
    self.__pattern.setValue(pattern)


  def _operator(self):
    return str(self.__operator.currentText()).lower()


  # XXX UTF 8
  def _filterChanged(self):
    query = "{} {} {}".format(self._attributeName(), self._operator(),
                              self.__pattern.value())
    self.emit(QtCore.SIGNAL("filterChanged(QString)"),
              QtCore.QString.fromUtf8(query))

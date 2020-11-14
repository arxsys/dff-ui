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

from datetime import datetime
import time

from qtpy import QtCore, QtGui

#from dff.api.taskmanager.processus import ProcessusManager 
from core.standarditems import StandardItem


class ProcessusCategory(StandardItem):
  def __init__(self, name, parent):
    super(ProcessusCategory, self).__init__(parent)
    self.__name = name


  def checkableAttribute(self):
    return "name"

    
  def display(self, attribute):
    if attribute == "name":
      name = QtCore.QString.fromUtf8(self.__name)
      return name
    return None


  def sizeHint(self, attribute):
    data = self.display(attribute)
    if data.isValid():
      fm = QtGui.QApplication.instance().fontMetrics()
      width = fm.width(data)
      sizeHint = QtCore.QSize(width+100, 16)
      return sizeHint
    return None


  def displayChildrenCount(self, attribute):
    if attribute == "name":
      count = self.childCount()
      return count
    return None

  

class ProcessusItem(StandardItem):
  def __init__(self, pid, parent):
    super(ProcessusItem, self).__init__(parent)
    self.__pid = pid


  def pid(self):
    return self.__pid

    
  def checkableAttribute(self):
    return "name"


  def sizeHint(self, attribute):
    data = self.display(attribute)
    if data.isValid():
      fm = QtGui.QApplication.instance().fontMetrics()
      width = fm.width(data)
      sizeHint = QtCore.QSize(width+100, 16)
      return sizeHint
    return None


  def display(self, attribute):
    if attribute == "name":
      processus = ProcessusManager()[self.__pid]
      name = QtCore.QString.fromUtf8(processus.name)
      return name
    if attribute == "pid":
      return self.__pid
    if attribute == "status":
      processus = ProcessusManager()[self.__pid]
      info = processus.stateinfo
      if len(info):
        status = processus.state + ": " + processus.stateinfo
      else:
        status = processus.state
      return status
    if attribute == "duration":
      return self.__processusDuration()
    return None


  def __processusDuration(self):
    processus = ProcessusManager()[self.__pid]
    if processus.timestart:
      stime = datetime.fromtimestamp(processus.timestart)
      if processus.timeend:
  	    etime = datetime.fromtimestamp(processus.timeend)
      else:
	      etime = datetime.fromtimestamp(time.time())
      delta = etime - stime
    else:
      delta = 0
    return str(delta)

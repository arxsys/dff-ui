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
from dff.ui.gui.nodes.nodesmodels import NodesListModel, NodesTreeModel
from dff.ui.gui.core.standardviews import StandardTableView, StandardTreeView, StandardIconView


class NodesDetailedView(StandardTableView):
  def __init__(self, parent=None):
    super(NodesDetailedView, self).__init__(parent)
    model = NodesListModel()
    self.setModel(model)


class NodesTreeView(StandardTreeView):
  def __init__(self, parent=None):
    super(NodesTreeView, self).__init__(parent)
    self.displayRecursion(True)
    model = NodesTreeModel()
    self.setModel(model)
    

  def setCurrentIndexFromUid(self, uid):
    index = self.model().createIndexFromUid(uid)
    if index.isValid():
      self.setCurrentIndex(index)
    

  def setFilesDisplay(self, enable):
    self.model().setFilesCreation(enable)


class NodesIconView(StandardIconView):
  def __init__(self, parent=None):
    super(NodesIconView, self).__init__(1, parent)

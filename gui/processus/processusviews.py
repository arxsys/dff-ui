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

import locale

from qtpy import QtCore, QtGui

from processus.processusmodels import ProcessusTreeModel
from core.standardviews import StandardTreeView


class ProcessusTreeView(StandardTreeView):
  def __init__(self, parent=None):
    super(ProcessusTreeView, self).__init__(parent)
    model = ProcessusTreeModel()
    self.setModel(model)
    self.__timer = QtCore.QTimer(self)
    #self.connect(self.__timer, QtCore.SIGNAL("timeout()"), model.refresh)
    self.__timer.start(2000)


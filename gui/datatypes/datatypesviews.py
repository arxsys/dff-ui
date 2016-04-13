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

from PyQt4 import QtCore, QtGui

from dff.ui.gui.datatypes.datatypesmodels import DatatypesTreeModel
from dff.ui.gui.core.standardviews import StandardTreeView


class DatatypesTreeView(StandardTreeView):
  def __init__(self, parent=None):
    super(DatatypesTreeView, self).__init__(parent)
    model = DatatypesTreeModel()
    self.setModel(model)

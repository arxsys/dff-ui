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

from tags.tagsmodels import TagsTreeModel
from core.standardviews import StandardTreeView


class TagsTreeView(StandardTreeView):
  def __init__(self, parent=None):
    super(TagsTreeView, self).__init__(parent)
    model = TagsTreeModel()
    self.setModel(model)

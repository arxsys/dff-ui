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

from nodes.nodesitems import NodeItem
#from dff.api.vfs.libvfs import VFS
from core.standarddelegates import StandardDelegate, StandardTreeDelegate, StandardIconDelegate


class NodesDelegate(StandardDelegate):
  def __init__(self, parent=None):
    super(NodesDelegate, self).__init__(parent)


  def tags(self, index):
    data = index.model().data(index, NodeItem.UidRole)
    if data.isValid():
      uid, success = data.toULongLong()
      if success and uid >= 0:
        node = VFS.Get().getNodeById(uid)
        if node is not None:
          tags = node.tags()
          return tags
    return []


class NodesTreeDelegate(StandardTreeDelegate):
  def __init__(self, parent=None):
    super(NodesTreeDelegate, self).__init__(parent)


  def tags(self, index):
    data = index.model().data(index, NodeItem.UidRole)
    if data.isValid():
      uid, success = data.toULongLong()
      if success and uid >= 0:
        node = VFS.Get().getNodeById(uid)
        if node is not None:
          tags = node.tags()
          return tags
    return []


class NodesIconDelegate(StandardIconDelegate):
  def __init__(self, parent=None):
    super(NodesIconDelegate, self).__init__(parent)


  def tags(self, index):
    data = index.model().data(index, NodeItem.UidRole)
    if data.isValid():
      uid, success = data.toULongLong()
      if success and uid >= 0:
        node = VFS.Get().getNodeById(uid)
        if node is not None:
          tags = node.tags()
          return tags
    return []

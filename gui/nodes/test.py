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

import sys, os, random

dffpath = os.getcwd()
idx = dffpath.find("dff")
dffpath = dffpath[:idx]
sys.path.append(dffpath)

from PyQt4 import QtGui, QtCore

from dff.ui.gui.nodes.nodestreemodel import NodesTreeModel
from dff.api.vfs.libvfs import VFS, Node
from dff.api.datatype import magichandler
from dff.api.events.libevents import EventHandler, event
from dff.api.types.libtypes import RCVariant, Variant

def generateTree(root, level, maxrec, count):
  maxsize = [1024, 1024**2, 1024**3, 1024**4, 1024**5]
  if level == maxrec:
    return
  else:
    lroot = Node("Level-" + str(level+1), 0, None, None)
    lroot.__disown__()
    root.addChild(lroot)
    for i in xrange(0, count):
      node = Node(str(i+1), 0, None, None)
      node.__disown__()
      if i % 2 == 0:
        node.setDir()
      else:
        node.setFile()
        node.setSize(random.randint(0, random.choice(maxsize)))
      randuid = random.randint(0, 10000)
      if randuid < 1000:
        node.setDeleted()
      lroot.addChild(node)
    generateTree(lroot, level + 1, maxrec, count)


class TestNodesTreeModel(QtGui.QWidget):
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)
    self.__view = QtGui.QTreeView()
    self.__treeModel = NodesTreeModel()
    self.__headers = QtGui.QHeaderView(QtCore.Qt.Horizontal)
    self.__headers.setModel(self.__treeModel)
    self.__view.setHeader(self.__headers)
    self.connect(self.__treeModel, QtCore.SIGNAL("insertedFoldersCount(int)"),
                 self.insertedFoldersCount)
    self.__root = VFS.Get().root
    for i in xrange(0, 10):
      croot = Node("Root-" + str(i+1), 0, None, None)
      croot.__disown__()
      self.__root.addChild(croot)
      generateTree(croot, 0, 50, 10)
    self.__view.setModel(self.__treeModel)
    populateTreeButton = QtGui.QPushButton("Populate base tree")
    self.connect(populateTreeButton, QtCore.SIGNAL("clicked()"), self.populate)
    registerTreeButton = QtGui.QPushButton("Register random tree")
    self.connect(registerTreeButton, QtCore.SIGNAL("clicked()"),
                 self.registerRandomTree)
    displayChildrenCheckbox = QtGui.QCheckBox("Display children count")
    self.connect(displayChildrenCheckbox, QtCore.SIGNAL("stateChanged(int)"),
                 self.displayChildrenCount)
    createFilesCheckbox = QtGui.QCheckBox("Create files")
    self.connect(createFilesCheckbox, QtCore.SIGNAL("stateChanged(int)"),
                 self.createFiles)
    layout = QtGui.QVBoxLayout()
    layout.addWidget(self.__view)
    layout.addWidget(populateTreeButton)
    layout.addWidget(registerTreeButton)
    layout.addWidget(displayChildrenCheckbox)
    layout.addWidget(createFilesCheckbox)
    self.setLayout(layout)

    
  def insertedFoldersCount(self, count):
    print("Number of folders inserted in tree view: {}".format(count))
    

  def populate(self):
    totalnodes = self.__root.totalChildrenCount()
    print("Populating tree view from {} nodes".format(totalnodes))
    self.__treeModel.setRootPath(self.__root)


  def displayChildrenCount(self, state):
    if state == QtCore.Qt.Checked:
      self.__treeModel.setDisplayChildrenCount(True)
    else:
      self.__treeModel.setDisplayChildrenCount(False)


  def createFiles(self, state):
    if state == QtCore.Qt.Checked:
      self.__treeModel.setFilesCreation(True)
    else:
      self.__treeModel.setFilesCreation(False)
      
      
  def registerRandomTree(self):
    randuid = random.randint(0, self.__root.totalChildrenCount()-1)
    parent = VFS.Get().getNodeById(randuid)
    cname = "Random {}".format(randuid)
    child = Node(cname, 0, None, None)
    child.__disown__()
    pabsolute = parent.absolute()
    pname = parent.name()
    info = 'Registering random tree "{}" to "{}"'.format(cname, pabsolute)
    if not (parent.hasChildren() or parent.isDir()):
      info += ' which had no children and was not set as folder'.format(pname)
    else:
      info += ' which already had children or was set as folder'.format(pname)
    print(info)
    parent.addChild(child)
    generateTree(child, 0, 10, 10)
    e = event()
    e.thisown = False
    e.value = RCVariant(Variant(child))
    VFS.Get().notify(e)


if __name__ == "__main__":
  qApp = QtGui.QApplication(sys.argv)
  test = TestNodesTreeModel()
  test.show()  
  sys.exit(qApp.exec_())

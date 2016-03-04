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
from dff.ui.gui.nodes.nodestablemodel import NodesTableModel

from dff.api.vfs.libvfs import VFS, Node
from dff.api.datatype import magichandler
from dff.api.events.libevents import EventHandler, event
from dff.api.types.libtypes import RCVariant, Variant

def generateTree(root, level, maxrec):
  maxsize = [1024, 1024**2, 1024**3, 1024**4, 1024**5]
  if level == maxrec:
    return
  else:
    lroot = Node("Level-" + str(level+1), 0, None, None)
    lroot.__disown__()
    root.addChild(lroot)
    for i in xrange(0, random.randint(0, 1024)):
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
    generateTree(lroot, level + 1, maxrec)


def registerRandomTree():
  randuid = random.randint(0, VFS.Get().root.totalChildrenCount()-1)
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
  generateTree(child, 0, random.randint(0, 32))
  e = event()
  e.thisown = False
  e.value = RCVariant(Variant(child))
  VFS.Get().notify(e)


def initTree():
  for i in xrange(0, random.randint(0, 32)):
    croot = Node("Root-" + str(i+1), 0, None, None)
    croot.__disown__()
    VFS.Get().root.addChild(croot)
    generateTree(croot, 0, random.randint(0, 32))
    


class NodesTreeBrowser(QtGui.QWidget):
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)
    self.__treeModel = NodesTreeModel()
    self.__root = None
    self.connect(self.__treeModel, QtCore.SIGNAL("insertedFoldersCount(int)"),
                 self.insertedFoldersCount)

    self.__treeHeaders = QtGui.QHeaderView(QtCore.Qt.Horizontal)
    self.__treeHeaders.setModel(self.__treeModel)

    self.__treeView = QtGui.QTreeView()
    self.__treeView.setModel(self.__treeModel)
    self.__treeView.setHeader(self.__treeHeaders)
    self.__treeView.clicked.connect(self.currentTreeItemChanged)
    
    layout = QtGui.QVBoxLayout()
    layout.addWidget(self.__treeView)
    self.setLayout(layout)
    self.createActions()

    
  def createActions(self):
    populateTreeButton = QtGui.QPushButton("Populate base tree")
    populateTreeButton.clicked.connect(self.populate)
    registerTreeButton = QtGui.QPushButton("Register random tree")
    registerTreeButton.clicked.connect(registerRandomTree)
    displayChildrenCheckbox = QtGui.QCheckBox("Display children count")
    displayChildrenCheckbox.stateChanged.connect(self.displayChildrenCount)
    createFilesCheckbox = QtGui.QCheckBox("Create files")
    createFilesCheckbox.stateChanged.connect(self.createFiles)
    self.layout().addWidget(populateTreeButton)
    self.layout().addWidget(registerTreeButton)
    self.layout().addWidget(displayChildrenCheckbox)
    self.layout().addWidget(createFilesCheckbox)


  def currentTreeItemChanged(self, index):
    if not index.isValid():
      return
    item = index.internalPointer()
    if item is None:
      return
    self.emit(QtCore.SIGNAL("currentTreeItemClicked(int)"), item.uid())


  def setRootUid(self, uid):
    if uid != -1:
      self.__rootUid = uid
      self.__treeModel.setRootUid(uid)
    

  def insertedFoldersCount(self, count):
    print("Number of folders inserted in tree view: {}".format(count))
    

  def populate(self):
    node = VFS.Get().getNodeById(self.__rootUid)
    if node is None:
      return
    totalnodes = node.totalChildrenCount()
    print("Populating tree view from {} nodes".format(totalnodes))
    self.__treeModel.setRootUid(self.__rootUid)


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


class NodesTableBrowser(QtGui.QWidget):
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)
    self.__tableModel = NodesTableModel()
    #self.__tableHeaders = QtGui.QHeaderView(QtCore.Qt.Horizontal)
    #self.__tableHeaders.setModel(self.__tableModel)

    self.__tableView = QtGui.QTableView()
    self.__tableView.setModel(self.__tableModel)
    #self.__tableView.setHeader(self.__tableHeaders)
    
    layout = QtGui.QVBoxLayout()
    layout.addWidget(self.__tableView)
    self.setLayout(layout)


  def setRootUid(self, uid):
    self.__tableModel.setRootUid(uid)



class TestNodesBrowser(QtGui.QWidget):
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)
    root = VFS.Get().GetNode("/")
    layout = QtGui.QHBoxLayout()
    self.setLayout(layout)
    self.__treeBrowser = NodesTreeBrowser()
    self.__treeBrowser.setRootUid(root.uid())

    self.__tableBrowser = NodesTableBrowser()
    self.__tableBrowser.setRootUid(root.uid())
    
    self.connect(self.__treeBrowser, QtCore.SIGNAL("currentTreeItemClicked(int)"), self.notifyViews)
    layout.addWidget(self.__treeBrowser)
    layout.addWidget(self.__tableBrowser)


  def notifyViews(self, uid):
    self.__tableBrowser.setRootUid(uid)
      

if __name__ == "__main__":
  qApp = QtGui.QApplication(sys.argv)
  initTree()
  test = TestNodesBrowser()
  test.show()  
  sys.exit(qApp.exec_())

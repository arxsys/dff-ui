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

import sys, os, random, time

dffpath = os.getcwd()
idx = dffpath.rfind("dff")
dffpath = dffpath[:idx]
sys.path.append(dffpath)

from PyQt4 import QtGui, QtCore

import dff
from dff.api.vfs.libvfs import VFS, Node
from dff.api.datatype.magichandler import *
from dff.api.events.libevents import EventHandler, event
from dff.api.types.libtypes import RCVariant, Variant
from dff.api.taskmanager.taskmanager import TaskManager

from dff.ui.gui.resources import gui_rc
from dff.ui.gui.browser.browser import Browser

from dff.ui.gui.api.widget.devicesdialog import DevicesDialog

from dff.ui.ui import parseArguments

from dff.ui.gui.widget.taskmanager import Processus
from dff.ui.gui.widget.stdio import STDErr, STDOut
from dff.ui.gui.widget.preview import Preview


from dff.ui.ui import UI

MODULES_PATHS = [os.path.join(dffpath, "dff", "modules")]

print MODULES_PATHS


MAX_DEPTH=16
MAX_CHILDREN=32

def generateTree(root, level, maxrec):
  maxsize = [1024, 1024**2, 1024**3, 1024**4, 1024**5]
  if level == maxrec:
    return
  else:
    lroot = Node("Level-" + str(level+1), 0, None, None)
    lroot.__disown__()
    root.addChild(lroot)
    for i in xrange(0, random.randint(0, MAX_CHILDREN)):
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
  generateTree(child, 0, random.randint(0, MAX_DEPTH))
  e = event()
  e.thisown = False
  e.value = RCVariant(Variant(child))
  VFS.Get().notify(e)


def registerWithSameName():
  parent = VFS.Get().GetNode("/")
  cname = "Same"
  child = Node(cname, 0, None, None)
  child.__disown__()
  pabsolute = parent.absolute()
  pname = parent.name()
  info = 'Registering "{}" to "{}"'.format(cname, pabsolute)
  if not (parent.hasChildren() or parent.isDir()):
    info += ' which had no children and was not set as folder'.format(pname)
  else:
    info += ' which already had children or was set as folder'.format(pname)
  print(info)
  parent.addChild(child)
  e = event()
  e.thisown = False
  e.value = RCVariant(Variant(child))
  VFS.Get().notify(e)


def initTree():
  for i in xrange(0, random.randint(0, MAX_CHILDREN)):
    croot = Node("Root-" + str(i+1), 0, None, None)
    croot.__disown__()
    VFS.Get().root.addChild(croot)
    generateTree(croot, 0, random.randint(0, MAX_DEPTH))


class DockWidget(QtGui.QDockWidget):
  def __init__(self, parent=None, widget=None, title="", flags=QtCore.Qt.Widget):
    QtGui.QDockWidget.__init__(self, parent, flags)
    self.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
    if widget != None:
      self.setWidget(widget)
    self.setWindowTitle(title)


  def windowIcon(self):
    return self.widget().windowIcon()
  
    
class OpenEvidenceMenu(QtGui.QMenu):
  def __init__(self, parent=None):
    QtGui.QMenu.__init__(self, parent)
    self.setStyleSheet("QMenu {icon-size: 32px;}")
    icon = self.__createIcon(QtGui.QStyle.SP_DriveHDIcon)
    self.addAction(icon, "Device", self.openDevice,
                   QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_D))
    icon = self.__createIcon(QtGui.QStyle.SP_FileIcon, "Raw")
    self.addAction(icon, "RAW image", self.openRaw,
                   QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_O))
    icon = self.__createIcon(QtGui.QStyle.SP_FileIcon, "Ewf")
    self.addAction(icon, "EWF image", self.openEwf,
                   QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_E))
    icon = self.__createIcon(QtGui.QStyle.SP_FileIcon, "Aff")
    self.addAction(icon, "AFF image", self.openAff,
                   QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_A))
    icon = self.__createIcon(QtGui.QStyle.SP_FileIcon)
    self.addAction(icon, "File(s)", self.openFiles,
                   QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_F))
    icon = self.__createIcon(QtGui.QStyle.SP_DirIcon)
    self.addAction(icon, "Folder(s)", self.openFolders,
                   QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.ALT + QtCore.Qt.Key_F))


  def __createIcon(self, iconName, text=None):
    baseIcon = QtGui.qApp.style().standardIcon(iconName)
    if text is not None:
      iconPixmap = baseIcon.pixmap(QtCore.QSize(32, 32))
      painter = QtGui.QPainter(iconPixmap)
      font = painter.font()
      font.setPointSize(9)
      painter.setFont(font)
      rect = iconPixmap.rect()
      rect.setX(rect.x())
      painter.drawText(rect, QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter, text)
      painter.end()
      icon = QtGui.QIcon(iconPixmap)
    else:
      icon = baseIcon
    return icon

  
  def openDevice(self):
    dialog = DevicesDialog()
    screenGeometry = QtGui.QApplication.desktop().screenGeometry(0)
    dialog.move(screenGeometry.center() - self.rect().center())
    dialog.exec_()
    

  def openRaw(self):
    caption = "Choose RAW file(s) to import."
    caption += " With split RAW files, you can only select the first segment"
    dialog = QtGui.QFileDialog(self, translate(self, caption))
    dialog.setNameFilters([self.tr("Raw File Format (*.bin, *.dd, *.001)"), self.tr("Any files (*)")])
    screenGeometry = QtGui.QApplication.desktop().screenGeometry(0)
    dialog.move(screenGeometry.center() - self.rect().center())
    dialog.exec_()


  def openEwf(self):
    caption = "Choose EWF file(s) to import."
    caption += " With split EWF files, you can only select the first segment"
    dialog = QtGui.QFileDialog(self, translate(self, caption))
    dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
    dialog.setNameFilters([self.tr("Encase File Format (*.E01)"), self.tr("Any files (*)")])
    screenGeometry = QtGui.QApplication.desktop().screenGeometry(0)
    dialog.move(screenGeometry.center() - self.rect().center())
    action = dialog.exec_()
    if action == QtGui.QDialog.Accepted:
      files = dialog.selectedFiles()
      if len(files):
        args = {}
        args['files'] = []
        ewfFile = QtCore.QFileInfo(files[0])
        folder = ewfFile.absoluteDir()
        ewfFiles = folder.entryList(["*E*"], QtCore.QDir.Files, QtCore.QDir.Name)
        for ewfFile in ewfFiles:
          args['files'].append(str(folder.filePath(ewfFile).toUtf8()))
        TaskManager().add('ewf', args, [])
      
  
  def openAff(self):
    caption = "Choose AFF file(s) to import."
    caption += " With split AFF files, you can only select the first segment"
    dialog = QtGui.QFileDialog(self, translate(self, caption))
    dialog.setNameFilters([self.tr("Aff File Format (*.A??)"), self.tr("Any files (*)")])
    screenGeometry = QtGui.QApplication.desktop().screenGeometry(0)
    dialog.move(screenGeometry.center() - self.rect().center())
    dialog.exec_()


  def openFiles(self):
    dialog = QtGui.QFileDialog(self)
    dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
    dialog.setNameFilters([self.tr("Any files (*)"),
                           self.tr("Images (*.png, *.jpg, *.bmp)"),
                           self.tr("Text files (*.txt)")])
    screenGeometry = QtGui.QApplication.desktop().screenGeometry(0)
    dialog.move(screenGeometry.center() - self.rect().center())
    action = dialog.exec_()
    if action == QtGui.QDialog.Accepted:
      files = dialog.selectedFiles()
      args = {}
      args['path'] = []
      for _file in files:
        args['path'].append(str(_file.toUtf8()))
      TaskManager().add('local', args, [])
      

  def openFolders(self):
    dialog = QtGui.QFileDialog(self)
    dialog.setFileMode(QtGui.QFileDialog.Directory)
    dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)
    screenGeometry = QtGui.QApplication.desktop().screenGeometry(0)
    dialog.move(screenGeometry.center() - self.rect().center())
    action = dialog.exec_()
    if action == QtGui.QDialog.Accepted:
      folders = dialog.selectedFiles()
      args = {}
      args['path'] = []
      for _folder in folders:
        args['path'].append(str(_folder.toUtf8()))
      TaskManager().add('local', args, [])


def translate(context, sourceText, disambiguation=None):
  return QtCore.QCoreApplication.translate(context.__class__.__name__,
                                           sourceText, disambiguation)
  

class OpenEvidenceButton(QtGui.QPushButton):
  def __init__(self, parent=None):
    QtGui.QPushButton.__init__(self, translate(self, "Open"),
                               parent)
    self.__pixmap = QtGui.QPixmap(":folder_documents_128.png").scaled(32, 32)
    self.setIcon(QtGui.QIcon(self.__pixmap))
    menu = OpenEvidenceMenu(self)
    self.setFlat(True)
    self.setDefault(False)
    self.setMenu(menu)


  def sizeHint(self):
    fm = QtGui.QApplication.instance().fontMetrics()
    width = fm.width(self.tr("Open"))
    sizeHint = QtCore.QSize(width+self.__pixmap.width()+15, self.__pixmap.height())
    return sizeHint

  
class MainWindowToolBar(QtGui.QToolBar):
  def __init__(self, parent=None):
    QtGui.QToolBar.__init__(self, parent)
    self.setMovable(False)
    self.setFloatable(True)
    openEvidence = OpenEvidenceButton(self)
    self.addWidget(openEvidence)
    createBrowserButton = QtGui.QPushButton(self.tr("Browser"), self)
    createBrowserButton.clicked.connect(self.__createBrowser)
    createBrowserButton.setFlat(True)
    createBrowserButton.setDefault(False)
    self.addWidget(createBrowserButton)


  def __createBrowser(self):
    browser = Browser()
    dockwidget = DockWidget(self, browser, self.tr("Browser"))
    self.parent().addDockWidget(QtCore.Qt.TopDockWidgetArea, dockwidget)


class MainWindow(QtGui.QMainWindow):
  def __init__(self, parent=None, flags=QtCore.Qt.Widget):
    QtGui.QMainWindow.__init__(self, parent, flags)
    self.__dockWidgets = {}
    self.__topRootDockWidget = None
    self.__bottomRootDockWidget = None
    self.__tabMovedConnections = set()
    self.__tabAreaInformaion = (None, None, None)
    self.__tabMoved = False
    self.__tabBars = set()
    self.__initDockingState()
    self.__toolBar = MainWindowToolBar(self)
    self.addToolBar(QtCore.Qt.TopToolBarArea, self.__toolBar)


  def render(self):
    browser = Browser()
    self.__mainBrowser = DockWidget(self, browser, self.tr("Browser"))
    self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.__mainBrowser)
    self.__processus = Processus(None)
    self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                       DockWidget(self, self.__processus,
                                  self.tr("Task manager")))
    # XXX manage debug flag
    self.__output = STDOut(None, True)
    self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                       DockWidget(self, self.__output, self.tr("Output")))                       
    self.__error = STDErr(None, False)
    self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                       DockWidget(self, self.__error, self.tr("Errors")))
    self.__preview = Preview(None)
    self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                       DockWidget(self, self.__preview, self.tr("Preview")))
    self.timer = QtCore.QTimer(self)
    self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.__refreshSecondWidgets)
    self.timer.start(2000)
    font = self.font()
    font.setPointSize(9)
    self.setFont(font)



  def tabifyDockWidget(self, first, second):
    super(MainWindow, self).tabifyDockWidget(first, second)
    #self.__updateTabConnections()


  def addDockWidget(self, area, dockwidget):
    if dockwidget is None:
      return
    baseTitle = dockwidget.windowTitle()
    counter = 0
    for dockWidgetTitle in self.__dockWidgets.iterkeys():
      if dockWidgetTitle.startsWith(baseTitle):
        counter += 1
    if counter > 0:
      baseTitle.append(QtCore.QString.number(counter))
      dockwidget.setWindowTitle(baseTitle)
    self.__dockWidgets[baseTitle] = dockwidget
    super(MainWindow, self).addDockWidget(area, dockwidget)
    if area == QtCore.Qt.TopDockWidgetArea:
      if self.__topRootDockWidget is None:
        self.__topRootDockWidget = dockwidget
      else:
        self.tabifyDockWidget(self.__topRootDockWidget, dockwidget)
    elif area == QtCore.Qt.BottomDockWidgetArea:
      if self.__bottomRootDockWidget is None:
        self.__bottomRootDockWidget = dockwidget
      else:
        self.tabifyDockWidget(self.__bottomRootDockWidget, dockwidget)
    dockwidget.dockLocationChanged.connect(self.__dockWidgetLocationChanged)


  def __dockWidgetLocationChanged(self, area):
    widget = self.childAt(QtCore.QPoint(self.__toolBar.pos().x(),
                                               self.__toolBar.height()+1))
    if widget is not None:
      if widget.inherits("QTabBar"):
        tabText = widget.tabText(0)
        if self.__dockWidgets.has_key(tabText):
          self.__topRootDockWidget = self.__dockWidgets[tabText]
      elif widget.inherits("QDockWidget"):
        self.__topRootDockWidget = widget
      else:
        print "__dockWidgetLocationChanged unknown widget type"


  # Each time a new tabification is done, the resulting qtabbar exists
  # forever, even if it is no longer used. So we can safely register the
  # newly created tabbar
  def tabifyDockWidget(self, first, second):
    super(MainWindow, self).tabifyDockWidget(first, second)
    count = 0
    children = self.children()
    for child in children:
      if child.inherits("QTabBar"):
        if child not in self.__tabBars:
          self.__tabBars.add(child)
          child.setMovable(True)
          child.tabMoved.connect(self._tabMoved,
                                 type=QtCore.Qt.UniqueConnection)
        for idx in xrange(0, child.count()):
          tabText = child.tabText(idx)
          if self.__dockWidgets.has_key(tabText):
            child.setTabIcon(idx, self.__dockWidgets[tabText].windowIcon())

  
  def __refreshTabBars(self):
    for tabBar in self.__tabBars:
      for idx in xrange(0, tabBar.count()):
        tabText = tabBar.tabText(idx)
        if self.__dockWidgets.has_key(tabText):
          tabBar.setTabIcon(idx, self.__dockWidgets[tabText].windowIcon())

              
  def event(self, event):          
    mouseStatus = int(QtGui.QApplication.mouseButtons())
    if mouseStatus & 0x00000001 == 0:
      if self.__tabMoved:
        self.__tabMoved = False
        tab, to, _from = self.__tabAreaInformation
        if tab is not None and tab.count() > 0:
          siblings = []
          visible = []
          hidden = []
          currentDockWidget = None
          for idx in xrange(0, tab.count()):
            tabText = tab.tabText(idx)
            dockwidget = self.__dockWidgets[tabText]
            if idx == tab.currentIndex():
              currentDockWidget = dockwidget
            elif dockwidget.isVisible():
              visible.append(dockwidget)
            else:
              hidden.append(dockwidget)
          if to == 0:
            siblings.append(currentDockWidget)
          else:
            siblings.append(visible.pop(0))
            if currentDockWidget is not None:
              visible.insert(to-1, currentDockWidget)
          siblings += visible + hidden
          root = siblings.pop(0)
          for sibling in siblings:
            if sibling is not None:
              self.tabifyDockWidget(root, sibling)
          tab.setCurrentIndex(to)
      elif event.type() == QtCore.QEvent.UpdateRequest:
        self.__refreshTabBars()        
    return super(MainWindow, self).event(event)


  # if updating tabBar while mouse is still pressed results in strange behaviour.
  # We just save the context that will be used in event method
  # to and _from are volontary swapped here compared to the original signal.
  def _tabMoved(self, to, _from):
    tab = self.sender()
    self.__tabAreaInformation = (tab, to, _from)
    self.__tabMoved = True


  def __initDockingState(self):
    self.setWindowModality(QtCore.Qt.ApplicationModal)
    self.setCentralWidget(None)
    self.setDockNestingEnabled(True)
    self.setContentsMargins(0, 0, 0, 0)
    widgetPos = [(QtCore.Qt.TopLeftCorner, QtCore.Qt.LeftDockWidgetArea, QtGui.QTabWidget.North),
	         (QtCore.Qt.BottomLeftCorner, QtCore.Qt.BottomDockWidgetArea, QtGui.QTabWidget.North),
	         (QtCore.Qt.TopLeftCorner, QtCore.Qt.TopDockWidgetArea, QtGui.QTabWidget.North),
	         (QtCore.Qt.BottomRightCorner, QtCore.Qt.RightDockWidgetArea, QtGui.QTabWidget.North)]
    for corner, area, point in widgetPos:
      self.setCorner(corner, area)
      self.setTabPosition(area, point)


  def __refreshSecondWidgets(self):
    self.__processus.LoadInfoProcess()


class TreeModifier(QtGui.QWidget):
  def __init__(self, parent=None):
    populateTreeButton = QtGui.QPushButton("Populate base tree")
    populateTreeButton.clicked.connect(self.populate)
    registerTreeButton = QtGui.QPushButton("Register random tree")
    registerTreeButton.clicked.connect(registerRandomTree)
    registerSameButton = QtGui.QPushButton("Register with same name")
    registerSameButton.clicked.connect(registerWithSameName)
    displayChildrenCheckbox = QtGui.QCheckBox("Display children count")
    displayChildrenCheckbox.stateChanged.connect(self.displayChildrenCount)
    createFilesCheckbox = QtGui.QCheckBox("Create files")
    createFilesCheckbox.stateChanged.connect(self.createFiles)
    self.layout().addWidget(populateTreeButton)
    self.layout().addWidget(registerTreeButton)
    self.layout().addWidget(registerSameButton)
    self.layout().addWidget(displayChildrenCheckbox)
    self.layout().addWidget(createFilesCheckbox)


  def populate(self):
    node = VFS.Get().getNodeById(self.__rootUid)
    if node is None:
      return
    totalnodes = node.totalChildrenCount()
    print("Populating tree view from {} nodes".format(totalnodes))
    self.__treeModel.setRootUid(self.__rootUid)


class SplashScreen(QtGui.QSplashScreen):
  def __init__(self, pixmap, windowFlag, versionNumber):
    QtGui.QSplashScreen.__init__(self, pixmap, windowFlag)
    self.__versionNumber = versionNumber


  def drawContents(self, painter):
    QtGui.QSplashScreen.drawContents(self, painter) 
    painter.drawText(10, 178, "Version " + str(self.__versionNumber))

    
class Gui(QtGui.QApplication, UI):
  def __init__(self, arguments):
    QtGui.QApplication.__init__(self, sys.argv)
    UI.__init__(self, arguments)
    resource = QtCore.QResource()
    resource.registerResource(gui_rc.qt_resource_data)
    self.__setFusionStyle(False)
    self.__arguments = arguments
    self.setApplicationName("Digital Forensics Framework")
    self.setApplicationVersion(dff.VERSION)
    pixmap = QtGui.QPixmap(":splash.png")
    self.__splash = SplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint, self.applicationVersion())
    self.__splash.setMask(pixmap.mask()) 


  def __setFusionStyle(self, dark=False):
    self.setStyle(QtGui.QStyleFactory.create("Fusion"))
    if dark:
      darkPalette = QtGui.QPalette()
      darkPalette.setColor(QtGui.QPalette.Window, QtGui.QColor(53,53,53))
      darkPalette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
      darkPalette.setColor(QtGui.QPalette.Base, QtGui.QColor(25,25,25))
      darkPalette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53,53,53))
      darkPalette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
      darkPalette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
      darkPalette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
      darkPalette.setColor(QtGui.QPalette.Button, QtGui.QColor(53,53,53))
      darkPalette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
      darkPalette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
      darkPalette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
      darkPalette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
      darkPalette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
      self.setPalette(darkPalette)


  def mainWindow(self):
    return self.__mainWindow


  def launch(self, modulesPaths = None, defaultConfig=None):
    self.__splash.show()
    if modulesPaths or defaultConfig:
      self.loadModules(modulesPaths, self.__splash.showMessage, defaultConfig)
    self.__mainWindow = MainWindow()
    self.__mainWindow.setWindowState(self.__mainWindow.windowState() | QtCore.Qt.WindowMaximized)
    self.__mainWindow.setWindowTitle("Digital Forensics Framework " + dff.VERSION)
    self.__mainWindow.render()
    self.__mainWindow.show()
    self.__splash.finish(self.__mainWindow)
    sys.exit(self.exec_())
  

if __name__ == "__main__":
  """You can place some script command here for testing purpose"""
  arguments = parseArguments()
  ui = Gui(arguments)
  ui.launch(MODULES_PATHS)

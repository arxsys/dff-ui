# DFF -- An Open Source Digital Forensics Framework
# Copyright (C) 2009-2013 ArxSys
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
#  Solal Jacob <solal.jacob@digital-forensic.org>
#
from PyQt4.QtCore import Qt, QString, QEvent, QVariant, SIGNAL
from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QBrush, QColor, QLabel

from dff.api.vfs.libvfs import VLink

from dff.ui.gui.api.widget.varianttreewidget import VariantTreeWidget

class PropertyTable(VariantTreeWidget):
  def __init__(self, parent):
    VariantTreeWidget.__init__(self, parent)
    self.node = None
    self.translation()

  def fillBase(self, node):
    fsobj = node.fsobj()
    fsobjname = ""
    if fsobj != None:
      fsobjname = fsobj.name
    itemName = QTreeWidgetItem(self)
    itemName.setText(0, self.nameText)
    itemName.setText(1, QString.fromUtf8(node.name()))
    if isinstance(node, VLink):
      linkPath = QTreeWidgetItem(self)
      linkPath.setText(0, self.linkPath)
      label = QLabel('<a href="' + QString.fromUtf8(node.linkPath()) + '" style="color: blue">'+QString.fromUtf8(node.linkAbsolute())+' </a>')
      label.connect(label, SIGNAL("linkActivated(QString)"), self.gotolink)
      self.setItemWidget(linkPath, 1, label)

    itemName = QTreeWidgetItem(self)
    itemName.setText(0, self.nodeTypeText)
 
    typestr = ""
    if node.isFile():
      typestr += self.fileText
      if node.hasChildren():
        typestr += self.modAppliedText
    self.fillCompatModule(node)
    if node.hasChildren():
      self.fillChildren(node)
        
    if node.isDir():
      typestr += self.folderText
      if not node.hasChildren():
        typestr += self.emptyText
    if node.isDeleted():
      typestr += self.deletedText
    itemName.setText(1, typestr)

    itemModule = QTreeWidgetItem(self)
    itemModule.setText(0, self.generateText)
    itemModule.setText(1, str(fsobjname))
    
    itemSize = QTreeWidgetItem(self)
    itemSize.setText(0, self.sizeText)
    itemSize.setText(1, str(node.size()))

    tags = node.tags()
    if len(tags):
      itemTags = QTreeWidgetItem(self)
      itemTags.setText(0, "tags")
      tags = node.tags()
      for tag in tags:
         itemTag = QTreeWidgetItem(itemTags)
	 color = tag.color()
	 itemTag.setBackground(0, QBrush(QColor(color.r, color.g, color.b)))
	 itemTag.setForeground(0, QBrush(QColor(255,255,255)))
         itemTag.setText(0, QString.fromUtf8(tag.name()))
      self.expandItem(itemTags)	

  def fillCompatModule(self, node):
    l = node.compatibleModules()
    if len(l) > 0:
      itemCompat = QTreeWidgetItem(self)
      itemCompat.setText(0, self.relevantText)
      buff = ""
      for i in l:
        buff += str(i) + " " 
      itemCompat.setText(1, buff)

  def fillChildren(self, node): 
    itemChildren = QTreeWidgetItem(self)
    itemChildren.setText(0, self.childrenText)
    itemChildren.setText(1, str(node.childCount()))
    children = node.children()
    filessize = 0
    filecount = 0
    dircount = 0
    for child in children:
      if child.size():
        filessize += child.size()
        filecount += 1
      elif child.isDir() or child.hasChildren():
        dircount += 1
    if filecount > 0:
      itemFile = QTreeWidgetItem(itemChildren)
      itemFile.setText(0, self.filesText)
      itemFile.setText(1, str(filecount) + self.totText + str(filessize) + self.bytesText)
    if dircount > 0:
      itemFolder = QTreeWidgetItem(itemChildren)
      itemFolder.setText(0, self.foldersText)
      itemFolder.setText(1, str(dircount))
    self.expandItem(itemChildren)    
    
  def fillAttributes(self, node):
    try:
      vmap = node.attributes()
      if vmap:
        if len(vmap) > 0:
          itemExtendedAttr = QTreeWidgetItem(self)
          itemExtendedAttr.setText(0, self.attributeText)
          self.fillMap(itemExtendedAttr, vmap)
          self.expandItem(itemExtendedAttr)
    except:
      pass

  def fill(self, node = None):
    if not node:
      node = self.node
    self.node = node
    self.clear()
    if self.isVisible():
      self.fillBase(node)
      self.fillAttributes(node)
      self.resizeColumnToContents(0)
      self.resizeColumnToContents(1)

  def translation(self):
    self.nameText = self.tr('name')
    self.pathText = self.tr('path')
    self.linkPath = self.tr('link path')
    self.nodeTypeText = self.tr('node type')
    self.fileText = self.tr('file')
    self.modAppliedText = self.tr(' with module(s) applied on it')
    self.folderText = self.tr('folder')
    self.emptyText = self.tr(' empty')
    self.deletedText = self.tr(' deleted')
    self.generateText = self.tr('generated by')
    self.sizeText = self.tr('size')
    self.relevantText = self.tr('relevant module(s)')
    self.childrenText = self.tr('children')
    self.filesText = self.tr('file(s)')
    self.totText = self.tr(' totalizing ')
    self.bytesText = self.tr(' bytes')
    self.foldersText = self.tr('folder(s)')
    self.attributeText = self.tr('attributes')
    
  def changeEvent(self, event):
    """ Search for a language change event
    
    This event have to call retranslateUi to change interface language on
    the fly.
    """
    if event.type() == QEvent.LanguageChange:
      self.retranslateUi(self)
      self.translation()
      if self.node is not None:
        self.fill()
    else:
      QTreeWidget.changeEvent(self, event)

# DFF -- An Open Source Digital Forensics Framework
# Copyright (C) 2009-2011 ArxSys
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
#  Romain Bertholon <rbe@digital-forensic.org>
# 
import sys

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import QWidget, QLabel, QPushButton, QDialog, QTableWidget, QTableWidgetItem, QAbstractItemView, QIcon, QVBoxLayout

from dff.api.vfs.libvfs import VFS

from api.gui.widget.nodeview import NodeLinkTreeView

from dff.ui.gui.resources.ui_modif_index import Ui_ModifIndex
from dff.ui.gui.widget.SelectMimeTypes import MimeTypesTree

class ModifIndex(QDialog, Ui_ModifIndex):
    """
    This class is used to graphically configures indexation :
    * its content
    * its behaviour and the type of data which musts be indexed
    
    It is composed of three tabs : Index, Advanced and Attributes.

    The `Index` tab us composed of two main widgets :
    * a NodeLinkTreeView, called `selectIndexItems`, connected to an instance
    of a TreeModel (see api.gui.model.vfsitemmodel, class TreeModel
    and api.gui.widget.nodeview, class NodeLinkTreeView).

    It displays the tree view of the VFS' nodes, with checkboxes used to select
    nodes the user wants to add in the index.

    * a QTableWidget, called `indexedItems`,  used to summarize the list of
    already indexed nodes.

    By checking / unchecking a nodes in the NodeLinkTreeView, it adds / removes
    elements in the `indexedItems` view. If an element is unchecked and the `OK`
    button clicked, the element will be removed from the index. On the contrary,
    if an element is checked in the NodeLinkTreeView and the `OK` button clicked,
    it will add it in the index ONLY if it was not already indexed.

    Changed are applied when the `OK` button is clicked.
    """
    def __init__(self, parent, model):
        """
        Constructor.

        Initialize parent, gui and translation. Connect signals.
        """
        super(QDialog, self).__init__()
        self.parent = parent
        self.setupUi(self)
        self.translation()

        self.initTableWidget()
        self.initMimeTypes()

        self.indexed_items = {}
        self.tmp_indexed_items = {}
        self.un_index = {}

        self.indexedItems.setColumnCount(2)
        self.indexedItems.setRowCount(self.load_items())
        self.model = TreeModel(self)
        self.model.root_item = model.root_item
        self.model.setCh(True)

        self.selectIndexItems = NodeLinkTreeView(None, True)
        self.selectIndexItems.setModel(self.model)
        vbox = QVBoxLayout()
        vbox.addWidget(self.selectIndexItems)
        self.groupBox_5.setLayout(vbox)
        self.connect(self.selectIndexItems, SIGNAL("nodeTreeClicked"), self.nodeTreeClicked)
        self.connect(self.selectIndexItems.model(), SIGNAL("stateChanged"), self.selectNodeChanged)
        self.connect(self.indexedItems, SIGNAL("itemChanged(QTableWidgetItem *)"), \
                         self.IAmBabarTheElephantKing)
        self.connect(self.indexedItems, SIGNAL("itemClicked"), self.IAmBabarTheElephantKing)

    def initTableWidget(self):
        """
        Initialize the QTableWidget `indexedItems`. Set the headers.
        """
        self.indexedItems.setColumnCount(2)

        # set the headers' titles and stretch the last section
        head1 = QTableWidgetItem(self.headIndexedItemTr)
        head2 = QTableWidgetItem(self.headRecursivelyTr)
        self.indexedItems.setHorizontalHeaderItem(0, head1)
        self.indexedItems.setHorizontalHeaderItem(1, head2)
        self.indexedItems.horizontalHeader().setStretchLastSection(True)

        # hide vertical header and grid, remove editable mode
        self.indexedItems.verticalHeader().hide()
        self.indexedItems.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.indexedItems.setShowGrid(False)
        self.indexedItems.setAlternatingRowColors(True)
        self.indexedItems.setSelectionBehavior(QAbstractItemView.SelectRows)

    def load_items(self):
        """
        Load items from the indexed_items list and add them in the
        self.indexedItems QTableWidget.
        """
        count = 0

        # get the list of already indexed stuff and add them in the qtablewidget
        # with a not-editable check box indicating if it has been indexed
        # recursively or not
        for i in self.indexed_items:
            node = VFS.Get().getNodeFromPointer(long(i))
            if node == None:
                continue
            recurse = self.indexed_items[i]

            new_item = QTableWidgetItem(QIcon(":/folder.png"), node.name())
            self.indexedItems.setRowCount(count + 1)
            new_item.setData(Qt.UserRole + 1, QVariant(long(node.this)))

            self.indexedItems.setItem(count, 0, new_item)

            new_item2 = QTableWidgetItem()
            new_item2.setFlags(Qt.ItemIsUserCheckable)
            if recurse:
                new_item2.setCheckState(Qt.Checked)
            else:
                new_item2.setCheckState(Qt.Unchecked)
            self.indexedItems.setItem(count, 1, new_item2)
            count += 1
        return count

    def initMimeTypes(self):
        self.typesTree = MimeTypesTree(self.mimeTypeList)
        self.mimeTypeList.setHeaderLabels([self.mimeTypeTr])

    def selectNodeChanged(self, index):
        """
        This slot is called when a node is checked / unchecked. Then, the method
        `addNodeInIndexList` or `removeNodeFromIndexList` is called (of course 
        depending if it was checked of unchcked).
        """
        if not index.isValid():
            return
        d = self.selectIndexItems.model().data(index, Qt.CheckStateRole)
        if d == Qt.Checked:
            self.addNodeInIndexList(index)
        else:
            self.removeNodeFromIndexList(index)

    def addNodeInIndexList(self, index):
        """
        Add the node wich pointer is index.data(QT.UserRole + 1) in the
        indexedItems list.
        """
        # get the node from the index
        node_ptr = self.selectIndexItems.model().data(index, Qt.UserRole + 1)
        if not node_ptr.isValid():
            return
        added_node = VFS.Get().getNodeFromPointer(node_ptr.toULongLong()[0])

        # add the node.this into the selected items list
        new_item = QTableWidgetItem(QIcon(":/folder.png"), added_node.name())
        new_item.setData(Qt.UserRole + 1, QVariant(long(added_node.this)))
        self.tmp_indexed_items[long(added_node.this)] = False

        new_checkbox = QTableWidgetItem(1);
        new_checkbox.data(Qt.CheckStateRole);
        new_checkbox.setCheckState(Qt.Unchecked);

        self.indexedItems.insertRow(0)
        self.indexedItems.setItem(0, 0, new_item)
        self.indexedItems.setItem(0, 1, new_checkbox)

    def IAmBabarTheElephantKing(self, item):
        if item.column() == 0:
            return
        row = item.row()
        item_check = self.indexedItems.itemAt(row, 0)
        data = item_check.data(Qt.UserRole + 1)
        if not data.isValid():
            return
        ptr = data.toULongLong()[0]
        try:
            self.tmp_indexed_items[long(ptr)] = not self.tmp_indexed_items[long(ptr)]
        except KeyError:
            pass

    def removeNodeFromIndexList(self, index):
        """
        Remove the node wich pointer is index.data(QT.UserRole + 1) from the
        indexedItems list.
        """
        # get the node from the index (if one of them is invalid, returns)
        if not index.isValid():
            return
        node_ptr = self.selectIndexItems.model().data(index, Qt.UserRole + 1)
        if not node_ptr.isValid():
            return

        # get the ptr of the node and search for the it in the indexedItems list
        ptr = node_ptr.toULongLong()[0]

        # for each items in the indexed_list, check if the value is equal to
        # `ptr`. If yes, remove the item from the QTableWidget self.indexedItems.
        found = False
        for i in range(0, len(self.indexed_items)):
            item = self.indexedItems.item(i, 0)
            if item != None:
                value = item.data(Qt.UserRole + 1)
                if value.isValid():
                    if value.toULongLong()[0] == ptr:
                        self.indexedItems.removeRow(i)
                        self.un_index[ptr] = self.indexed_items[ptr]
                        found = True
                        break

        if not found:
            for i in range(0, len(self.tmp_indexed_items)):
                item = self.indexedItems.item(i, 0)
                if item != None:
                    value = item.data(Qt.UserRole + 1)
                    if value.isValid():
                        if value.toULongLong()[0] == ptr:
                            self.indexedItems.removeRow(i)
                            break

        # finally pop the item from the indexed_items or tmp_indexed_items map
        try:
            if not found:
                self.tmp_indexed_items.pop(ptr)                
        except KeyError:
            pass

    def nodeTreeClicked(self, mouseButton, node, index = None):
        """
        This slot is called when a node from the NodeLinkTreeView is clicked.
        """
        self.selectIndexItems.model().setRootPath(node)

    def translation(self):
        """
        Used for the dynamic translations.
        """
        self.headIndexedItemTr = self.tr("Indexed items")
        self.headRecursivelyTr = self.tr("Recursively")
        self.mimeTypeTr = self.tr("Mime types")

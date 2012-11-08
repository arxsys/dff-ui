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
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import QWidget, QPushButton, QDialog, QTableWidget, QTableWidgetItem, QAbstractItemView, QIcon

from dff.ui.gui.resources.ui_indexationui import Ui_IndexationUI
from dff.ui.gui.resources.ui_modif_index import Ui_ModifIndex
from dff.ui.gui.widget.modif_index import ModifIndex

class IndexOpt(QDialog, Ui_IndexationUI):
    """
    This GUI dialog box is used to display nodes which already are indexedm with the exception of
    subdirectories which are nod added in the index.

    It is made as follow :

    Indexed items | Exceptions
    ------------------------------------
    Dir1          |        --
    Dir2          | Subdir2.1, Subdir2.2
    Dir3          |        --

    and so on.

    To button are clickable "Modify" and "Advanced", respectively allowing to modify the content
    of the index and to configure the behavior of the index.
    """
    def __init__(self, parent, model):
        """
        Init the GUI, the parent and connect signals.

        **Param**::
                * ``parent`` : the parent widget (NodeFilterBox instance)
        """

        super(QDialog, self).__init__()
        self.parent = parent
        self.setupUi(self)
        self.model = model
        
        self.adv_index = ModifIndex(self, model)
        
        # connect the buttons signal to their slots.
        if QtCore.PYQT_VERSION_STR >= "4.5.0":
            self.indexAdvanced.clicked.connect(self.advanceOpt)
            self.modifIndexItems.clicked.connect(self.indexItems)
        else:
            QtCore.QObject.connect(self.indexAdvanced, SIGNAL("clicked(bool)"), self.advanceOpt)
            QtCore.QObject.connect(self.modifIndexItems, SIGNAL("clicked(bool)"), self.indexItems)

        self.initTableWidget()

        # ### FOR TESTING ###
        self.indexedItems.setRowCount(3)
        self.load_items()

    def initTableWidget(self):
        self.indexedItems.setColumnCount(2)

        # set the headers' titles and stretch the last section
        head1 = QTableWidgetItem("Indexed items")
        head2 = QTableWidgetItem("Exceptions")
        self.indexedItems.setHorizontalHeaderItem(0, head1)
        self.indexedItems.setHorizontalHeaderItem(1, head2)
        self.indexedItems.horizontalHeader().setStretchLastSection(True)

        # hide vertical header and grid, remove editable mode
        self.indexedItems.verticalHeader().hide()
        self.indexedItems.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.indexedItems.setShowGrid(False)
        self.indexedItems.setAlternatingRowColors(True)
        self.indexedItems.setSelectionBehavior(QAbstractItemView.SelectRows)

    # ### FOR TESTING ###
    def load_items(self):
        item1 = QTableWidgetItem(QIcon(":/folder.png"), "Dir 1")
        self.indexedItems.setItem(0, 0, item1)
        self.indexedItems.setItem(1, 0, QTableWidgetItem(QIcon(":/folder.png"), "Dir2"))
        self.indexedItems.setItem(1, 1, QTableWidgetItem("Dir2.1, Dir2.2"))
        self.indexedItems.setItem(2, 0, QTableWidgetItem(QIcon(":/folder.png"), "Dir3"))

    def indexItems(self, changed):
        """
        Open the dialog box to modify index.
        """
        self.adv_index.tabWidget.setCurrentIndex(0)

        #self.adv_index.model.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.adv_index.model.root_item = self.model.root_item
        #self.adv_index.model.emit(SIGNAL("layoutChanged()"))
        self.adv_index.exec_()
        # self.adv_index.model.setCh(False)

    def advanceOpt(self, changed):
        """
        Open the dialog box to configure the index engine.
        """
        self.adv_index.tabWidget.setCurrentIndex(1)


        #self.adv_index.model.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.adv_index.model.root_item = self.model.root_item
        #self.adv_index.model.emit(SIGNAL("layoutChanged()"))
        # self.adv_index.model.setCh(True)
        self.adv_index.exec_()
        #elf.adv_index.model.setCh(False)

    def translation(self):
        pass

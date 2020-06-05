'''python
'''

from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
from os import stat
from collections import OrderedDict


import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om

import os
import datetime


# GENERAL VARS
version = '0.1.0'
path = '/Users/alberto/Desktop/BWtest/'




def getMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    mainWindow = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return mainWindow


class modelLoader(QtWidgets.QMainWindow):

    def __init__(self, parent=getMainWindow()):
        super(modelLoader, self).__init__(parent, QtCore.Qt.WindowStaysOnTopHint)

        # Creates object, Title Name and Adds a QtWidget as our central widget/Main Layout
        self.setObjectName('modelLoaderUI')
        self.setWindowTitle('Model Loader' + ' ' + 'v' + version)
        mainLayout = QtWidgets.QWidget(self)
        self.setCentralWidget(mainLayout)

        # Adding a Horizontal layout to divide the UI in two columns
        columns = QtWidgets.QHBoxLayout(mainLayout)

        # Creating 2 vertical layout for the sanity checks and one for the report
        self.col1 = QtWidgets.QVBoxLayout()
        #self.col2 = QtWidgets.QVBoxLayout()

        # Set columns for each layout using stretch policy to psudo fixed width for the 'checks' layout
        columns.addLayout(self.col1, 1)
        #columns.addLayout(self.col2, 2)

        # Adding UI ELEMENTS IN col1
        layout1 = QtWidgets.QVBoxLayout()
        self.col1.addLayout(layout1)

        # Combobox selector for asset type
        self.assetTypeSelector = QtWidgets.QComboBox(self)
        self.assetTypeSelector.setMinimumWidth(250)        
        self.assetTypeSelector.addItem('Character', '1_CH')
        self.assetTypeSelector.addItem('Background', '2_BG')
        self.assetTypeSelector.addItem('Prop', '3_PR')
        self.assetTypeSelector.activated[str].connect(self.assetTypeSel)
     
        # Input for filter list of assets
        self.assetSearchBox = QtWidgets.QLineEdit('', self)
        self.assetRegex = QtCore.QRegExp('[0-9A-Za-z_]+')
        self.assetValidator = QtGui.QRegExpValidator(self.assetRegex)
        self.assetSearchBox.setValidator(self.assetValidator)
        self.assetSearchBox.textChanged.connect(self.assetFilter)

        # List of assets
        self.assetList = QtWidgets.QListWidget(self)
        self.assetList.setMinimumWidth(250)
        self.assetList.itemClicked.connect(self.assetSelection)

        # Labels for scene info
        self.sceneLabel = QtWidgets.QLabel('Scene: ', self)
        self.sizeLabel = QtWidgets.QLabel('Size: ', self)
        self.dateLabel = QtWidgets.QLabel('Date: ', self)

        # Status message bar
        self.msgLabel = QtWidgets.QLabel('', self)

        # Button for import
        self.importBtn = QtWidgets.QPushButton('Import')
        self.importBtn.clicked.connect(self.importScene)

        # Add elements to layout
        layout1.addWidget(self.assetTypeSelector)
        layout1.addWidget(self.assetSearchBox)
        layout1.addWidget(self.assetList)
        layout1.addWidget(self.sceneLabel)
        layout1.addWidget(self.sizeLabel)
        layout1.addWidget(self.dateLabel)
        layout1.addWidget(self.msgLabel)
        layout1.addWidget(self.importBtn)

    
    def restoreLabels(self):
        self.sceneLabel.setText('Scene: ')
        self.sizeLabel.setText('Size: ')
        self.dateLabel.setText('Date: ')
      
    
    def assetTypeSel(self):
        global directory
        userdata = self.assetTypeSelector.itemData(self.assetTypeSelector.currentIndex())
        directory = path + userdata
        folders = []
        folders.append(os.listdir(directory))
        
        self.restoreLabels()
        self.msgLabel.clear()
        self.assetList.clear()

        for f in folders:
            self.assetList.addItems(f)
        return folders


    def assetSelection(self, item):
        global sceneFullPath
        global asset

        asset = format(item.text())
        sceneFullPath = directory + '/' + asset + '/08_MODEL/v01/' + asset + '_model_v01.ma'
        scene = asset + '_model_v01.ma'
        size = os.stat(sceneFullPath).st_size
        mtime = os.stat(sceneFullPath).st_mtime
        date = datetime.datetime.fromtimestamp(mtime).strftime('%d/%m/%Y %H:%M')
        
        self.sceneLabel.setText('Scene: ' + scene)
        self.sizeLabel.setText('Size: ' + str(size/1024) + ' KB')
        self.dateLabel.setText('Date: ' + str(date))
        return asset


    def assetFilter(self):
        textFilter = str(self.assetSearchBox.text()).lower()
        if not textFilter:
            for row in range(self.assetList.count()):
                self.assetList.setRowHidden(row, False)
        else:
            for row in range(self.assetList.count()):
                if textFilter in str(self.assetList.item(row).text()).lower():
                    self.assetList.setRowHidden(row, False)
                else:
                    self.assetList.setRowHidden(row, True)


    def importScene(self):
        if self.assetList.currentItem():
            mel.eval('MLdeleteUnused;')
            cmds.file(sceneFullPath, i=True, gr=True, dns=False, gn=str(asset))
            self.msgLabel.setText('Model imported successfully!')
        else:    
            self.msgLabel.setText('No scene selected')
            self.msgLabel.setStyleSheet('color:orange; text-align:center;')
        

 
    


        


if __name__ == '__main__':
  try:
      win.close()
  except:
      pass
  win = modelLoader(parent=getMainWindow())
  win.show()
  win.raise_()

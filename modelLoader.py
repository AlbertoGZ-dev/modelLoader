'''
-----------------------------------------
modelLoader for BWater pipeline 
Gets model published to import 
in current scene with no namespace.

Autor: AlbertoGZ
Email: albertogzonline@gmail.com
-----------------------------------------
'''

from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
from os import stat
from collections import OrderedDict


import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
import shiboken2

import os
import datetime


# GENERAL VARS
version = '0.1.1'
winWidth = 400
winHeight = 300
path = '/Users/alberto/Desktop/BWtest/'
#path = 'W:/PRODUCTIONS/DIDDL/PRE/'



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
        
        # Adding a Horizontal layout to divide the UI in columns
        columns = QtWidgets.QHBoxLayout(mainLayout)

        # Creating N vertical layout
        self.col1 = QtWidgets.QVBoxLayout()
        self.col2 = QtWidgets.QVBoxLayout()
        self.col3 = QtWidgets.QVBoxLayout()

        # Set columns for each layout using stretch policy
        columns.addLayout(self.col1, 1)
        columns.addLayout(self.col2, 1)
        columns.addLayout(self.col3, 1)
        
        # Adding UI elements
        layout1 = QtWidgets.QVBoxLayout()
        layout2A = QtWidgets.QHBoxLayout()
        layout2B = QtWidgets.QVBoxLayout()
        layout3 = QtWidgets.QVBoxLayout()

        self.col1.addLayout(layout1)
        self.col2.addLayout(layout2A)
        self.col2.addLayout(layout2B)
        self.col3.addLayout(layout3)


        ### ASSET UI ELEMENTS
        #
        # Combobox selector for asset type
        self.assetTypeSelector = QtWidgets.QComboBox(self)
        self.assetTypeSelector.setMinimumWidth(250)        
        self.assetTypeSelector.addItem('Character', '1_CH')
        self.assetTypeSelector.addItem('Background', '2_BG')
        self.assetTypeSelector.addItem('Prop', '3_PR')
        self.assetTypeSelector.activated[str].connect(self.assetTypeSel)
     
        # SearchBox input for filter ASSET list
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
        self.importBtn.setEnabled(False)
        self.importBtn.clicked.connect(self.importScene)


        #### OBJECT UI ELEMENTS
        #
        # SearchBox input for filter OBJECT list
        self.objectSearchBox = QtWidgets.QLineEdit('', self)
        self.objectRegex = QtCore.QRegExp('[0-9A-Za-z_]+')
        self.objectValidator = QtGui.QRegExpValidator(self.objectRegex)
        self.objectSearchBox.setValidator(self.objectValidator)
        self.objectSearchBox.textChanged.connect(self.objectFilter)

        # List of objects
        self.objectsList = QtWidgets.QListWidget(self)
        self.objectsList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.objectsList.setMinimumWidth(200)
        self.objectsList.itemClicked.connect(self.objectsSelection)

        # Button for list objects (preload scene)
        self.preloadBtn = QtWidgets.QPushButton('List objects')
        self.preloadBtn.setEnabled(False)
        self.preloadBtn.setMinimumWidth(140)
        self.preloadBtn.setFixedHeight(18)
        self.preloadBtn.clicked.connect(self.preloadModel)

        # Button for clear objects list (unload scene)
        self.clearObjectsListBtn = QtWidgets.QPushButton('Clear')
        self.clearObjectsListBtn.setEnabled(False)
        self.clearObjectsListBtn.setFixedWidth(60)
        self.clearObjectsListBtn.setFixedHeight(18)
        self.clearObjectsListBtn.clicked.connect(self.unloadModel)

        ### Ghost panel
        self.ghost = QtWidgets.QLabel('')
        self.ghost.setFixedWidth(300)
        self.ghost.setFixedHeight(300)
        self.ghost.setStyleSheet('background-color:green')
        
        '''
        ### Maya viewport embed to Qt
        layout3.setObjectName('viewportLayout')
        cmds.setParent('viewportLayout')
        paneLayoutName = cmds.paneLayout()
        modelPanelName = cmds.modelEditor('embeddedModelEditor#', cam='persp', da='smoothShaded', gr=False, hud=False)
        ptr = omui.MQtUtil.findControl(paneLayoutName)
        viewport = shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)
        '''

        # Add status bar widget
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        #self.statusBar.setVisible(False)

        # Add elements to layout
        layout1.addWidget(self.assetTypeSelector)
        layout1.addWidget(self.assetSearchBox)
        layout1.addWidget(self.assetList)
        layout1.addWidget(self.sceneLabel)
        layout1.addWidget(self.sizeLabel)
        layout1.addWidget(self.dateLabel)
        layout1.addWidget(self.msgLabel)
        layout1.addWidget(self.importBtn)
        
        layout2A.addWidget(self.preloadBtn)
        layout2A.addWidget(self.clearObjectsListBtn)
        layout2B.addWidget(self.objectSearchBox)
        layout2B.addWidget(self.objectsList)
        
        #layout3.addWidget(viewport)
        #viewport.setVisible(False)
        self.resize(winWidth, winHeight)

    


    ### Combobox selector for asset type
    def assetTypeSel(self):
        global directory

        self.restoreLabels()
        self.assetList.clear()
        self.objectsList.clear()
        self.importBtn.setEnabled(False)
        if cmds.objExists('___tmp___*'):
            self.unloadModel()

        assetType = self.assetTypeSelector.itemData(self.assetTypeSelector.currentIndex())
        directory = path + assetType
        folders = []
        folders.append(os.listdir(directory))
        
        # Load list of folders from select asset type
        for f in folders:
            self.assetList.addItems(f)
        return folders


    ### Actions when asset is selected in list
    def assetSelection(self, item):
        global sceneFullPath
        global asset

        self.objectsList.clear()
        if cmds.objExists('___tmp___*'):
            self.unloadModel()

        asset = format(item.text())
        sceneFullPath = directory + '/' + asset + '/08_MODEL/v01/' + asset + '_model_v01.ma'
        scene = asset + '_model_v01.ma'
        size = os.stat(sceneFullPath).st_size
        mtime = os.stat(sceneFullPath).st_mtime
        date = datetime.datetime.fromtimestamp(mtime).strftime('%d/%m/%Y %H:%M')
        
        self.sceneLabel.setText('Scene: ' + scene)
        self.sizeLabel.setText('Size: ' + str(size/1024) + ' KB')
        self.dateLabel.setText('Date: ' + str(date))

        self.importBtn.setEnabled(True)
        self.preloadBtn.setEnabled(True)
        return asset

    
    ### Filter by typing for ASSET list
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
    
     ### Filter by typing for OBJECTS list
    def objectFilter(self):
        textFilter = str(self.objectSearchBox.text()).lower()
        if not textFilter:
            for row in range(self.objectsList.count()):
                self.objectsList.setRowHidden(row, False)
        else:
            for row in range(self.objectsList.count()):
                if textFilter in str(self.objectsList.item(row).text()).lower():
                    self.objectsList.setRowHidden(row, False)
                else:
                    self.objectsList.setRowHidden(row, True)

    
    ### Actions for import button
    def importScene(self):
        # Check if any objects is selected; then import them 
        if self.objectsList.currentItem():
            mel.eval('MLdeleteUnused;')
            cmds.select(objs)
            cmds.group(n=asset, w=True)
            self.objectsList.clear()
            self.unloadModel()
            self.statusBar.setVisible(True)
            self.statusBar.showMessage('Selected objects from model imported successfully!', 4000)
        # If no object select then import all model
        elif self.assetList.currentItem():
            mel.eval('MLdeleteUnused;')
            cmds.file(sceneFullPath, i=True, gr=True, dns=False, gn=str(asset))
            self.statusBar.showMessage('Model imported successfully!', 4000)
        else:    
            self.statusBar.showMessage('No scene selected', 4000)


    ### Select objects in objects list
    def objectsSelection(self, item):
        global objs
        items = self.objectsList.selectedItems()
        objs = []
        for i in list(items):
            objs.append(str(i.text()))

    
    ### Actions for list objects button
    def preloadModel(self):
        global grpTemp
        grpTemp = '___tmp___'
        
        if self.assetList.currentItem():
            mel.eval('MLdeleteUnused;')
            cmds.file(sceneFullPath, i=True, gr=True, dns=False, gn=grpTemp, ifr=True)
            cmds.select(grpTemp+'*')
            cmds.hide(grpTemp+'*')
            mel.eval('setAttr ___tmp___.hiddenInOutliner true;AEdagNodeCommonRefreshOutliners();')
            listObjects = cmds.ls(grpTemp, dag=True, sn=True, s=False, tr=True)
            listObjects.remove(str(grpTemp))
            self.objectsList.addItems(listObjects)
        else:    
            self.statusBar.showMessage('No object selected', 4000)
        
        self.preloadBtn.setEnabled(False)
        self.clearObjectsListBtn.setEnabled(True)
    


    def restoreLabels(self):
        self.sceneLabel.setText('Scene: ')
        self.sizeLabel.setText('Size: ')
        self.dateLabel.setText('Date: ')
      
    
    def unloadModel(self):
        cmds.delete(grpTemp+'*')
        mel.eval('MLdeleteUnused;')
        self.cleanScene()
        self.objectsList.clear()
        self.preloadBtn.setEnabled(True)
        self.clearObjectsListBtn.setEnabled(False)

    
    def cleanScene(self):
        cmds.delete('*_hyperShadePrimaryNodeEditorSavedTabsInfo*')
        cmds.delete('*ConfigurationScriptNode*')
        

    def closeEvent(self, event):
        self.unloadModel()
        self.cleanScene()


if __name__ == '__main__':
  try:
      win.close()
  except:
      pass
  win = modelLoader(parent=getMainWindow())
  win.show()
  win.raise_()

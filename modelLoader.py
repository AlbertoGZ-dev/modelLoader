'''
-----------------------------------------
modelLoader for BWater pipeline 
Gets model published to import 
in current scene with no namespaces.

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
import re


# GENERAL VARS
version = '0.1.4'
winWidth = 350
winHeight = 300
red = '#872323'
green = '#207527'

# BWATER VARS
#testing path
path = '/Users/alberto/Desktop/BWtest/W/01_PRODUCTIONS/01_TVSERIES/03_DIDDL/1_PRE/'
#production path
#path = 'W:/01_PRODUCTIONS/01_TVSERIES/03_DIDDL/1_PRE/'
taskDir = '08_MODEL'
versionDir = 'v01'
mayaExt = '.ma'
sceneSuffix = '_model_' + versionDir + mayaExt


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
        #self.col3 = QtWidgets.QVBoxLayout()

        # Set columns for each layout using stretch policy
        columns.addLayout(self.col1, 1)
        columns.addLayout(self.col2, 1)
        #columns.addLayout(self.col3, 1)
        
        # Adding UI elements
        layout1 = QtWidgets.QVBoxLayout()
        layout2A = QtWidgets.QHBoxLayout()
        layout2B = QtWidgets.QVBoxLayout()
        #layout3 = QtWidgets.QVBoxLayout()

        self.col1.addLayout(layout1)
        self.col2.addLayout(layout2A)
        self.col2.addLayout(layout2B)
        #self.col3.addLayout(layout3)


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

        # Cleaning button
        self.cleanBtn = QtWidgets.QPushButton('Clean')
        self.cleanBtn.clicked.connect(self.removePrefix)


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
        self.objectsList.setMinimumWidth(170)
        self.objectsList.itemClicked.connect(self.objectsSelection)

        # Button for list objects (preload model scene)
        self.listObjectsBtn = QtWidgets.QPushButton('List objects')
        self.listObjectsBtn.setEnabled(False)
        self.listObjectsBtn.setMinimumWidth(110)
        self.listObjectsBtn.setFixedHeight(18)
        self.listObjectsBtn.clicked.connect(self.preloadModel)

        # Button for clear objects list (unload model scene)
        self.clearObjectsListBtn = QtWidgets.QPushButton('Clear')
        self.clearObjectsListBtn.setEnabled(False)
        self.clearObjectsListBtn.setFixedWidth(60)
        self.clearObjectsListBtn.setFixedHeight(18)
        self.clearObjectsListBtn.clicked.connect(self.unloadModel)

        
        ### Test panel
        self.viewport = QtWidgets.QLabel('')
        self.viewport.setFixedWidth(300)
        self.viewport.setFixedHeight(300)
        self.viewport.setStyleSheet('background-color:gray')
        
        '''
        ### Maya viewport embed to Qt
        layout3.setObjectName('viewportLayout')
        cmds.setParent('viewportLayout')
        paneLayoutName = cmds.paneLayout()
        modelPanelName = cmds.modelEditorl('embeddedModelEditor1', cam='persp')
        ptr = omui.MQtUtil.findControl(paneLayoutName)
        self.viewport = shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)
        '''        

        # Add status bar widget
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.messageChanged.connect(self.statusChanged)


        # Add elements to layout
        layout1.addWidget(self.assetTypeSelector)
        layout1.addWidget(self.assetSearchBox)
        layout1.addWidget(self.assetList)
        layout1.addWidget(self.sceneLabel)
        layout1.addWidget(self.sizeLabel)
        layout1.addWidget(self.dateLabel)
        layout1.addWidget(self.msgLabel)
        layout1.addWidget(self.importBtn)
        #layout1.addWidget(self.cleanBtn)
        
        layout2A.addWidget(self.listObjectsBtn)
        layout2A.addWidget(self.clearObjectsListBtn)
        layout2B.addWidget(self.objectSearchBox)
        layout2B.addWidget(self.objectsList)
        
        #layout3.addWidget(self.viewport)
        #viewport.setVisible(False)
        self.resize(winWidth, winHeight)

    


    ### Combobox selector for asset type
    def assetTypeSel(self):
        global directory

        self.restoreLabels()
        self.assetList.clear()
        self.unloadModel()
        self.importBtn.setEnabled(False)
        self.listObjectsBtn.setEnabled(False)

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

        asset = format(item.text())
        sceneFullPath = directory + '/' + asset + '/' + taskDir + '/' + versionDir + '/' + asset + sceneSuffix
        scene = asset + sceneSuffix
        size = os.stat(sceneFullPath).st_size
        mtime = os.stat(sceneFullPath).st_mtime
        date = datetime.datetime.fromtimestamp(mtime).strftime('%d/%m/%Y %H:%M')
        
        self.sceneLabel.setText('Scene: ' + scene)
        self.sizeLabel.setText('Size: ' + str(size/1024) + ' KB')
        self.dateLabel.setText('Date: ' + str(date))

        self.importBtn.setEnabled(True)
        self.listObjectsBtn.setEnabled(True)
        
        self.unloadModel()

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
            try:
                mel.eval('MLdeleteUnused;')
                cmds.select(objs)
                cmds.group(n=asset+'sel1', w=True)
                self.removePrefix()
                self.cleanScene()
                self.objectsList.clear()
                self.unloadModel()
                self.statusBar.setStyleSheet('background-color:' + green)
                self.statusBar.showMessage('Selected objects from model imported successfully!', 4000)
            except:
                self.statusBar.setStyleSheet('background-color:' + red)
                self.statusBar.showMessage('Object(s) with same name already in scene', 4000)
        # If no object select then import all model
        elif self.assetList.currentItem():
            mel.eval('MLdeleteUnused;')
            cmds.file(sceneFullPath, i=True, gr=True, dns=False, gn=str(asset+'tmp1'))
            self.removePrefix()
            self.cleanScene()
            self.statusBar.setStyleSheet('background-color:' + green)
            self.statusBar.showMessage('Model imported successfully!', 4000)
        else:
            self.statusBar.setStyleSheet('background-color:' + red)
            self.statusBar.showMessage('No scene selected', 4000)


    ### Select objects in objects list
    def objectsSelection(self, item):
        global objs
        items = self.objectsList.selectedItems()
        objs = []
        for i in list(items):
            objs.append(i.text())
        objs.sort()

    
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
            listObjects = cmds.listRelatives(grpTemp, s=False)
            self.objectsList.addItems(listObjects)
        else:
            self.statusBar.setStyleSheet('background-color:' + red)
            self.statusBar.showMessage('No object selected', 4000)
        
        self.listObjectsBtn.setEnabled(False)
        self.clearObjectsListBtn.setEnabled(True)
    

    def restoreLabels(self):
        self.sceneLabel.setText('Scene: ')
        self.sizeLabel.setText('Size: ')
        self.dateLabel.setText('Date: ')
    

    def statusChanged(self, args):
        if not args:
            self.statusBar.setStyleSheet('background-color:none')
      

    def unloadModel(self):
        #self.cleanScene()
        self.objectsList.clear()
        self.listObjectsBtn.setEnabled(True)
        self.clearObjectsListBtn.setEnabled(False)
        if cmds.objExists('___tmp___*'):
            cmds.delete('___tmp___*')
        mel.eval('MLdeleteUnused;')

    
    def cleanScene(self):
        node1 = '*_hyperShadePrimaryNodeEditorSavedTabsInfo*'
        node2 = '*ConfigurationScriptNode*'
        if cmds.objExists(node1):
            cmds.delete(node1)
        if cmds.objExists(node2):
            cmds.delete(node2)

    
    # Prevent groupname as prefix of any node
    def removePrefix(self):
        groupname = cmds.ls(asset + '_*')
        for gn in groupname:
            new = gn.split(str(asset + '_model_v01_'))
            cmds.rename(gn, new[1])


    def closeEvent(self, event):
        self.unloadModel()
        self.cleanScene()
        self.removePrefix()


if __name__ == '__main__':
  try:
      win.close()
  except:
      pass
  win = modelLoader(parent=getMainWindow())
  win.show()
  win.raise_()

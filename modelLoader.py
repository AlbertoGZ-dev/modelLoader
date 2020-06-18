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
import time
import re


# GENERAL VARS
version = '0.1.5'
winWidth = 400
winHeight = 300
red = '#872323'
green = '#207527'

# BWATER VARS 
testPath = '/Users/alberto/Desktop/BWtest/W/01_PRODUCTIONS/01_TVSERIES/03_DIDDL/1_PRE/'
prodPath = 'W:/01_PRODUCTIONS/01_TVSERIES/03_DIDDL/1_PRE/'
path = testPath
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
        self.col3 = QtWidgets.QVBoxLayout()

        # Set columns for each layout using stretch policy
        columns.addLayout(self.col1, 2)
        columns.addLayout(self.col2, 1)
        columns.addLayout(self.col3, 2)
        
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
        self.assetComboBox = QtWidgets.QComboBox(self)
        self.assetComboBox.setMinimumWidth(250)        
        self.assetComboBox.addItem('Character', '1_CH')
        self.assetComboBox.addItem('Background', '2_BG')
        self.assetComboBox.addItem('Prop', '3_PR')
        self.assetComboBox.activated[str].connect(self.assetTypeSel)
     
        # SearchBox input for filter ASSET list
        self.assetSearchBox = QtWidgets.QLineEdit('', self)
        self.assetRegex = QtCore.QRegExp('[0-9A-Za-z_]+')
        self.assetValidator = QtGui.QRegExpValidator(self.assetRegex)
        self.assetSearchBox.setValidator(self.assetValidator)
        self.assetSearchBox.textChanged.connect(self.assetFilter)

        # List of assets
        self.assetQList = QtWidgets.QListWidget(self)
        self.assetQList.setMinimumWidth(250)
        self.assetQList.itemClicked.connect(self.assetSel)

        # Labels for scene info
        self.sceneLabel = QtWidgets.QLabel('Scene: ', self)
        self.sizeLabel = QtWidgets.QLabel('Size: ', self)
        self.dateLabel = QtWidgets.QLabel('Date: ', self)

        # Status message bar
        self.msgLabel = QtWidgets.QLabel('', self)

        # Button for import
        self.importBtn = QtWidgets.QPushButton('Import')
        self.importBtn.setEnabled(False)
        self.importBtn.clicked.connect(self.importAsset)

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
        self.objectQList = QtWidgets.QListWidget(self)
        self.objectQList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.objectQList.setMinimumWidth(170)
        self.objectQList.itemClicked.connect(self.objectSel)

        # Button for list objects (preload model scene)
        self.objectListBtn = QtWidgets.QPushButton('List objects')
        self.objectListBtn.setEnabled(False)
        self.objectListBtn.setMinimumWidth(110)
        self.objectListBtn.setFixedHeight(18)
        self.objectListBtn.clicked.connect(self.objectLoad)

        # Button for clear objects list (unload model scene)
        self.objectListClearBtn = QtWidgets.QPushButton('Clear')
        self.objectListClearBtn.setEnabled(False)
        self.objectListClearBtn.setFixedWidth(60)
        self.objectListClearBtn.setFixedHeight(18)
        self.objectListClearBtn.clicked.connect(self.objectUnload)

        # Check for open viewer to show object(s)
        self.objectViewCheckbox = QtWidgets.QCheckBox('Object viewer')
        self.objectViewCheckbox.setEnabled(False)
        self.objectViewCheckbox.clicked.connect(self.showViewer)

        
        # Add status bar widget
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.messageChanged.connect(self.statusChanged)


        ### MAYA embedding modelEditor widget in Pyside layout
        self.paneLayoutName = cmds.paneLayout()
        global modelEditorName
        global viewer
        
        self.createCam()

        #objectViewerCam = 'objectViewerCam1'
        modelEditorName = 'modelEditor#'
        viewer = cmds.modelEditor(modelEditorName, cam=objectViewerCam, hud=False, grid=False, da='smoothShaded', sel=False)
        self.ptr = omui.MQtUtil.findControl(self.paneLayoutName)            
        self.objectViewer = shiboken2.wrapInstance(long(self.ptr), QtWidgets.QWidget)
        self.objectViewer.setVisible(False)


        # Add elements to layout
        layout1.addWidget(self.assetComboBox)
        layout1.addWidget(self.assetSearchBox)
        layout1.addWidget(self.assetQList)
        layout1.addWidget(self.sceneLabel)
        layout1.addWidget(self.sizeLabel)
        layout1.addWidget(self.dateLabel)
        layout1.addWidget(self.msgLabel)
        layout1.addWidget(self.importBtn)
        
        layout2A.addWidget(self.objectListBtn)
        layout2A.addWidget(self.objectListClearBtn)
        layout2B.addWidget(self.objectSearchBox)
        layout2B.addWidget(self.objectQList)
        layout2B.addWidget(self.objectViewCheckbox)
        
        layout3.addWidget(self.objectViewer)
        
        self.resize(winWidth, winHeight)

    


    ### Combobox selector for asset type
    def assetTypeSel(self):
        global directory

        self.restoreLabels()
        self.assetQList.clear()
        self.objectUnload()
        self.importBtn.setEnabled(False)
        self.objectListBtn.setEnabled(False)

        assetType = self.assetComboBox.itemData(self.assetComboBox.currentIndex())
        directory = path + assetType
        assetList = []
        assetList.append(os.listdir(directory))
        
        # Load list of folders from select asset type
        for asset in assetList:
            asset.sort()
            self.assetQList.addItems(asset)
        return assetList


    ### Human redeable bytes conversion
    def convert_bytes(self, num):
        step_unit = 1000.0 #1024 bad the size

        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < step_unit:
                return "%3.1f %s" % (num, x)
            num /= step_unit
    

    ### Actions when asset is selected in list
    def assetSel(self, item):
        global sceneFullPath
        global asset

        asset = format(item.text())
        sceneFullPath = directory + '/' + asset + '/' + taskDir + '/' + versionDir + '/' + asset + sceneSuffix
        scene = asset + sceneSuffix
        size = os.stat(sceneFullPath).st_size
        mtime = os.stat(sceneFullPath).st_mtime
        date = datetime.datetime.fromtimestamp(mtime).strftime('%d/%m/%Y %H:%M')

        humansize = self.convert_bytes(size)

        self.sceneLabel.setText('Scene: ' + scene)
        self.sizeLabel.setText('Size: ' + str(humansize))
        self.dateLabel.setText('Date: ' + str(date))

        self.importBtn.setEnabled(True)
        self.objectListBtn.setEnabled(True)
        
        self.objectUnload()

        return asset


    

    ### Filter by typing for ASSET list
    def assetFilter(self):
        textFilter = str(self.assetSearchBox.text()).lower()
        if not textFilter:
            for row in range(self.assetQList.count()):
                self.assetQList.setRowHidden(row, False)
        else:
            for row in range(self.assetQList.count()):
                if textFilter in str(self.assetQList.item(row).text()).lower():
                    self.assetQList.setRowHidden(row, False)
                else:
                    self.assetQList.setRowHidden(row, True)
    
     ### Filter by typing for OBJECTS list
    def objectFilter(self):
        textFilter = str(self.objectSearchBox.text()).lower()
        if not textFilter:
            for row in range(self.objectQList.count()):
                self.objectQList.setRowHidden(row, False)
        else:
            for row in range(self.objectQList.count()):
                if textFilter in str(self.objectQList.item(row).text()).lower():
                    self.objectQList.setRowHidden(row, False)
                else:
                    self.objectQList.setRowHidden(row, True)

    
    ### Actions for import button
    def importAsset(self):
        # Check if any objects is selected; then import them
        if self.objectQList.currentItem():
            try:
                mel.eval('MLdeleteUnused;')
                cmds.select(objs)
                cmds.group(n=asset+'sel1', w=True)
                self.removePrefix()
                self.cleanScene()
                self.objectQList.clear()
                self.objectUnload()
                self.statusBar.setStyleSheet('background-color:' + green)
                self.statusBar.showMessage('Selected objects from model imported successfully!', 4000)
            except:
                self.statusBar.setStyleSheet('background-color:' + red)
                self.statusBar.showMessage('Object(s) with same name already in scene', 4000)
        # If no object select then import all model
        elif self.assetQList.currentItem():
            mel.eval('MLdeleteUnused;')
            cmds.file(sceneFullPath, i=True, gr=True, dns=False, gn=str(asset+'tmp1'))
            self.removePrefix()
            self.cleanScene()
            self.statusBar.setStyleSheet('background-color:' + green)
            self.statusBar.showMessage('Model imported successfully!', 4000)
        else:
            self.statusBar.setStyleSheet('background-color:' + red)
            self.statusBar.showMessage('No scene selected', 4000)


    def hideViewer(self):
        self.objectViewer.setVisible(False)
        winWidth = 400
        self.resize(winWidth, winHeight)


    def createCam(self):
            global objectViewerCam
            objectViewerCam = 'objectViewerCam1'
            cmds.camera(name=objectViewerCam)
            cmds.xform(t=(28.000, 21.000, 28.000), ro=(-27.938, 45.0, -0.0) )
            #cmds.hide(objectViewerCam)


    def showViewer(self):
        if self.objectViewCheckbox.isChecked():
            
            self.objectViewer.setVisible(True)
            winWidth = 800
            self.resize(winWidth, winHeight)

            if self.objectQList.currentItem():
                cmds.showHidden(grpTemp+'*')
                cmds.select(objs)
                cmds.isolateSelect(viewer, s=False)
                cmds.isolateSelect(viewer, s=True)
                cmds.viewFit(objectViewerCam)
                #cmds.refresh()
        else:
            self.hideViewer()




    ### Select objects in objects list
    def objectSel(self, item):
        global objs
        items = self.objectQList.selectedItems()
        objs = []
        for i in list(items):
            objs.append(i.text())
        self.statusBar.showMessage(str(objs), 4000)

        cmds.showHidden(grpTemp+'*')
        cmds.select(objs)
        cmds.isolateSelect(viewer, s=False)
        cmds.isolateSelect(viewer, s=True)
        cmds.viewFit(objectViewerCam)
        #cmds.refresh()

        
            
    
    ### Actions for list objects button
    def objectLoad(self):
        global grpTemp
        grpTemp = '___tmp___'
        
        if self.assetQList.currentItem():
            mel.eval('MLdeleteUnused;')
            cmds.file(sceneFullPath, i=True, gr=True, dns=False, gn=grpTemp, ifr=True)
            cmds.select(grpTemp+'*')
            cmds.hide(grpTemp+'*')
            #mel.eval('setAttr ___tmp___.hiddenInOutliner true;AEdagNodeCommonRefreshOutliners();')
            objectList = cmds.listRelatives(grpTemp, s=False)
            objectList.sort()
            self.objectQList.addItems(objectList)
            self.objectViewCheckbox.setEnabled(True)
        else:
            self.statusBar.setStyleSheet('background-color:' + red)
            self.statusBar.showMessage('No object selected', 4000)
        
        self.objectListBtn.setEnabled(False)
        self.objectListClearBtn.setEnabled(True)
    

    def restoreLabels(self):
        self.sceneLabel.setText('Scene: ')
        self.sizeLabel.setText('Size: ')
        self.dateLabel.setText('Date: ')
    

    def statusChanged(self, args):
        if not args:
            self.statusBar.setStyleSheet('background-color:none')
      

    def objectUnload(self):
        self.objectQList.clear()
        self.objectListBtn.setEnabled(True)
        self.objectListClearBtn.setEnabled(False)
        self.objectViewCheckbox.setEnabled(False)
        
        if self.objectViewCheckbox.isChecked():
            self.hideViewer()
            self.objectViewCheckbox.setChecked(False)

        if cmds.objExists('___tmp___*'):
            cmds.delete('___tmp___*')

    
    def cleanScene(self):
        node1 = '*_hyperShadePrimaryNodeEditorSavedTabsInfo*'
        node2 = '*ConfigurationScriptNode*'
        if cmds.objExists(node1):
            cmds.delete(node1)
        if cmds.objExists(node2):
            cmds.delete(node2)
        cmds.delete(objectViewerCam)        
        cmds.deleteUI(modelEditorName+'*')
        mel.eval('MLdeleteUnused;')
        
    
    # Prevent groupname as prefix of any node
    def removePrefix(self):
        groupname = cmds.ls(asset + '_*')
        for gn in groupname:
            new = gn.split(str(asset + '_model_v01_'))
            cmds.rename(gn, new[1])


    def closeEvent(self, event):
        self.objectUnload()
        self.cleanScene()
        #self.removePrefix()



if __name__ == '__main__':
  try:
      win.close()
  except:
      pass
  win = modelLoader(parent=getMainWindow())
  win.show()
  win.raise_()

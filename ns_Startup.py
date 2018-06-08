#ns_Startup v0.1.02

import sys
import os
from PyQt4.QtGui import *
from PyQt4.uic import *
from time import *
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt
import getpass
from functools import partial
import xml.etree.cElementTree as ET
import xml.dom.minidom
import ns_Utility
import subprocess




#############################################################################################
lt = localtime()
jahr, monat, tag = lt[0:3]
ns_date = str(jahr)[2:4]+str(monat).zfill(2)+str(tag).zfill(2)
user = getpass.getuser()
##################################### LOOKUP PATHES #########################################
scriptRoot = sys.path[0]
presetPath = scriptRoot + os.sep + "Presets"
configPath = scriptRoot + os.sep + "Config"
searchPathHoudiniWIN = "C:\Program Files\Side Effects Software"
renderServicePath = "C:\Users\<USER>\AppData\Local\Thinkbox\Deadline10\submitters\HoudiniSubmitter"
searchPathWorkgroups = "L:\Workgroups"
searchPathArnold = searchPathWorkgroups + os.sep + "Workgroups_HTOA"
searchPathRedshift= searchPathWorkgroups + os.sep + "Workgroups_Redshift"
searchPathRSLocalWIN = "C:\ProgramData\Redshift"
deadlinePathWIN = "C:\Users\NS\AppData\Local\Thinkbox\Deadline10\submitters\HoudiniSubmitter"
#############################################################################################


class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)
        self.menu = QtGui.QMenu(parent)
        openAction = self.menu.addAction("Open ns_Startup v0.1.02")
        self.menu.addSeparator()
        exitAction = self.menu.addAction("Exit Tray")
        exitAction.triggered.connect(QtGui.QApplication.quit)
        self.activated.connect(self.openGUI)
        openAction.triggered.connect(self.openGUI)
        self.setContextMenu(self.menu)
        self.setToolTip("ns_Startup Tray v0.1.02")


    def openGUI(self):
        gui.openGUI()


class MainWindow(QtGui.QMainWindow):
    checkerRenderer = []
    checkerWorkgroups = []
    selectedRenderer = []
    selectedWorkgroups = []
    presetFlag = False


    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.gui = uic.loadUi("UI" + os.sep + "ns_Startup.ui")
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.gui.move(resolution.width() - 473, resolution.height() - 980)
        self.gui.closeEvent = self.closeEvent
        self.gui.lineEdit_renderService.setText(renderServicePath)
        self.connect(self.gui.pushButton_savePreset, QtCore.SIGNAL('clicked()'), self.savePresetButton)
        self.connect(self.gui.pushButton_deletePreset, QtCore.SIGNAL('clicked()'), self.deleteCurrentPreset)
        self.connect(self.gui.pushButton_defaultPreset, QtCore.SIGNAL('clicked()'), self.saveDefaultPreset)
        self.connect(self.gui.pushButton_open, QtCore.SIGNAL('clicked()'), self.openApplication)
        self.connect(self.gui.pushButton_setArnoldLic, QtCore.SIGNAL('clicked()'), self.setArnoldLic)
        self.connect(self.gui.pushButton_WOL_0, QtCore.SIGNAL('clicked()'), self.send_WOL_0)
        self.connect(self.gui.pushButton_WOL_1, QtCore.SIGNAL('clicked()'), self.send_WOL_1)
        self.connect(self.gui.pushButton_WOL_2, QtCore.SIGNAL('clicked()'), self.send_WOL_2)
        self.connect(self.gui.pushButton_WOL_3, QtCore.SIGNAL('clicked()'), self.send_WOL_3)
        self.connect(self.gui.pushButton_update, QtCore.SIGNAL('clicked()'), self.fireRoboCopy)
        self.connect(self.gui.pushButton_saveConfig, QtCore.SIGNAL('clicked()'), self.saveConfig)
        self.connect(self.gui.comboBox_preset, QtCore.SIGNAL('currentIndexChanged(int)'), self.setPresetValues)
        self.presetSaveDialog = loadUi("UI" + os.sep + "presetSave.ui")
        self.presetSaveDialog.label_presetLogo.mousePressEvent = self.getPresetLogo
        self.connect(self.presetSaveDialog.pushButton_savePreset, QtCore.SIGNAL('clicked()'), self.getNewPresetNameAndSave)
        self.loadSettings()

    def closeEvent(self, event):
        event.ignore()
        self.gui.hide()


    def hideEvent(self, event):
        self.gui.closeEvent(event)


    def loadSettings(self):
        try:
            if os.path.isfile(configPath + os.sep + "Config.xml"):
                tree = ET.parse(configPath + os.sep + "Config.xml")
                root = tree.getroot()
                #Arnold
                arnoldLic = root.find("Arnold_RLM")
                wol0 = root.find("WOL_0")
                wol1 = root.find("WOL_1")
                wol2 = root.find("WOL_2")
                wol3 = root.find("WOL_3")

                str_out = ""

                self.gui.lineEdit_arnoldLic.setText(arnoldLic.text)

                self.gui.lineEdit_WOL_MAC_0.setText(wol0.get("Address"))
                self.gui.lineEdit_WOL_Des_0.setText(wol0.get("Description"))
                if wol0.get("startUp") ==  "True":
                    ns_Utility.wake_on_lan(str(wol0.get("Address")))
                    self.gui.checkBox_startUp_0.setChecked(True)
                    str_out = str_out + "WOL to " + str(wol0.get("Description")) + "\n"

                self.gui.lineEdit_WOL_MAC_1.setText(wol1.get("Address"))
                self.gui.lineEdit_WOL_Des_1.setText(wol1.get("Description"))
                if wol1.get("startUp") == "True":
                    ns_Utility.wake_on_lan(str(wol1.get("Address")))
                    self.gui.checkBox_startUp_1.setChecked(True)
                    str_out = str_out + "WOL to " + str(wol1.get("Description")) + "\n"

                self.gui.lineEdit_WOL_MAC_2.setText(wol2.get("Address"))
                self.gui.lineEdit_WOL_Des_2.setText(wol2.get("Description"))
                if wol2.get("startUp") == "True":
                    ns_Utility.wake_on_lan(str(wol2.get("Address")))
                    self.gui.checkBox_startUp_3.setChecked(True)
                    str_out = str_out + "WOL to " + str(wol2.get("Description")) + "\n"

                self.gui.lineEdit_WOL_MAC_3.setText(wol3.get("Address"))
                self.gui.lineEdit_WOL_Des_3.setText(wol3.get("Description"))
                if wol3.get("startUp") == "True":
                    ns_Utility.wake_on_lan(str(wol3.get("Address")))
                    self.gui.checkBox_startUp_3.setChecked(True)
                    str_out = str_out + "WOL to " + str(wol3.get("Description")) + "\n"

                os.environ["solidangle_LICENSE"] = str(self.gui.lineEdit_arnoldLic.text())

                trayIcon.showMessage("ns_Startup", str_out, icon=QSystemTrayIcon.Information, msecs = 10000)

        except ValueError:
            pass


    def getPresetLogo(self, event):
        try:
            logoFile = QFileDialog.getOpenFileName(None, str("Logo location"), scriptRoot, str("jpg files (*.jpg)"))
            picPixmap = QtGui.QPixmap(logoFile)
            picPixmapSize = picPixmap.size()
            factor = float(picPixmapSize.width())/float(picPixmapSize.height())
            picPixmap = picPixmap.scaledToWidth(50, mode = Qt.SmoothTransformation)
            picPixmap = picPixmap.scaledToHeight(50/factor, mode = Qt.SmoothTransformation)
            self.presetSaveDialog.label_presetLogo.setStyleSheet("background-color: rgb(0, 0, 0)")
            self.presetSaveDialog.label_presetLogo.setPixmap(picPixmap);
        except:
            pass


    def loadPresetsToCombo(self, presetName):
        self.gui.comboBox_preset.clear()
        try:
            presets = os.listdir(presetPath)
            for i in presets:
                if i.find(".xml") != -1:
                    presetIcon = QtGui.QIcon(QtGui.QPixmap(presetPath + os.sep + i.replace("xml", "jpg")))
                    self.gui.comboBox_preset.addItem(presetIcon, i.replace(".xml", ""))
        except:
            pass
        #FIXME find double execution
        try:
            if presetName != "":
                self.gui.comboBox_preset.setCurrentIndex(self.gui.comboBox_preset.findText(presetName)) # Preset Item
            else:
                self.gui.comboBox_preset.setCurrentIndex(self.gui.comboBox_preset.count() - 1) # Last Item
        except:
            pass


    def getNewPresetNameAndSave(self):
        try:
            if os.path.exists(presetPath):
                pass
            else:
                os.makedirs(presetPath)

            root = ET.Element(str(self.presetSaveDialog.lineEdit_presetName.text()))
            app = ET.SubElement(root, "Application")
            renderer = ET.SubElement(root, "Renderer")
            workgroup = ET.SubElement(root, "Workgroup")
            addParas = ET.SubElement(root, "AdditionalParameters")
            exeVersion = ET.SubElement(root, "exeVersion")
            renderService = ET.SubElement(root, "RenderService")

            ET.SubElement(app, "Application", name="Houdini", version=str(self.gui.comboBox_HOUVersion.currentText()))

            for i in range(0, len(self.selectedRenderer)):
                ET.SubElement(renderer, "Renderer",  name=self.selectedRenderer[i][0], version=self.selectedRenderer[i][1], plugin=self.selectedRenderer[i][2], path=self.selectedRenderer[i][3])

            for i in range(0, len(self.selectedWorkgroups)):
                ET.SubElement(workgroup, "Workgroup", name=self.selectedWorkgroups[i][0], path=self.selectedWorkgroups[i][1])

            ET.SubElement(addParas, "AdditionalParameters", value=str(self.gui.textEdit_addParameters.toPlainText()).replace("\n", "\n___"))
            ET.SubElement(exeVersion, "exeVersion", value=str(self.gui.comboBox_exeVersion.currentText()))
            ET.SubElement(renderService, "RenderService", value=str(self.gui.lineEdit_renderService.text()))

            xmlBeauty = xml.dom.minidom.parseString(ET.tostring(root, encoding='utf8', method='xml'))
            xmlFile = open(presetPath + os.sep + str(self.presetSaveDialog.lineEdit_presetName.text()) + ".xml", "w")
            xmlFile.write(xmlBeauty.toprettyxml())
            xmlFile.close()

            pic = self.presetSaveDialog.label_presetLogo.pixmap()
            pic.save(presetPath + os.sep + str(self.presetSaveDialog.lineEdit_presetName.text()) + ".jpg", "JPG")

            self.loadPresetsToCombo(self.presetSaveDialog.lineEdit_presetName.text())
        except:
            pass

        presetName = self.presetSaveDialog.lineEdit_presetName.text()
        self.presetSaveDialog.close()
        self.loadPresetsToCombo(presetName)

        if self.presetFlag:
            self.saveDefaultPreset()
            self.presetFlag = False


    def deleteCurrentPreset(self):
        try:
            os.remove(presetPath + os.sep + str(self.gui.comboBox_preset.currentText()) + ".xml")
            os.remove(presetPath + os.sep + str(self.gui.comboBox_preset.currentText()) + ".jpg")
        except:
            pass

        self.loadPresetsToCombo("")


    def savePresetButton(self):
        selectedRenderer = []
        selectedWorkgroups = []

        #Look at Lists & AppVersion

        houVersion = self.gui.comboBox_HOUVersion.currentText()

        for i in range(self.gui.listWidget_renderer.rowCount()):
            nameItem = self.gui.listWidget_renderer.item(i, 0)
            versionItem = self.gui.listWidget_renderer.item(i, 1)
            pluginItem = self.gui.listWidget_renderer.item(i, 2)
            pathItem =  self.gui.listWidget_renderer.item(i, 4)

            cellItem = self.gui.listWidget_renderer.cellWidget(i, 3)
            cellLayout = cellItem.layout()
            layoutItem = cellLayout.itemAt(0)
            checkboxItem = layoutItem.widget()
            if checkboxItem.isChecked():
                if nameItem.text() in ["Redshift"]:
                    cellItem = self.gui.listWidget_renderer.cellWidget(i, 2)
                    cellLayout = cellItem.layout()
                    layoutItem = cellLayout.itemAt(0)
                    comboItem = layoutItem.widget()
                    selectedRenderer.append([str(nameItem.text()), str(versionItem.text()), str(comboItem.currentText()), str(pathItem.text())])
                else:
                    selectedRenderer.append([str(nameItem.text()), str(versionItem.text()), str(pluginItem.text()), str(pathItem.text())])

        for i in range(self.gui.listWidget_workgroup.rowCount()):
            nameItem = self.gui.listWidget_workgroup.item(i, 0)
            pathItem = self.gui.listWidget_workgroup.item(i, 2)

            cellItem = self.gui.listWidget_workgroup.cellWidget(i, 1)
            cellLayout = cellItem.layout()
            layoutItem = cellLayout.itemAt(0)
            checkboxItem = layoutItem.widget()
            if checkboxItem.isChecked():
                selectedWorkgroups.append([str(nameItem.text()), str(pathItem.text())])

        self.selectedRenderer = selectedRenderer
        self.selectedWorkgroups = selectedWorkgroups
        self.presetSaveDialog.lineEdit_presetName.setText("")
        self.presetSaveDialog.label_presetLogo.setPixmap(QtGui.QPixmap(scriptRoot + os.sep + "Icons" + os.sep + "noicon.jpg"));
        self.presetSaveDialog.show()


    def saveDefaultPreset(self):
        #TODO implement a mysql solution for none local usage
        selectedRenderer = []
        selectedWorkgroups = []

        for i in range(self.gui.listWidget_renderer.rowCount()):
            nameItem = self.gui.listWidget_renderer.item(i, 0)
            versionItem = self.gui.listWidget_renderer.item(i, 1)
            pluginItem = self.gui.listWidget_renderer.item(i, 2)
            pathItem =  self.gui.listWidget_renderer.item(i, 4)

            cellItem = self.gui.listWidget_renderer.cellWidget(i, 3)
            cellLayout = cellItem.layout()
            layoutItem = cellLayout.itemAt(0)
            checkboxItem = layoutItem.widget()
            if checkboxItem.isChecked():
                if str(nameItem.text()) in ["Redshift"]:
                    cellItem = self.gui.listWidget_renderer.cellWidget(i, 2)
                    cellLayout = cellItem.layout()
                    layoutItem = cellLayout.itemAt(0)
                    comboItem = layoutItem.widget()
                    selectedRenderer.append([str(nameItem.text()), str(versionItem.text()), str(comboItem.currentText()), str(pathItem.text())])
                else:
                    selectedRenderer.append([str(nameItem.text()), str(versionItem.text()), str(pluginItem.text()), str(pathItem.text())])

        for i in range(self.gui.listWidget_workgroup.rowCount()):
            nameItem = self.gui.listWidget_workgroup.item(i, 0)
            pathItem = self.gui.listWidget_workgroup.item(i, 2)

            cellItem = self.gui.listWidget_workgroup.cellWidget(i, 1)
            cellLayout = cellItem.layout()
            layoutItem = cellLayout.itemAt(0)
            checkboxItem = layoutItem.widget()
            if checkboxItem.isChecked():
                selectedWorkgroups.append([str(nameItem.text()), str(pathItem.text())])

        self.selectedRenderer = selectedRenderer
        self.selectedWorkgroups = selectedWorkgroups

        presetName = self.gui.comboBox_preset.currentText()
        if presetName == "":
            reply = QtGui.QMessageBox.question(self, "Warning", "No preset selected. Create one with current values?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.presetFlag = True
                self.savePresetButton()
            else:
                try:
                    if os.path.exists(configPath):
                        pass
                    else:
                        os.makedirs(configPath)

                    root = ET.Element("Default")
                    app = ET.SubElement(root, "Application")
                    renderer = ET.SubElement(root, "Renderer")
                    workgroup = ET.SubElement(root, "Workgroup")
                    addParas = ET.SubElement(root, "AdditionalParameters")
                    exeVersion = ET.SubElement(root, "exeVersion")
                    renderService = ET.SubElement(root, "RenderService")

                    ET.SubElement(app, "Application", name="Houdini", version=str(self.gui.comboBox_HOUVersion.currentText()))

                    for i in range(0, len(self.selectedRenderer)):
                        ET.SubElement(renderer, "Renderer", name=self.selectedRenderer[i][0], version=self.selectedRenderer[i][1], plugin=self.selectedRenderer[i][2], path=self.selectedRenderer[i][3])

                    for i in range(0, len(self.selectedWorkgroups)):
                        ET.SubElement(workgroup, "Workgroup", name=self.selectedWorkgroups[i][0], path=self.selectedWorkgroups[i][1])

                    ET.SubElement(addParas, "AdditionalParameters", value=str(self.gui.textEdit_addParameters.toPlainText()).replace("\n", "\n___"))
                    ET.SubElement(exeVersion, "exeVersion", value=str(self.gui.comboBox_exeVersion.currentText()))
                    ET.SubElement(renderService, "RenderService", value=str(self.gui.lineEdit_renderService.text()))

                    xmlBeauty = xml.dom.minidom.parseString(ET.tostring(root, encoding='utf8', method='xml'))
                    xmlFile = open(configPath + os.sep + "Default.xml", "w")
                    xmlFile.write(xmlBeauty.toprettyxml())
                    xmlFile.close()
                except ValueError:
                    pass

        else:
            try:
                if os.path.exists(configPath):
                    pass
                else:
                    os.makedirs(configPath)

                root = ET.Element(str(presetName))
                app = ET.SubElement(root, "Application")
                renderer = ET.SubElement(root, "Renderer")
                workgroup = ET.SubElement(root, "Workgroup")
                addParas = ET.SubElement(root, "AdditionalParameters")
                exeVersion = ET.SubElement(root, "exeVersion")
                renderService = ET.SubElement(root, "RenderService")

                ET.SubElement(app, "Application", name="Houdini", version=str(self.gui.comboBox_HOUVersion.currentText()))

                for i in range(0, len(self.selectedRenderer)):
                    ET.SubElement(renderer, "Renderer", name=self.selectedRenderer[i][0], version=self.selectedRenderer[i][1], plugin=self.selectedRenderer[i][2], path=self.selectedRenderer[i][3])

                for i in range(0, len(self.selectedWorkgroups)):
                    ET.SubElement(workgroup, "Workgroup", name=self.selectedWorkgroups[i][0], path=self.selectedWorkgroups[i][1])

                ET.SubElement(addParas, "AdditionalParameters", value=str(self.gui.textEdit_addParameters.toPlainText()).replace("\n", "\n___"))
                ET.SubElement(exeVersion, "exeVersion", value=str(self.gui.comboBox_exeVersion.currentText()))
                ET.SubElement(renderService, "RenderService", value=str(self.gui.lineEdit_renderService.text()))

                xmlBeauty = xml.dom.minidom.parseString(ET.tostring(root, encoding='utf8', method='xml'))
                xmlFile = open(configPath + os.sep + "Default.xml", "w")
                xmlFile.write(xmlBeauty.toprettyxml())
                xmlFile.close()
            except ValueError:
                pass

    def setDefaultPresetValues(self):
        for i in range(self.gui.listWidget_workgroup.rowCount()): #Set all FALSE in Workgroups
            workgroup_checkBox = QCheckBox()
            workgroup_checkBox.setChecked(False)
            workgroup_cellWidget = QWidget()
            workgroup_cellWidget.setStyleSheet('''
                                                background-color: rgb(150, 0, 0);
                                                color: rgb(255, 255, 255);
                                                ''')
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(workgroup_checkBox)
            layout.setAlignment(QtCore.Qt.AlignCenter)

            workgroup_cellWidget.setLayout(layout)

            self.gui.listWidget_workgroup.setCellWidget(i, 1, workgroup_cellWidget)
            workgroup_checkBox.stateChanged.connect(partial(self.ns_workgroup_checkBoxChanged, i, workgroup_checkBox, workgroup_cellWidget))

        for i in range(self.gui.listWidget_renderer.rowCount()): #Set all FALSE in Renderer
            renderer_checkBox = QCheckBox()
            renderer_checkBox.setChecked(False)
            renderer_cellWidget = QWidget()
            renderer_cellWidget.setStyleSheet('''
                                                background-color: rgb(150, 0, 0);
                                                color: rgb(255, 255, 255);
                                                ''')
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(renderer_checkBox)
            layout.setAlignment(QtCore.Qt.AlignCenter)

            renderer_cellWidget.setLayout(layout)

            self.gui.listWidget_renderer.setCellWidget(i, 3, renderer_cellWidget)
            renderer_checkBox.stateChanged.connect(partial(self.ns_renderer_checkBoxChanged, i, renderer_checkBox, renderer_cellWidget))
        try:
            root = ET.parse(configPath + os.sep + "Default.xml").getroot()
            for child in root:
                if child.tag == "Application":
                    for i in child:
                        index =  self.gui.comboBox_HOUVersion.findText(i.attrib['version'])
                        self.gui.comboBox_HOUVersion.setCurrentIndex(index)
                if child.tag == "Renderer":
                    for ii in child:
                        for i in range(self.gui.listWidget_renderer.rowCount()):
                            pluginVersion = ""
                            if str(self.gui.listWidget_renderer.item(i, 0).text()) in ["Redshift"]:
                                cellItem = self.gui.listWidget_renderer.cellWidget(i, 2)
                                cellLayout = cellItem.layout()
                                layoutItem = cellLayout.itemAt(0)
                                comboItem = layoutItem.widget()
                                index = comboItem.findText(ii.attrib['plugin'])
                                if index != -1:
                                    comboItem.setCurrentIndex(index)
                                else:
                                    comboItem.setCurrentIndex(0)
                                pluginVersion = str(comboItem.currentText())
                            else:
                                pluginVersion = str(self.gui.listWidget_renderer.item(i, 2).text())

                            if str(self.gui.listWidget_renderer.item(i, 0).text()) == ii.attrib['name'] and str(self.gui.listWidget_renderer.item(i, 1).text()) == ii.attrib['version'] and pluginVersion == ii.attrib['plugin'] and str(self.gui.listWidget_renderer.item(i, 4).text()) == ii.attrib['path']:
                                renderer_checkBox = QCheckBox()
                                renderer_checkBox.setChecked(True)
                                renderer_cellWidget = QWidget()
                                renderer_cellWidget.setStyleSheet('''
                                                                    background-color: rgb(0, 150, 0);
                                                                    color: rgb(255, 255, 255);
                                                                    ''')
                                layout = QHBoxLayout()
                                layout.setContentsMargins(0, 0, 0, 0)
                                layout.setSpacing(0)
                                layout.addWidget(renderer_checkBox)
                                layout.setAlignment(QtCore.Qt.AlignCenter)

                                renderer_cellWidget.setLayout(layout)

                                self.gui.listWidget_renderer.setCellWidget(i, 3, renderer_cellWidget)
                                renderer_checkBox.stateChanged.connect(partial(self.ns_renderer_checkBoxChanged, i, renderer_checkBox, renderer_cellWidget))
                if child.tag == "Workgroup":
                    for ii in child:
                        for i in range(self.gui.listWidget_workgroup.rowCount()):
                            if str(self.gui.listWidget_workgroup.item(i, 0).text()) == ii.attrib['name'] and str(self.gui.listWidget_workgroup.item(i, 2).text()) == ii.attrib['path']:
                                workgroup_checkBox = QCheckBox()
                                workgroup_checkBox.setChecked(True)
                                workgroup_cellWidget = QWidget()
                                workgroup_cellWidget.setStyleSheet('''
                                                                    background-color: rgb(0, 150, 0);
                                                                    color: rgb(255, 255, 255);
                                                                    ''')

                                layout = QHBoxLayout()
                                layout.setContentsMargins(0, 0, 0, 0)
                                layout.setSpacing(0)
                                layout.addWidget(workgroup_checkBox)
                                layout.setAlignment(QtCore.Qt.AlignCenter)

                                workgroup_cellWidget.setLayout(layout)

                                self.gui.listWidget_workgroup.setCellWidget(i, 1, workgroup_cellWidget)
                                workgroup_checkBox.stateChanged.connect(partial(self.ns_workgroup_checkBoxChanged, i, workgroup_checkBox, workgroup_cellWidget))
                if child.tag == "AdditionalParameters":
                    for ii in child:
                        self.gui.textEdit_addParameters.setText(ii.attrib['value'].replace("___", "\n"))
                if child.tag == "exeVersion":
                    for ii in child:
                        self.gui.comboBox_exeVersion.setCurrentIndex(self.gui.comboBox_exeVersion.findText(ii.attrib['value'].replace(" ", "\n")))
                if child.tag == "RenderService":
                    for ii in child:
                        self.gui.lineEdit_renderService.setText(ii.attrib['value'].replace(" ", "\n"))

            self.gui.comboBox_preset.setCurrentIndex(self.gui.comboBox_preset.findText(root.tag))
        except:
           pass


    def setPresetValues(self, index):
        try:
            presetName = self.gui.comboBox_preset.itemText(index)
            root = ET.parse(presetPath + os.sep + str(presetName) + ".xml").getroot()
            self.gui.lineEdit_renderService.setText("")
            self.gui.textEdit_addParameters.clear()
            for i in range(self.gui.listWidget_workgroup.rowCount()):  # Set all FALSE in Workgroups
                workgroup_checkBox = QCheckBox()
                workgroup_checkBox.setChecked(False)
                workgroup_cellWidget = QWidget()
                workgroup_cellWidget.setStyleSheet('''
                                                    background-color: rgb(150, 0, 0);
                                                    color: rgb(255, 255, 255);
                                                    ''')
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                layout.addWidget(workgroup_checkBox)
                layout.setAlignment(QtCore.Qt.AlignCenter)

                workgroup_cellWidget.setLayout(layout)

                self.gui.listWidget_workgroup.setCellWidget(i, 1, workgroup_cellWidget)
                workgroup_checkBox.stateChanged.connect(
                    partial(self.ns_workgroup_checkBoxChanged, i, workgroup_checkBox, workgroup_cellWidget))

            for i in range(self.gui.listWidget_renderer.rowCount()):  # Set all FALSE in Renderer
                renderer_checkBox = QCheckBox()
                renderer_checkBox.setChecked(False)
                renderer_cellWidget = QWidget()
                renderer_cellWidget.setStyleSheet('''
                                                    background-color: rgb(150, 0, 0);
                                                    color: rgb(255, 255, 255);
                                                    ''')
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                layout.addWidget(renderer_checkBox)
                layout.setAlignment(QtCore.Qt.AlignCenter)

                renderer_cellWidget.setLayout(layout)

                self.gui.listWidget_renderer.setCellWidget(i, 3, renderer_cellWidget)
                renderer_checkBox.stateChanged.connect(
                    partial(self.ns_renderer_checkBoxChanged, i, renderer_checkBox, renderer_cellWidget))
            for child in root:
                if child.tag == "Application":
                    for i in child:
                        index =  self.gui.comboBox_HOUVersion.findText(i.attrib['version'])
                        self.gui.comboBox_HOUVersion.setCurrentIndex(index)
                if child.tag == "Renderer":
                    for ii in child:
                        for i in range(self.gui.listWidget_renderer.rowCount()):
                            pluginVersion = ""
                            if str(self.gui.listWidget_renderer.item(i, 0).text()) in ["Redshift"]:
                                cellItem = self.gui.listWidget_renderer.cellWidget(i, 2)
                                cellLayout = cellItem.layout()
                                layoutItem = cellLayout.itemAt(0)
                                comboItem = layoutItem.widget()
                                index = comboItem.findText(ii.attrib['plugin'])
                                if index != -1:
                                    comboItem.setCurrentIndex(index)
                                else:
                                    comboItem.setCurrentIndex(0)
                                pluginVersion = str(comboItem.currentText())
                            else:
                                pluginVersion = str(self.gui.listWidget_renderer.item(i, 2).text())

                            if str(self.gui.listWidget_renderer.item(i, 0).text()) == ii.attrib['name'] and str(self.gui.listWidget_renderer.item(i, 1).text()) == ii.attrib['version'] and pluginVersion == ii.attrib['plugin'] and str(self.gui.listWidget_renderer.item(i, 4).text()) == ii.attrib['path']:
                                renderer_checkBox = QCheckBox()
                                renderer_checkBox.setChecked(True)
                                renderer_cellWidget = QWidget()
                                renderer_cellWidget.setStyleSheet('''
                                                                    background-color: rgb(0, 150, 0);
                                                                    color: rgb(255, 255, 255);
                                                                    ''')
                                layout = QHBoxLayout()
                                layout.setContentsMargins(0, 0, 0, 0)
                                layout.setSpacing(0)
                                layout.addWidget(renderer_checkBox)
                                layout.setAlignment(QtCore.Qt.AlignCenter)

                                renderer_cellWidget.setLayout(layout)

                                self.gui.listWidget_renderer.setCellWidget(i, 3, renderer_cellWidget)
                                renderer_checkBox.stateChanged.connect(partial(self.ns_renderer_checkBoxChanged, i, renderer_checkBox, renderer_cellWidget))
                if child.tag == "Workgroup":
                    for ii in child:
                        for i in range(self.gui.listWidget_workgroup.rowCount()):
                            if str(self.gui.listWidget_workgroup.item(i, 0).text()) == ii.attrib['name'] and str(self.gui.listWidget_workgroup.item(i, 2).text()) == ii.attrib['path']:
                                workgroup_checkBox = QCheckBox()
                                workgroup_checkBox.setChecked(True)
                                workgroup_cellWidget = QWidget()
                                workgroup_cellWidget.setStyleSheet('''
                                                                    background-color: rgb(0, 150, 0);
                                                                    color: rgb(255, 255, 255);
                                                                    ''')

                                layout = QHBoxLayout()
                                layout.setContentsMargins(0, 0, 0, 0)
                                layout.setSpacing(0)
                                layout.addWidget(workgroup_checkBox)
                                layout.setAlignment(QtCore.Qt.AlignCenter)

                                workgroup_cellWidget.setLayout(layout)

                                self.gui.listWidget_workgroup.setCellWidget(i, 1, workgroup_cellWidget)
                                workgroup_checkBox.stateChanged.connect(partial(self.ns_workgroup_checkBoxChanged, i, workgroup_checkBox, workgroup_cellWidget))
                if child.tag == "AdditionalParameters":
                    for ii in child:
                        self.gui.textEdit_addParameters.setText(ii.attrib['value'].replace("___", "\n"))

                self.gui.comboBox_preset.setCurrentIndex(self.gui.comboBox_preset.findText(root.tag))
                if child.tag == "exeVersion":
                    for ii in child:
                        self.gui.comboBox_exeVersion.setCurrentIndex(self.gui.comboBox_exeVersion.findText(ii.attrib['value'].replace(" ", "\n")))
                if child.tag == "RenderService":
                    for ii in child:
                        self.gui.lineEdit_renderService.setText(ii.attrib['value'].replace(" ", "\n"))
        except:
           pass

    def openGUI(self):
        self.gui.show()
        self.update()
        self.setDefaultPresetValues()


    def update(self):
        #Icons
        iconRS = QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "rsIcon.png"))
        iconRS_Local = QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "rsIcon_Local.png"))
        iconArnold = QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "arnoldIcon.png"))
        iconHou = QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "houIcon.png"))

        self.gui.comboBox_HOUVersion.clear()
        self.gui.listWidget_renderer.setRowCount(0)
        self.gui.listWidget_workgroup.setRowCount(0)

        # Get Houdini Versions #########################################################################################
        houdiniVersions = []
        houdiniEntryPathes = []

        if sys.platform == "darwin": #macOS 
                pass
                #TODO macOS version
        if sys.platform == "linux2": #Linux
                pass
                #TODO linux version
        if sys.platform == "win32": #Windows
            
            foundedFiles = [d for d in os.listdir(searchPathHoudiniWIN) if os.path.isdir(os.path.join(searchPathHoudiniWIN, d))]

            for i in foundedFiles:

                if i.find("Houdini") != -1:

                    houdiniVersions.append(i)
                    houdiniEntryPathes.append(searchPathHoudiniWIN+os.sep+i)
                    self.gui.comboBox_HOUVersion.addItem(i)


        # Get Arnold HTOA ##############################################################################################
        try:
            arnoldVersions = []
            arnoldHTOAVersions = []
            arnoldEntryPathes = []

            if sys.platform == "darwin": #macOS 
                    pass
            if sys.platform == "linux2": #Linux
                    pass
            if sys.platform == "win32": #Windows
                
                foundedFiles = [d for d in os.listdir(searchPathArnold) if os.path.isdir(os.path.join(searchPathArnold, d))]

                for i in foundedFiles:

                    if i.find("htoa") != -1:

                        parts = i.split("_")
                        arnoldParts = parts[0].split("-")
                        houdiniParts = parts[-1].split("-")
                        
                        arnoldHTOAVersions.append(houdiniParts[1])
                        arnoldVersions.append(arnoldParts[1])
                        arnoldEntryPathes.append(searchPathArnold+os.sep+i)


            for i in range(len(arnoldVersions)):
                self.gui.listWidget_renderer.insertRow(i)
                
                arnoldItem = QTableWidgetItem("Arnold")
                arnoldItem.setIcon(iconArnold)

                
                self.gui.listWidget_renderer.setItem(i, 0, arnoldItem)
                self.gui.listWidget_renderer.setItem(i, 1, QTableWidgetItem(arnoldVersions[i]))
                self.gui.listWidget_renderer.setItem(i, 2, QTableWidgetItem(arnoldHTOAVersions[i]))
                self.gui.listWidget_renderer.setItem(i, 4, QTableWidgetItem(arnoldEntryPathes[i]))

                #Checkboxes
                renderer_checkBox = QCheckBox()
                renderer_checkBox.setChecked(False)
                renderer_cellWidget = QWidget()
                
                if renderer_checkBox.checkState() == QtCore.Qt.Checked:
                    renderer_cellWidget.setStyleSheet('''
                                                        background-color: rgb(0, 150, 0);
                                                        color: rgb(255, 255, 255);
                                                        ''')
                else:
                    renderer_cellWidget.setStyleSheet('''
                                                        background-color: rgb(150, 0, 0);
                                                        color: rgb(255, 255, 255);
                                                        ''')
                layout = QHBoxLayout()
                layout.setContentsMargins(0,0,0,0)
                layout.setSpacing(0)
                layout.addWidget(renderer_checkBox)
                layout.setAlignment(QtCore.Qt.AlignCenter)
                
                renderer_cellWidget.setLayout(layout)

                renderer_checkBox.stateChanged.connect(partial(self.ns_renderer_checkBoxChanged, i, renderer_checkBox,  renderer_cellWidget))
                self.gui.listWidget_renderer.setCellWidget(i, 3, renderer_cellWidget)
                self.gui.listWidget_renderer.setColumnWidth(3, 50)
                self.gui.listWidget_renderer.setColumnWidth(4, 500)
        except:
            pass
        # Get Redshift #################################################################################################
        try:
            rsVersions = []
            rsEntryPathes = []

            if sys.platform == "darwin":  # macOS
                pass
            if sys.platform == "linux2":  # Linux
                pass
            if sys.platform == "win32":  # Windows

                foundedFiles = [d for d in os.listdir(searchPathRedshift) if os.path.isdir(os.path.join(searchPathRedshift, d))]

                for i in foundedFiles:

                    if i.find("Redshift") != -1:

                        parts = i.split("_")
                        rsVersions.append(parts[1])
                        rsEntryPathes.append(searchPathRedshift + os.sep + i)

            if sys.platform == "darwin":  # macOS
                pass
            if sys.platform == "linux2":  # Linux
                pass
            if sys.platform == "win32":  # Windows

                for i in range(len(rsVersions)):
                    rsPluginVersions = [d for d in os.listdir(rsEntryPathes[i] + os.sep + "plugins" + os.sep + "houdini") if os.path.isdir(os.path.join(rsEntryPathes[i] + os.sep + "plugins" + os.sep + "houdini", d))]
                    rsItem = QTableWidgetItem("Redshift")
                    rsItem.setIcon(iconRS)

                    self.gui.listWidget_renderer.insertRow(self.gui.listWidget_renderer.rowCount())
                    self.gui.listWidget_renderer.setItem(self.gui.listWidget_renderer.rowCount()-1, 0, rsItem)
                    self.gui.listWidget_renderer.setItem(self.gui.listWidget_renderer.rowCount()-1, 1, QTableWidgetItem(rsVersions[i]))
                    self.gui.listWidget_renderer.setItem(self.gui.listWidget_renderer.rowCount()-1, 2, QTableWidgetItem("combo"))
                    self.gui.listWidget_renderer.setItem(self.gui.listWidget_renderer.rowCount()-1, 4, QTableWidgetItem(rsEntryPathes[i]))

                    # Checkboxes
                    renderer_checkBox = QCheckBox()
                    renderer_checkBox.setChecked(False)
                    renderer_cellWidget = QWidget()

                    if renderer_checkBox.checkState() == QtCore.Qt.Checked:
                        renderer_cellWidget.setStyleSheet('''
                                                            background-color: rgb(0, 150, 0);
                                                            color: rgb(255, 255, 255);
                                                            ''')
                    else:
                        renderer_cellWidget.setStyleSheet('''
                                                            background-color: rgb(150, 0, 0);
                                                            color: rgb(255, 255, 255);
                                                            ''')
                    layout = QHBoxLayout()
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setSpacing(0)
                    layout.addWidget(renderer_checkBox)
                    layout.setAlignment(QtCore.Qt.AlignCenter)

                    renderer_cellWidget.setLayout(layout)

                    renderer_checkBox.stateChanged.connect(partial(self.ns_renderer_checkBoxChanged, self.gui.listWidget_renderer.rowCount()-1, renderer_checkBox, renderer_cellWidget))
                    self.gui.listWidget_renderer.setCellWidget(self.gui.listWidget_renderer.rowCount()-1, 3, renderer_cellWidget)

                    # Combobox
                    renderer_comboBox = QComboBox()
                    for i in rsPluginVersions:
                        renderer_comboBox.addItem(i)
                    renderer_cellWidget = QWidget()

                    renderer_cellWidget.setStyleSheet('''
                                                        color: rgb(255, 255, 255);
                                                        ''')

                    layout = QHBoxLayout()
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setSpacing(0)
                    layout.addWidget(renderer_comboBox)
                    layout.setAlignment(QtCore.Qt.AlignCenter)

                    renderer_cellWidget.setLayout(layout)

                    self.gui.listWidget_renderer.setCellWidget(self.gui.listWidget_renderer.rowCount()-1, 2, renderer_cellWidget)
                    self.gui.listWidget_renderer.setColumnWidth(0, 120)
                    self.gui.listWidget_renderer.setColumnWidth(1, 50)
                    self.gui.listWidget_renderer.setColumnWidth(2, 100)
                    self.gui.listWidget_renderer.setColumnWidth(3, 50)
                    self.gui.listWidget_renderer.setColumnWidth(4, 500)
        except:
            pass
        # Get Redshift Local ###########################################################################################
        # try:
        #     releaseFile = open(searchPathRSLocalWIN + os.sep + "release_notes.txt", "r")
        #     rsVersion = releaseFile.readline()
        #     rsVersion = rsVersion.replace("\n", "")
        #     releaseFile.close()
        #     rsPluginVersions = [d for d in os.listdir(searchPathRSLocalWIN + os.sep + "plugins" + os.sep + "houdini") if os.path.isdir(os.path.join(searchPathRSLocalWIN + os.sep + "plugins" + os.sep + "houdini", d))]
        #
        #     if sys.platform == "darwin":  # macOS
        #         pass
        #     if sys.platform == "linux2":  # Linux
        #         pass
        #     if sys.platform == "win32":  # Windows
        #
        #         rsItem = QTableWidgetItem("Redshift")
        #         rsItem.setIcon(iconRS_Local)
        #
        #         self.gui.listWidget_renderer.insertRow(self.gui.listWidget_renderer.rowCount())
        #         self.gui.listWidget_renderer.setItem(self.gui.listWidget_renderer.rowCount()-1, 0, rsItem)
        #         self.gui.listWidget_renderer.setItem(self.gui.listWidget_renderer.rowCount()-1, 1, QTableWidgetItem(rsVersion))
        #         self.gui.listWidget_renderer.setItem(self.gui.listWidget_renderer.rowCount()-1, 2, QTableWidgetItem("combo"))
        #         self.gui.listWidget_renderer.setItem(self.gui.listWidget_renderer.rowCount()-1, 4, QTableWidgetItem(searchPathRSLocalWIN))
        #
        #         # Checkboxes
        #         renderer_checkBox = QCheckBox()
        #         renderer_checkBox.setChecked(False)
        #         renderer_cellWidget = QWidget()
        #
        #         if renderer_checkBox.checkState() == QtCore.Qt.Checked:
        #             renderer_cellWidget.setStyleSheet('''
        #                                                 background-color: rgb(0, 150, 0);
        #                                                 color: rgb(255, 255, 255);
        #                                                 ''')
        #         else:
        #             renderer_cellWidget.setStyleSheet('''
        #                                                 background-color: rgb(150, 0, 0);
        #                                                 color: rgb(255, 255, 255);
        #                                                 ''')
        #         layout = QHBoxLayout()
        #         layout.setContentsMargins(0, 0, 0, 0)
        #         layout.setSpacing(0)
        #         layout.addWidget(renderer_checkBox)
        #         layout.setAlignment(QtCore.Qt.AlignCenter)
        #
        #         renderer_cellWidget.setLayout(layout)
        #
        #         renderer_checkBox.stateChanged.connect(partial(self.ns_renderer_checkBoxChanged, self.gui.listWidget_renderer.rowCount()-1, renderer_checkBox, renderer_cellWidget))
        #         self.gui.listWidget_renderer.setCellWidget(self.gui.listWidget_renderer.rowCount()-1, 3, renderer_cellWidget)
        #
        #         # Combobox
        #         renderer_comboBox = QComboBox()
        #         for i in rsPluginVersions:
        #             renderer_comboBox.addItem(i)
        #         renderer_cellWidget = QWidget()
        #
        #         renderer_cellWidget.setStyleSheet('''
        #                                             color: rgb(255, 255, 255);
        #                                             ''')
        #
        #
        #         layout = QHBoxLayout()
        #         layout.setContentsMargins(0, 0, 0, 0)
        #         layout.setSpacing(0)
        #         layout.addWidget(renderer_comboBox)
        #         layout.setAlignment(QtCore.Qt.AlignCenter)
        #
        #         renderer_cellWidget.setLayout(layout)
        #
        #         self.gui.listWidget_renderer.setCellWidget(self.gui.listWidget_renderer.rowCount()-1, 2, renderer_cellWidget)
        #         self.gui.listWidget_renderer.setColumnWidth(0, 120)
        #         self.gui.listWidget_renderer.setColumnWidth(1, 50)
        #         self.gui.listWidget_renderer.setColumnWidth(2, 100)
        #         self.gui.listWidget_renderer.setColumnWidth(3, 50)
        #         self.gui.listWidget_renderer.setColumnWidth(4, 500)
        # except:
        #     pass

        # Get Houdini Workgroups #######################################################################################
        try:

            workgroupEntryPathes = []
            workgroupName = []

            if sys.platform == "darwin": #macOS
                    pass
            if sys.platform == "linux2": #Linux
                    pass
            if sys.platform == "win32": #Windows

                foundedFiles = [d for d in os.listdir(searchPathWorkgroups) if os.path.isdir(os.path.join(searchPathWorkgroups, d))]

                for i in foundedFiles:

                    if i.find("Houdini") != -1:

                        workgroupEntryPathes.append(searchPathWorkgroups+os.sep+i)
                        workgroupName.append(i)

            for i in range(len(workgroupEntryPathes)):

                houItem = QTableWidgetItem(workgroupName[i])

                if os.path.exists(workgroupEntryPathes[i] + os.sep + "icon.png"):
                    iconHou = QtGui.QIcon(QtGui.QPixmap(workgroupEntryPathes[i] + os.sep + "icon.png"))
                else:
                    iconHou = QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "houIcon.png"))


                houItem.setIcon(iconHou)

                self.gui.listWidget_workgroup.insertRow(i)
                self.gui.listWidget_workgroup.setItem(i, 0, houItem)
                self.gui.listWidget_workgroup.setItem(i, 2, QTableWidgetItem(workgroupEntryPathes[i]))

                #Checkboxes
                workgroup_checkBox = QCheckBox()
                workgroup_checkBox.setChecked(False)
                workgroup_cellWidget = QWidget()

                if renderer_checkBox.checkState() == QtCore.Qt.Checked:
                    workgroup_cellWidget.setStyleSheet('''
                                                        background-color: rgb(0, 150, 0);
                                                        color: rgb(255, 255, 255);
                                                        ''')
                else:
                    workgroup_cellWidget.setStyleSheet('''
                                                        background-color: rgb(150, 0, 0);
                                                        color: rgb(255, 255, 255);
                                                        ''')
                layout = QHBoxLayout()
                layout.setContentsMargins(0,0,0,0)
                layout.setSpacing(0)
                layout.addWidget(workgroup_checkBox)
                layout.setAlignment(QtCore.Qt.AlignCenter)

                workgroup_cellWidget.setLayout(layout)

                workgroup_checkBox.stateChanged.connect(partial(self.ns_workgroup_checkBoxChanged, i, workgroup_checkBox,  workgroup_cellWidget))
                self.gui.listWidget_workgroup.setCellWidget(i, 1, workgroup_cellWidget)
                self.gui.listWidget_workgroup.setColumnWidth(0, 250)
                self.gui.listWidget_workgroup.setColumnWidth(1, 50)
                self.gui.listWidget_workgroup.setColumnWidth(2, 500)
        except:
            pass

        self.loadPresetsToCombo("")


    def ns_renderer_checkBoxChanged(self, rowIndex, renderer_checkBox, renderer_cellWidget):
        typeRenderer = self.gui.listWidget_renderer.item(rowIndex, 0)

        if renderer_checkBox.checkState() == QtCore.Qt.Checked:
            renderer_cellWidget.setStyleSheet('''
                                                background-color: rgb(0, 150, 0);
                                                color: rgb(255, 255, 255); ''')
            renderer_cellWidget.setToolTip("Active")
        else:
            renderer_cellWidget.setStyleSheet('''
                                                background-color: rgb(150, 0, 0);
                                                color: rgb(255, 255, 255);''')

        for i in range(self.gui.listWidget_renderer.rowCount()):
            currentItemType = self.gui.listWidget_renderer.item(i, 0)
            if currentItemType.text() == typeRenderer.text():
                if i != rowIndex:
                    renderer_checkBox = QCheckBox()
                    renderer_checkBox.setChecked(False)
                    renderer_cellWidget = QWidget()

                    if renderer_checkBox.checkState() == QtCore.Qt.Checked:
                        renderer_cellWidget.setStyleSheet('''
                                                            background-color: rgb(0, 150, 0);
                                                            color: rgb(255, 255, 255);
                                                            ''')
                    else:
                        renderer_cellWidget.setStyleSheet('''
                                                            background-color: rgb(150, 0, 0);
                                                            color: rgb(255, 255, 255);
                                                            ''')
                    layout = QHBoxLayout()
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setSpacing(0)
                    layout.addWidget(renderer_checkBox)
                    layout.setAlignment(QtCore.Qt.AlignCenter)

                    renderer_cellWidget.setLayout(layout)

                    renderer_checkBox.stateChanged.connect(partial(self.ns_renderer_checkBoxChanged, i, renderer_checkBox, renderer_cellWidget))

                    self.gui.listWidget_renderer.setCellWidget(i, 3, renderer_cellWidget)


    def ns_workgroup_checkBoxChanged(self, rowIndex, workgroup_checkBox, workgroup_cellWidget):
        if workgroup_checkBox.checkState() == QtCore.Qt.Checked:
            workgroup_cellWidget.setStyleSheet('''
                                                background-color: rgb(0, 150, 0);
                                                color: rgb(255, 255, 255); ''')
        else:
            workgroup_cellWidget.setStyleSheet('''
                                                background-color: rgb(150, 0, 0);
                                                color: rgb(255, 255, 255);''')


    def openApplication(self):

        executeString = "\necho ns_Startup v0.1\n\n"
        additionalParameters = str(self.gui.textEdit_addParameters.toPlainText()).split("\n")
        for i in range(len(additionalParameters)):
            executeString = executeString + "SET " + "\"" + additionalParameters[i] + "\"" + "\n"

        # Look at Lists & AppVersion
        selectedRenderer = []
        selectedWorkgroups = []
        houVersion = self.gui.comboBox_HOUVersion.currentText()
        exeVersion = self.gui.comboBox_exeVersion.currentText()
        renderService = self.gui.lineEdit_renderService.text()

        for i in range(self.gui.listWidget_renderer.rowCount()):
            nameItem = self.gui.listWidget_renderer.item(i, 0)
            versionItem = self.gui.listWidget_renderer.item(i, 1)
            pluginItem = self.gui.listWidget_renderer.item(i, 2)
            pathItem = self.gui.listWidget_renderer.item(i, 4)

            cellItem = self.gui.listWidget_renderer.cellWidget(i, 3)
            cellLayout = cellItem.layout()
            layoutItem = cellLayout.itemAt(0)
            checkboxItem = layoutItem.widget()
            if checkboxItem.isChecked():
                if nameItem.text() in ["Redshift"]:
                    cellItem = self.gui.listWidget_renderer.cellWidget(i, 2)
                    cellLayout = cellItem.layout()
                    layoutItem = cellLayout.itemAt(0)
                    comboItem = layoutItem.widget()
                    selectedRenderer.append([str(nameItem.text()), str(versionItem.text()), str(comboItem.currentText()), str(pathItem.text())])
                else:
                    selectedRenderer.append([str(nameItem.text()), str(versionItem.text()), str(pluginItem.text()), str(pathItem.text())])

        for i in range(self.gui.listWidget_workgroup.rowCount()):
            nameItem = self.gui.listWidget_workgroup.item(i, 0)
            pathItem = self.gui.listWidget_workgroup.item(i, 2)

            cellItem = self.gui.listWidget_workgroup.cellWidget(i, 1)
            cellLayout = cellItem.layout()
            layoutItem = cellLayout.itemAt(0)
            checkboxItem = layoutItem.widget()
            if checkboxItem.isChecked():
                selectedWorkgroups.append([str(nameItem.text()), str(pathItem.text())])

        paths = []
        houdiniPaths = []
        houdiniOtlScanPaths = []
        houdiniToolbarPaths = []
        houdiniGalleryPaths = []
        houdiniScriptPaths = []

        #Renderer
        for i in range(len(selectedRenderer)):

            if selectedRenderer[i][0] == "Redshift":
                executeString = executeString + "SET " + "\"" + "PATH_RENDERER_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + os.sep + "bin" + "\"" + "\n"
                paths.append("%PATH_RENDERER_" + selectedRenderer[i][0].upper() + "%")
                executeString = executeString + "SET " + "\"" + "HOUDINI_PATH_RENDERER_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + os.sep + "Plugins" + os.sep + "Houdini" + os.sep + selectedRenderer[i][2] + "\"" + "\n"
                houdiniPaths.append("%HOUDINI_PATH_RENDERER_" + selectedRenderer[i][0].upper() + "%")
                #######################################################################################
                # set ENVs
                os.environ["REDSHIFT_COREDATAPATH"] = selectedRenderer[i][3]
                os.environ["REDSHIFT_LOCALDATAPATH"] = selectedRenderer[i][3]
                os.environ["REDSHIFT_PROCEDURALSPATH"] = selectedRenderer[i][3] + os.sep + "Procedurals"
                # local only workaround
                os.environ["REDSHIFT_LICENSEPATH"] = "C:\ProgramData\Redshift"
                os.environ["REDSHIFT_PREFSPATH"] = "C:\ProgramData\Redshift\preferences.xml"
                os.environ["REDSHIFT_LOGPATH"] = "C:\ProgramData\Redshift\Log"
                #######################################################################################

            if selectedRenderer[i][0] == "Arnold":
                path = selectedRenderer[i][3].split(os.sep)

                executeString = executeString + "SET " + "\"" + "PATH_RENDERER_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + os.sep + "scripts" + os.sep + "bin" + "\"" + "\n"
                paths.append("%PATH_RENDERER_" + selectedRenderer[i][0].upper() + "%")

                executeString = executeString + "SET " + "\"" + "HOUDINI_PATH_RENDERER_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + "\"" + "\n"
                houdiniPaths.append("%HOUDINI_PATH_RENDERER_" + selectedRenderer[i][0].upper() + "%")

                executeString = executeString + "SET " + "\"" + "HOUDINI_OTLSCAN_PATH_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + os.sep + "otls" + "\"" + "\n"
                houdiniOtlScanPaths.append("%HOUDINI_OTLSCAN_PATH_" + selectedRenderer[i][0].upper() + "%")

                executeString = executeString + "SET " + "\"" + "HOUDINI_TOOLBAR_PATH_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + os.sep + "toolbar" + "\"" + "\n"
                houdiniToolbarPaths.append("%HOUDINI_TOOLBAR_PATH_" + selectedRenderer[i][0].upper() + "%")

                executeString = executeString + "SET " + "\"" + "HOUDINI_SCRIPT_PATH_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + os.sep + "scripts" + "\"" + "\n"
                houdiniScriptPaths.append("%HOUDINI_SCRIPT_PATH_" + selectedRenderer[i][0].upper() + "%")



        #Workgroups
        for i in range(len(selectedWorkgroups)):
            if "Workgroup_Houdini_H" in selectedWorkgroups[i][0]:
                executeString = executeString + "SET " + "\"" + "HSITE=" + selectedWorkgroups[i][1] + "\"" + "\n"
                houdiniPaths.append("%HSITE%")

                y=0
                for x in os.walk(selectedWorkgroups[i][1] + os.sep + "otls"): #subfolders check in otls folder
                    allFolders = x[0].split(os.sep)
                    if allFolders[-1] != "backup":
                        executeString = executeString + "SET " + "\"" + "HSITE_OTLSCAN_PATH_" + selectedWorkgroups[i][0].upper() + "_" + str(y) + "=" + x[0] + "\"" + "\n"
                        houdiniOtlScanPaths.append("%HSITE_OTLSCAN_PATH_" + selectedWorkgroups[i][0].upper() + "_" + str(y) + "%")
                        y=y+1

                executeString = executeString + "SET " + "\"" + "HSITE_TOOLBAR_PATH_" + selectedWorkgroups[i][0].upper() + "=%HSITE%" + os.sep + "toolbar" + "\"" + "\n"
                houdiniToolbarPaths.append("%HSITE_TOOLBAR_PATH_" + selectedWorkgroups[i][0].upper() + "%")

                executeString = executeString + "SET " + "\"" + "HSITE_GALLERY_PATH_" + selectedWorkgroups[i][0].upper() + "=%HSITE%" + os.sep + "gallery" + "\"" + "\n"
                houdiniGalleryPaths.append("%HSITE_GALLERY_PATH_" + selectedWorkgroups[i][0].upper() + "%")

                executeString = executeString + "SET " + "\"" + "HSITE_SCRIPT_PATH_" + selectedWorkgroups[i][0].upper() + "=%HSITE%" + os.sep + "scripts" + "\"" + "\n"
                houdiniScriptPaths.append("%HSITE_SCRIPT_PATH_" + selectedWorkgroups[i][0].upper() + "%")

            else:
                executeString = executeString + "SET " + "\"" + "HOUDINI_PATH_" + selectedWorkgroups[i][0].upper() + "=" + selectedWorkgroups[i][1] + "\"" + "\n"
                houdiniPaths.append("%HOUDINI_PATH_" + selectedWorkgroups[i][0].upper()+"%")

                y=0
                for x in os.walk(selectedWorkgroups[i][1] + os.sep + "otls"): #subfolders check in otls folder
                    allFolders = x[0].split(os.sep)
                    if allFolders[-1] != "backup":
                        executeString = executeString + "SET " + "\"" + "HOUDINI_OTLSCAN_PATH_" + selectedWorkgroups[i][0].upper() + "_" + str(y) + "=" + x[0] + "\"" + "\n"
                        houdiniOtlScanPaths.append("%HOUDINI_OTLSCAN_PATH_" + selectedWorkgroups[i][0].upper() + "_" + str(y) + "%")
                        y=y+1

                executeString = executeString + "SET " +  "\"" + "HOUDINI_TOOLBAR_PATH_" + selectedWorkgroups[i][0].upper() + "=%PATH_" + selectedWorkgroups[i][0].upper() + "%" + os.sep + "toolbar"  + "\"" + "\n"
                houdiniToolbarPaths.append("%HOUDINI_TOOLBAR_PATH_" + selectedWorkgroups[i][0].upper() + "%")

        #RenderService
        executeString = executeString + "SET " + "\"" + "HOUDINI_PATH_RENDER_SERVICE=" + renderService.replace("<USER>", user) + "\"" + "\n"
        houdiniPaths.append("%HOUDINI_PATH_RENDER_SERVICE%")

        tmp = ""
        for i in range(len(paths)):
            tmp = tmp + paths[i] + ";"
        executeString = executeString + "SET " + "\"" + "PATH=" + tmp + "&" + "\"" + "\n"

        tmp = ""
        for i in range(len(houdiniPaths)):
            tmp = tmp + houdiniPaths[i] + ";"
        executeString = executeString + "SET " + "\"" + "HOUDINI_PATH=" + tmp + "&" + "\"" + "\n"

        tmp = ""
        for i in range(len(houdiniOtlScanPaths)):
            tmp = tmp + houdiniOtlScanPaths[i] + ";"
        executeString = executeString + "SET " + "\"" + "HOUDINI_OTLSCAN_PATH=" + tmp + "&" + "\"" + "\n"

        tmp = ""
        for i in range(len(houdiniToolbarPaths)):
            tmp = tmp + houdiniToolbarPaths[i] + ";"
        executeString = executeString + "SET " + "\"" + "HOUDINI_TOOLBAR_PATH=" + tmp + "&" + "\"" + "\n"

        tmp = ""
        for i in range(len(houdiniGalleryPaths)):
            tmp = tmp + houdiniGalleryPaths[i] + ";"
        executeString = executeString + "SET " + "\"" + "HOUDINI_GALLERY_PATH=" + tmp + "&" + "\"" + "\n"

        tmp = ""
        for i in range(len(houdiniScriptPaths)):
            tmp = tmp + houdiniScriptPaths[i] + ";"
        executeString = executeString + "SET " + "\"" + "HOUDINI_SCRIPT_PATH=" + tmp + "&" + "\"" + "\n"

        executeString = executeString + "START /d " + "\"" + searchPathHoudiniWIN + os.sep + houVersion + os.sep + "bin" + "\" " + exeVersion


        #print(executeString)
        batFile = open(scriptRoot + os.sep + "startup.bat", "w")
        batFile.write(executeString)
        batFile.close()

        p = subprocess.Popen(scriptRoot + os.sep + "startup.bat", shell=True, stdout=subprocess.PIPE)

        stdout, stderr = p.communicate()
        if p.returncode == 0:
            trayIcon.showMessage("", "ns_Startup> is starting a Houdini session.", icon=QSystemTrayIcon.Information)
        else:
            trayIcon.showMessage("", "ns_Startup> something went wrong!", icon=QSystemTrayIcon.Information)

        if self.gui.checkBox_deleteBat.isChecked():
            try:
                os.remove(scriptRoot + os.sep + "startup.bat")
            except:
                pass

    def setArnoldLic(self):
            try:
                if not os.path.isfile(configPath + os.sep + "Config.xml"):
                    root = ET.Element("ns_Startup__settings")

                    arnoldLic = ET.Element("Arnold_RLM")
                    arnoldLic.text = str(self.gui.lineEdit_arnoldLic.text())

                    root.append(arnoldLic)

                    xml_beauty = ET.tostring(root)

                    if os.path.exists(configPath):
                        pass
                    else:
                        os.makedirs(configPath)

                    xml_file = open(configPath + os.sep + "Config.xml", "w")
                    xml_file.write(xml_beauty)
                    xml_file.close()
                else:
                    tree = ET.parse(configPath + os.sep + "Config.xml")
                    root = tree.getroot()
                    elem = root.find("Arnold_RLM")
                    if elem is not None:
                        elem.text = str(self.gui.lineEdit_arnoldLic.text())
                    else:
                        elem = ET.Element("Arnold_RLM")
                        elem.text = str(self.gui.lineEdit_arnoldLic.text())
                        root.append(elem)
                    tree.write(configPath + os.sep + "Config.xml")

                os.environ["solidangle_LICENSE"] = str(self.gui.lineEdit_arnoldLic.text())
                trayIcon.showMessage("ns_Startup", "Set solidangle_LICENSE=" + str(self.gui.lineEdit_arnoldLic.text()), icon=QSystemTrayIcon.Information, msecs=10000)

            except ValueError:
                pass


    def send_WOL_0(self):
        try:
            ns_Utility.wake_on_lan(str(self.gui.lineEdit_WOL_MAC_0.text()))
            trayIcon.showMessage("ns_Startup", "Send WOL: " + self.gui.lineEdit_WOL_MAC_0.text(), icon=QSystemTrayIcon.Information, msecs=10000)
        except:
            trayIcon.showMessage("ns_Startup", "Incorrect MAC address format." + self.gui.lineEdit_WOL_MAC_0.text(), icon=QSystemTrayIcon.Information, msecs=10000)


    def send_WOL_1(self):
        try:
            ns_Utility.wake_on_lan(str(self.gui.lineEdit_WOL_MAC_1.text()))
            trayIcon.showMessage("ns_Startup", "Send WOL: " + self.gui.lineEdit_WOL_MAC_1.text(), icon=QSystemTrayIcon.Information, msecs=10000)
        except:
            trayIcon.showMessage("ns_Startup", "Incorrect MAC address format." + self.gui.lineEdit_WOL_MAC_1.text(), icon=QSystemTrayIcon.Information, msecs=10000)


    def send_WOL_2(self):
        try:
            ns_Utility.wake_on_lan(str(self.gui.lineEdit_WOL_MAC_2.text()))
            trayIcon.showMessage("ns_Startup", "Send WOL: " + self.gui.lineEdit_WOL_MAC_2.text(), icon=QSystemTrayIcon.Information, msecs=10000)
        except:
            trayIcon.showMessage("ns_Startup", "Incorrect MAC address format." + self.gui.lineEdit_WOL_MAC_2.text(), icon=QSystemTrayIcon.Information, msecs=10000)


    def send_WOL_3(self):
        try:
            ns_Utility.wake_on_lan(str(self.gui.lineEdit_WOL_MAC_3.text()))
            trayIcon.showMessage("ns_Startup", "Send WOL: " + self.gui.lineEdit_WOL_MAC3.text(), icon=QSystemTrayIcon.Information, msecs=10000)
        except:
            trayIcon.showMessage("ns_Startup", "Incorrect MAC address format." + self.gui.lineEdit_WOL_MAC_3.text(), icon=QSystemTrayIcon.Information, msecs=10000)


    def saveConfig(self):
        try:
            if not os.path.isfile(configPath + os.sep + "Config.xml"):
                root = ET.Element("ns_Startup__settings")

                arnoldLic = ET.Element("Arnold_RLM")
                arnoldLic.text = str(self.gui.lineEdit_arnoldLic.text())
                wol0 = ET.Element("WOL_0", Address=str(self.gui.lineEdit_WOL_MAC_0.text()), Description=str(self.gui.lineEdit_WOL_Des_0.text()), startUp=str(self.gui.checkBox_startUp_0.isChecked()))
                wol1 = ET.Element("WOL_1", Address=str(self.gui.lineEdit_WOL_MAC_1.text()), Description=str(self.gui.lineEdit_WOL_Des_1.text()), startUp=str(self.gui.checkBox_startUp_1.isChecked()))
                wol2 = ET.Element("WOL_2", Address=str(self.gui.lineEdit_WOL_MAC_2.text()), Description=str(self.gui.lineEdit_WOL_Des_2.text()), startUp=str(self.gui.checkBox_startUp_2.isChecked()))
                wol3 = ET.Element("WOL_3", Address=str(self.gui.lineEdit_WOL_MAC_3.text()), Description=str(self.gui.lineEdit_WOL_Des_3.text()), startUp=str(self.gui.checkBox_startUp_3.isChecked()))

                root.append(arnoldLic)
                root.append(wol0)
                root.append(wol1)
                root.append(wol2)
                root.append(wol3)

                xml_beauty = ET.tostring(root)

                if os.path.exists(configPath):
                    pass
                else:
                    os.makedirs(configPath)

                xml_file = open(configPath + os.sep + "Config.xml", "w")
                xml_file.write(xml_beauty)
                xml_file.close()
            else:
                tree = ET.parse(configPath + os.sep + "Config.xml")
                root = tree.getroot()
                arnoldLic = root.find("Arnold_RLM")
                wol0 = root.find("WOL_0")
                wol1 = root.find("WOL_1")
                wol2 = root.find("WOL_2")
                wol3 = root.find("WOL_3")

                if arnoldLic is not None:
                    arnoldLic.text = str(self.gui.lineEdit_arnoldLic.text())
                else:
                    arnoldLic = ET.Element("Arnold_RLM")
                    arnoldLic.text = str(self.gui.lineEdit_arnoldLic.text())
                    root.append(arnoldLic)

                if wol0 is not None:
                    wol0.set("Address", str(self.gui.lineEdit_WOL_MAC_0.text()))
                    wol0.set("Description", str(self.gui.lineEdit_WOL_Des_0.text()))
                    wol0.set("startUp", str(self.gui.checkBox_startUp_0.isChecked()))
                else:
                    wol0 = ET.Element("WOL_0", Address=str(self.gui.lineEdit_WOL_MAC_0.text()), Description=str(self.gui.lineEdit_WOL_Des_0.text()), startUp=str(self.gui.checkBox_startUp_0.isChecked()))
                    root.append(wol0)

                if wol1 is not None:
                    wol1.set("Address", str(self.gui.lineEdit_WOL_MAC_1.text()))
                    wol1.set("Description", str(self.gui.lineEdit_WOL_Des_1.text()))
                    wol1.set("startUp", str(self.gui.checkBox_startUp_1.isChecked()))

                else:
                    wol1 = ET.Element("WOL_1", Address=str(self.gui.lineEdit_WOL_MAC_1.text()), Description=str(self.gui.lineEdit_WOL_Des_1.text()), startUp=str(self.gui.checkBox_startUp_1.isChecked()))
                    root.append(wol1)

                if wol2 is not None:
                    wol2.set("Address", str(self.gui.lineEdit_WOL_MAC_2.text()))
                    wol2.set("Description", str(self.gui.lineEdit_WOL_Des_2.text()))
                    wol2.set("startUp", str(self.gui.checkBox_startUp_2.isChecked()))
                else:
                    wol2 = ET.Element("WOL_2", Address=str(self.gui.lineEdit_WOL_MAC_2.text()), Description=str(self.gui.lineEdit_WOL_Des_2.text()), startUp=str(self.gui.checkBox_startUp_2.isChecked()))
                    root.append(wol2)

                if wol3 is not None:
                    wol3.set("Address", str(self.gui.lineEdit_WOL_MAC_3.text()))
                    wol3.set("Description", str(self.gui.lineEdit_WOL_Des_3.text()))
                    wol3.set("startUp", str(self.gui.checkBox_startUp_3.isChecked()))
                else:
                    wol3 = ET.Element("WOL_3", Address=str(self.gui.lineEdit_WOL_MAC_3.text()), Description=str(self.gui.lineEdit_WOL_Des_3.text()), startUp=str(self.gui.checkBox_startUp_3.isChecked()))
                    root.append(wol3)

                tree.write(configPath + os.sep + "Config.xml")

            os.environ["solidangle_LICENSE"] = str(self.gui.lineEdit_arnoldLic.text())

        except ValueError:
            pass

    def fireRoboCopy(self):
        if sys.platform == "darwin":  # macOS
            pass
        if sys.platform == "linux2":  # Linux
            pass
        if sys.platform == "win32":  # Windows
            trayIcon.showMessage("ns_Startup", "Robocopy latest version & restart.", icon=QSystemTrayIcon.Information, msecs=10000)
            sleep(3)
            app.quit()
            subprocess.call(["robocopy", "P:/Python/ns_Startup", "C:/Users/" + user + "/Desktop/Python_Scripts/ns_Startup/", "/S", "/LOG:robocopy_log.txt"])
            subprocess.Popen("C:/Users/" + user + "/Desktop/Python_Scripts/ns_Startup/ns_Startup.py 1", shell=True)







if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    guiTray = uic.loadUi("UI" + os.sep + "ns_Startup.ui")
    trayIcon = SystemTrayIcon(QtGui.QIcon("UI" + os.sep + "favicon.ico"), guiTray)
    trayIcon.show()

    gui = MainWindow()
    sys.exit(app.exec_())










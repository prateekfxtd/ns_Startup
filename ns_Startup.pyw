version = "v0.1.43"
## Niclas Schlapmann - Freelance 3D Generalist
## www.enoni.de
## hello@enoni.de
## ns_Startup
## 26.02.2020
##############################################################################################################
## EDIT FROM HERE ## #########################################################################################
import sys
import os
import getpass
import xml.etree.cElementTree as ET
import xml.dom.minidom
import ns_Utility
import subprocess
import shutil
from threading import *
import time
import socket
from PyQt4.uic import *
from datetime import datetime
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui, QtCore, uic
from functools import partial
import json
import random
import pyaudio
import wave
import resource
##############################################################################################################
## DEFAULTS ## ###############################################################################################
lt = time.localtime()
jahr, monat, tag = lt[0:3]
ns_date = str(jahr)[2:4]+str(monat).zfill(2)+str(tag).zfill(2)
user = getpass.getuser()
## Lookup Pathes/Defaults ##
scriptRoot = sys.path[0]
presetPath = scriptRoot + os.sep + "Presets"
globalPresetPath = ("P:/_Global_Presets").replace("/", os.sep)
localPackagePath = scriptRoot + os.sep + "Packages"
configPath = scriptRoot + os.sep + "Config"
searchPathHoudiniWIN = ("C:/Program Files/Side Effects Software").replace("/", os.sep)
# searchPathHoudiniLINUX "" TODO
# searchPathHoudiniMAC  = "" TODO
renderServicePath = ""
searchPathWorkgroups = ("L:/Workgroups").replace("/", os.sep)
searchPathArnold = searchPathWorkgroups + os.sep + "Workgroup_HTOA"
searchPathVray = searchPathWorkgroups + os.sep + "Workgroup_V-Ray"
searchPathOctane = searchPathWorkgroups + os.sep + "Workgroup_Octane"
searchPathRedshift= searchPathWorkgroups + os.sep + "Workgroup_Redshift"
## Update Pathes ##
maintenanceScriptPath = ("P:/Python/ns_Startup").replace("/", os.sep)
maintenanceRenderScriptPath = ("P:/Python/Deadline_Client_Scripts").replace("/", os.sep)
localRenderSubmitterScripLocationDEADLINE = ("C:/Users/" + user + "/AppData/Local/Thinkbox/Deadline10/submitters/HoudiniSubmitter").replace("/", os.sep) 
##############################################################################################################
## CHAT CLIENT DEFAULTS ## ###################################################################################
## Loggin ##
chat_host = "localhost"
chat_alias = user
## Socket ##
TCP_IP_DEFAULT = "YourServerName"
TCP_PORT_DEFAULT = 666
TCP_BUFFER_DEFAULT = 4096
TIME_OUT = 4000
USER = user
MACHINE = socket.gethostname()
SEND_FLAG = False
STOP_FLAG = False
MESSAGE = ""
##############################################################################################################
## CLASSES ## ################################################################################################


class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)
        
        self.menu = QtGui.QMenu(parent)
        self.submenu_packages = QtGui.QMenu("HOU Packages Quickstarter", parent)
        self.submenu_packages.setIcon(QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "houIcon.png")))
        
        self.submenu_packages_local = QtGui.QMenu("local (" + MACHINE + ")", parent)
        self.submenu_packages_local.setIcon(QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "folderIcon.png")))
        self.submenu_packages_global = QtGui.QMenu("global (NS-Storage\\Projects)", parent)
        self.submenu_packages_global.setIcon(QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "networkIcon.png")))
        
        openAction = self.menu.addAction(QtGui.QIcon(QtGui.QPixmap("Logo" + os.sep + "Logo.png")), "Open ns_Startup " + version)
        self.menu.addSeparator()
        
        self.menu.addMenu(self.submenu_packages) 
        self.submenu_packages.addMenu(self.submenu_packages_local)
        self.submenu_packages.addSeparator()
        self.submenu_packages.addMenu(self.submenu_packages_global)
        
        self.menu.addSeparator()
        exitAction = self.menu.addAction(QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "unselectedIcon.png")), "Exit")

        ## SIGNALS ##
        self.activated.connect(self.updatePackages)
        exitAction.triggered.connect(QtGui.QApplication.quit)
        openAction.triggered.connect(self.openGUI)
        
        self.setContextMenu(self.menu)
        self.setToolTip("ns_Startup Tray " + version)


    def openGUI(self):
        gui.openGUI()


    def openPackageLocation(self, ns_path):
        if os.path.exists(ns_path.replace("/", os.sep)):
            if sys.platform == "darwin":  ## macOS ##
                subprocess.Popen(["open", "--", ns_path.replace("/", os.sep)])
            if sys.platform == "linux2":  ## Linux ##
                subprocess.Popen(["xdg-open", "--", ns_path.replace("/", os.sep)])
            if sys.platform == "win32":  ## Windows ##
                subprocess.Popen(["explorer", ns_path.replace("/", os.sep)])
        else:
            QtGui.QMessageBox.warning(self, "ns_Startup - Packages", "Cant open package location.", QtGui.QMessageBox.Ok)

    def managePackages(self, ns_path):
    	gui.openManagePackagesPanel()
   
    
    def updatePackages(self):
        self.submenu_packages_global.clear()
        self.submenu_packages_local.clear()
        try:
            ## GATHER Packages ##
            ## local ##
            packagesLocalPath = scriptRoot + os.sep + "Packages"
            packagesLocalDirs = [d for d in os.listdir(packagesLocalPath) if os.path.isdir(os.path.join(packagesLocalPath, d))]
            # localActionArray = []
            for package in packagesLocalDirs:
            	if package not in ["_tmp"]:
	                icon = QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "noicon.png"))
	                ## try find icons ##
	                if os.path.isfile(packagesLocalPath + os.sep + package + os.sep + "icon.png"):
	                    icon = QtGui.QIcon(QtGui.QPixmap(packagesLocalPath + os.sep + package + os.sep + "icon.png"))

	                openP = self.submenu_packages_local.addAction(icon, package)
	                openP.triggered.connect(lambda checked, a=package: self.execute_package_local(checked, a))
            
            self.submenu_packages_local.addSeparator()
            
            openPL = self.submenu_packages_local.addAction(QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "folderIcon.png")), "[ Open package location ]")
            openPL.triggered.connect(lambda checked, a=(scriptRoot + os.sep + "Packages"): self.openPackageLocation(a))
            managePG = self.submenu_packages_local.addAction(QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "packageManage.png")), "[ Manage packages ]")
            managePG.triggered.connect(lambda checked, a=(globalPresetPath + os.sep + "Packages"): self.managePackages(a))

            ## global ##
            packagesGlobalPath = globalPresetPath + os.sep + "Packages"
            packagesGlobalDirs = [d for d in os.listdir(packagesGlobalPath) if os.path.isdir(os.path.join(packagesGlobalPath, d))]
            # localActionArray = []
            for package in packagesGlobalDirs:
            	if package not in ["_tmp"]:
	                icon = QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "noicon.png"))
	                ## try find icons ##
	                if os.path.isfile(packagesGlobalPath + os.sep + package + os.sep + "icon.png"):
	                    icon = QtGui.QIcon(QtGui.QPixmap(packagesGlobalPath + os.sep + package + os.sep + "icon.png"))

	                openP = self.submenu_packages_global.addAction(icon, package)
	                openP.triggered.connect(lambda checked, a=package: self.execute_package_global(checked, a))
            
            self.submenu_packages_global.addSeparator()
            
            openPG = self.submenu_packages_global.addAction(QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "networkIcon.png")), "[ Open package location ]")
            openPG.triggered.connect(lambda checked, a=(globalPresetPath + os.sep + "Packages"): self.openPackageLocation(a))
            managePG = self.submenu_packages_global.addAction(QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "packageManage.png")), "[ Manage packages ]")
            managePG.triggered.connect(lambda checked, a=(globalPresetPath + os.sep + "Packages"): self.managePackages(a))
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


    def execute_package_local(self, checked, package_name):
        try:
            with open(scriptRoot + os.sep + "Packages" + os.sep + "hou_references.json") as f:
                json_ref_data = json.load(f)

            for items in json_ref_data['data']:
                if items['package'] == package_name:
                    exe_path = items['hou_path']
                    houVersion = items['hou_version']
                    exeVersion = items['hou_bin']

                    if sys.platform == "darwin": ## macOS ##
                        pass
                        #TODO macOS version
                    if sys.platform == "linux2": ## Linux ##
                        pass
                        #TODO linux version
                    if sys.platform == "win32": ## Windows ##
                        os.environ["HOUDINI_PACKAGE_DIR"] = str(scriptRoot + os.sep + "Packages" + os.sep + package_name)
                        subprocess.Popen([exe_path])
                        self.showMessage("", "ns_Startup> is starting a Houdini session via local packages.", icon=QSystemTrayIcon.Information)                     
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            self.showMessage("", "ns_Startup> something went wrong.", icon=QSystemTrayIcon.Information)


    def execute_package_global(self, checked, package_name):
        try:
            with open(globalPresetPath + os.sep + "Packages" + os.sep + "hou_references.json") as f:
                json_ref_data = json.load(f)

            for items in json_ref_data['data']:
                if items['package'] == package_name:
                    exe_path = items['hou_path']
                    houVersion = items['hou_version']
                    exeVersion = items['hou_bin']

                    if sys.platform == "darwin": ## macOS ##
                        pass
                        #TODO macOS version
                    if sys.platform == "linux2": ## Linux ##
                        pass
                        #TODO linux version
                    if sys.platform == "win32": ## Windows ##
                        os.environ["HOUDINI_PACKAGE_DIR"] = str(globalPresetPath + os.sep + "Packages" + os.sep + package_name)
                        subprocess.Popen([exe_path])
                        self.showMessage("", "ns_Startup> is starting a Houdini session via global packages.", icon=QSystemTrayIcon.Information)                           
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            self.showMessage("", "ns_Startup> something went wrong.", icon=QSystemTrayIcon.Information)


class ClientThread(QThread):
    def __init__(self, gui, parent=None):
        QThread.__init__(self, parent)
        self.TCP_IP = str(gui.lineEdit_chat_host.text())
        self.TCP_PORT = TCP_PORT_DEFAULT
        self.TCP_PORT2 = self.TCP_PORT + 1
        self.BUFFER_SIZE = TCP_BUFFER_DEFAULT
        self.threadStack = []
        if gui.lineEdit_alias.text() != "":
            self.ALIAS = str(gui.lineEdit_alias.text())
        else:
            self.ALIAS =  USER + "@" + MACHINE
        global STOP_FLAG
        STOP_FLAG = False


    def run(self):
        try:
            self.sendThread = ServerThreadSend(self)
            self.sendThread.daemon = True
            self.readThread = ServerThreadRead(self)
            self.readThread.daemon = True
            self.sendThread.start()
            self.readThread.start()
            self.threadStack.append(self.readThread)
            self.threadStack.append(self.sendThread)

            self.emit(SIGNAL("addEntry(QString)"), "                                                   ## Chat Client started. ##" + "::::" + socket.gethostbyname(socket.gethostname()))
            self.emit(SIGNAL("setConnectButton(QString)"), "Connected")
        except Exception as e:
            self.emit(SIGNAL("addEntry(QString)"), "                                                   ## Chat Client cant connect. ##" + "::::" + socket.gethostbyname(socket.gethostname()))
            self.emit(SIGNAL("setConnectButton(QString)"), "Disconnected")
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


    def stop(self):
        global STOP_FLAG
        STOP_FLAG = True


class ServerThreadSend(Thread):
    def __init__(self, clientThread):
        Thread.__init__(self)
        self.clientThread = clientThread
        self.socketSend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketSend.connect((self.clientThread.TCP_IP, self.clientThread.TCP_PORT))
        self.DATA_RECIEVED = self.dataRecieved(self.socketSend, "arg")  ## TIMEOUT ##
        self.ALIAS = clientThread.ALIAS


    def dataToSend(self, socketToSend, typeString, dataString, ipString):
        DATA_TO_SEND = json.dumps({"arg": [typeString, dataString, ipString]})
        socketToSend.send(DATA_TO_SEND.encode('utf-8'))


    def dataRecieved(self, recievingSocket, indexString):
        try:
            DATA_RECIEVED = (json.loads(recievingSocket.recv(self.clientThread.BUFFER_SIZE).decode('utf-8'))).get(indexString)
            return DATA_RECIEVED
        except:
            self.socketSend.close()
            # print("ServerThreadSend exit. (dataRecieved)")
            sys.exit()


    def run(self):
        self.dataToSend(self.socketSend, "m", datetime.now().strftime("%H:%M:%S") + " > " + self.ALIAS + " joined the Chat. Welcome.", socket.gethostbyname(socket.gethostname()))
        self.DATA_RECIEVED = self.dataRecieved(self.socketSend, "arg")
        self.dataToSend(self.socketSend, "u", self.ALIAS, socket.gethostbyname(socket.gethostname()))
        self.DATA_RECIEVED = self.dataRecieved(self.socketSend, "arg")
        self.clientThread.emit(SIGNAL("addEntry(QString)"), datetime.now().strftime("%H:%M:%S") + " > " + self.DATA_RECIEVED[1].replace(self.ALIAS, "YOU") + "::::" + "Server")

        try:
            while True:
                time.sleep(0.1)
                global SEND_FLAG
                global MESSAGE
                global STOP_FLAG

                if SEND_FLAG:
                    SEND_FLAG = False
                    self.dataToSend(self.socketSend, "m", datetime.now().strftime("%H:%M:%S") + " > " + self.ALIAS + " > " + MESSAGE, socket.gethostbyname(socket.gethostname()))
                    self.DATA_RECIEVED = self.dataRecieved(self.socketSend, "arg")
                    print("data_recv: " + self.DATA_RECIEVED[1])

                if STOP_FLAG:
                    self.dataToSend(self.socketSend, "m", datetime.now().strftime("%H:%M:%S") + " > " + self.ALIAS + " leaved the Chat. Bye.", socket.gethostbyname(socket.gethostname()))
                    self.DATA_RECIEVED = self.dataRecieved(self.socketSend, "arg")
                    print("data_recv: " + self.DATA_RECIEVED[1])
                    time.sleep(3)
                    self.dataToSend(self.socketSend, "c", "_exit_", socket.gethostbyname(socket.gethostname()))
                    self.DATA_RECIEVED = self.dataRecieved(self.socketSend, "arg")
                    print("data_recv: " + self.DATA_RECIEVED[1])

                    if self.DATA_RECIEVED[0] == "c":
                        if self.DATA_RECIEVED[1] == "_exit_ok_":
                            break

            # print("ServerThreadSend exit.")
            self.socketSend.close()
            sys.exit()
        except socket.error:
            print("ServerThreadSend exit. (socket.error)")
            self.socketSend.close()
            sys.exit()
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    def kill(self):
        self.socketSend.close()
        # print("ServerThreadSend exit. (kill)")
        sys.exit()


class ServerThreadRead(Thread):
    def __init__(self, clientThread):
        Thread.__init__(self)
        self.clientThread = clientThread
        self.socketRead = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketRead.connect((self.clientThread.TCP_IP, self.clientThread.TCP_PORT2))
        self.DATA_RECIEVED = self.dataRecieved(self.socketRead, "arg")
        ## WELCOME MESSAGE ##
        self.clientThread.emit(SIGNAL("addEntry(QString)"), "                         " + self.DATA_RECIEVED[1] + "::::" + self.DATA_RECIEVED[2])


    def dataToSend(self, socketToSend, typeString, dataString, ipString):
        DATA_TO_SEND = json.dumps({"arg": [typeString, dataString, ipString]})
        socketToSend.send(DATA_TO_SEND.encode('utf-8'))


    def dataRecieved(self, recievingSocket, indexString):
        try:
            DATA_RECIEVED = (json.loads(recievingSocket.recv(self.clientThread.BUFFER_SIZE).decode('utf-8'))).get(indexString)
            return DATA_RECIEVED
        except:
            self.socketRead.close()
            # print("ServerThreadRead exit. (dataRecieved)")
            self.clientThread.emit(SIGNAL("addEntry(QString)"), "                                          ## Chat Client stopped Connection. ##" + "::::" + socket.gethostbyname(socket.gethostname()))
            self.clientThread.stop()
            sys.exit()
    

    def run(self):
        try:
            while True:
                time.sleep(0.1)
                self.DATA_RECIEVED = self.dataRecieved(self.socketRead, "arg")
                if self.DATA_RECIEVED[0] == "m":
                    ## client gui chat ##
                    self.clientThread.emit(SIGNAL("addEntry(QString)"), self.DATA_RECIEVED[1] + "::::" + self.DATA_RECIEVED[2])
        except socket.error:
            self.socketRead.close()
            print("ServerThreadRead exit. (socket.error)")
            sys.exit()
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


    def kill(self):
        self.socketRead.close()
        # print("ServerThreadRead exit. (kill)")
        sys.exit()


class PlayNotificationSound(Thread):
    def __init__(self):
        self.SOUND_NOTI_PATH = scriptRoot + os.sep + "Sounds" + os.sep + "Notification.wav"
        self.SOUND_ENTER_PATH = scriptRoot + os.sep + "Sounds" + os.sep + "Enter.wav"
        self.SOUND_LEFT_PATH = scriptRoot + os.sep + "Sounds" + os.sep + "Left.wav"
        self.SOUND_HOLYS_PATH = scriptRoot + os.sep + "Sounds" + os.sep + "HolyShit.wav"


    def run(self, type):
        if type == "enter":
            self.playSound(self.SOUND_ENTER_PATH)
        elif type == "notif":
            self.playSound(self.SOUND_NOTI_PATH)
        elif type == "left":
            self.playSound(self.SOUND_LEFT_PATH)
        elif type == "holy":
            self.playSound(self.SOUND_HOLYS_PATH)


    def playSound(self, path):
        self.f = wave.open(path, "rb")
        chunk = 1024
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(self.f.getsampwidth()), channels=self.f.getnchannels(), rate=self.f.getframerate(), output=True)
        data = self.f.readframes(chunk)
        while data:
            stream.write(data)
            data = self.f.readframes(chunk)
        stream.stop_stream()
        stream.close()
        p.terminate()


class MainWindow(QtGui.QMainWindow):
    
    presetFlag = False
    globalPresetLocation = ""
    checkerRenderer = []
    checkerWorkgroups = []
    selectedRenderer = []
    selectedWorkgroups = []
    workgroups = []
    workgroups_xml = []
    workgroups_path = []
    workgroups_path_xml = []
    renderer = []
    renderer_xml = []
    renderer_path = []
    renderer_path_xml = []
    apps = []
    apps_xml = []
    apps_path = []
    apps_path_xml = []
    selectedPresetCombo = 0


    def __init__(self):
        ## INIT ##
        QtGui.QMainWindow.__init__(self)
        self.gui = uic.loadUi("UI" + os.sep + "ns_Startup.ui")
        self.gui.setWindowTitle("ns_Startup " + version)
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(scriptRoot + os.sep + "Logo" + os.sep + "Logo.png")))
        self.resolution = QtGui.QDesktopWidget().screenGeometry()
        self.gui.move(self.resolution.width() - 473, self.resolution.height() - 980)
        self.gui.closeEvent = self.closeEvent
        self.gui.lineEdit_globalPresetLocation.setText(globalPresetPath)
        self.gui.lineEdit_chat_host.setText(chat_host)
        self.gui.lineEdit_alias.setText(chat_alias)

        self.envDialog = loadUi("UI" + os.sep + "ns_EnvCheck.ui")
        self.presetSaveDialog = loadUi("UI" + os.sep + "presetSave.ui")
        self.managePackages = loadUi("UI" + os.sep + "ns_ManagePackages.ui")
        
        self.gui.textEdit_debug_log.setText(datetime.now().strftime("%H:%M:%S") + "> ns_Startup " + version + "\n------------------------------------------")

        ## SIGNALS BUTTONS ##
        self.connect(self.gui.pushButton_savePreset, QtCore.SIGNAL('clicked()'), self.savePresetButton)
        self.connect(self.gui.pushButton_deletePreset, QtCore.SIGNAL('clicked()'), self.deleteCurrentPreset)
        self.connect(self.gui.pushButton_pushPreset, QtCore.SIGNAL('clicked()'), self.pushCurrentPreset)
        self.connect(self.gui.pushButton_defaultPreset, QtCore.SIGNAL('clicked()'), self.saveDefaultPreset)
        self.connect(self.gui.pushButton_open, QtCore.SIGNAL('clicked()'), self.openApplication)
        self.connect(self.gui.pushButton_setArnoldLic, QtCore.SIGNAL('clicked()'), self.setArnoldLic)
        self.connect(self.gui.pushButton_WOL_0, QtCore.SIGNAL('clicked()'), self.send_WOL_0)
        self.connect(self.gui.pushButton_WOL_1, QtCore.SIGNAL('clicked()'), self.send_WOL_1)
        self.connect(self.gui.pushButton_WOL_2, QtCore.SIGNAL('clicked()'), self.send_WOL_2)
        self.connect(self.gui.pushButton_WOL_3, QtCore.SIGNAL('clicked()'), self.send_WOL_3)
        self.connect(self.gui.pushButton_update, QtCore.SIGNAL('clicked()'), self.fireRoboCopy)
        self.connect(self.gui.pushButton_saveConfig, QtCore.SIGNAL('clicked()'), self.saveConfig)
        self.connect(self.presetSaveDialog.pushButton_savePreset, QtCore.SIGNAL('clicked()'), self.getNewPresetNameAndSave)
        self.connect(self.gui.pushButton_setGlobalPresetsLocation, QtCore.SIGNAL('clicked()'), self.setGlobalPresetLocation)
        self.connect(self.gui.pushButton_setRenderService, QtCore.SIGNAL('clicked()'), self.setRenderServiceLocation)
        self.connect(self.gui.pushButton_check, QtCore.SIGNAL('clicked()'), self.openEnvPanel)
        self.connect(self.gui.pushButton_managePackages, QtCore.SIGNAL('clicked()'), self.openManagePackagesPanel)
        self.connect(self.gui.pushButton_clear_log, QtCore.SIGNAL('clicked()'), self.clearLog)
        self.connect(self.gui.pushButton_chat_connection, QtCore.SIGNAL('clicked()'), self.startChatClient)
        self.connect(self.gui.pushButton_chat_send, QtCore.SIGNAL('clicked()'), self.sendMessage)

        self.presetSaveDialog.label_presetLogo.mousePressEvent = self.getPresetLogo

        ## SIGNALS TABWIDGET ##
        self.gui.tabWidget.currentChanged.connect(self.tabChange)

        ## SIGNALS LINE-EDIT ##
        self.gui.textEdit_chat_out.returnPressed.connect(self.sendMessage)

        ## SIGNALS COMBO ##
        self.connect( self.managePackages.comboBox_json_files, QtCore.SIGNAL('currentIndexChanged(int)'), self.loadJSONFile_PackageManager)

        ## Plain text only for env vars##
        self.gui.textEdit_addParameters.setAcceptRichText(False)

        ## RUN ##
        self.loadConfigSettings()
        self.checkStartupVersion(notify=True)


    def startChatClient(self):
        if self.gui.pushButton_chat_connection.text() in ["Connecting", "Connect", "Disconnected"]:
            self.gui.listWidget_chat_in.setRowCount(0)
            self.clientThread = ClientThread(self.gui)
            self.gui.connect(self.clientThread, SIGNAL("setConnectButton(QString)"), self.setConnectButton)
            self.gui.connect(self.clientThread, SIGNAL("addEntry(QString)"), self.addEntry)
            self.clientThread.run()

            ## Debug Log ##
            prev_text = self.gui.textEdit_debug_log.toPlainText()
            prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> start Chat client"
            self.gui.textEdit_debug_log.setText(prev_text)
            ## Debug Log - End ##

            self.gui.pushButton_chat_connection.setText("Connected")
            self.gui.pushButton_chat_connection.setStyleSheet("""
            QPushButton{
            color: rgb(0 ,230, 0);
            background-color: rgb(31, 31, 31);
            border-radius: 10px;
            }

            QPushButton:hover {
                background-color: rgb(150, 0, 0);
                color: rgb(255, 0, 0);
                border-style: inset;
            }

            QPushButton:pressed {
                background-color:  rgb(0, 100, 0);
                color: rgb(0, 230, 0);
                border-style: inset;
            }
            """)
        elif self.gui.pushButton_chat_connection.text() in ["Disconnecting", "Disconnect", "Connected"]:
            self.gui.pushButton_chat_connection.setText("Disconnected")
            self.gui.pushButton_chat_connection.setStyleSheet("""
            QPushButton{
            color: rgb(230 ,0 ,0);
            background-color: rgb(31, 31, 31);
            border-radius: 10px;
            }

            QPushButton:hover {
                background-color: rgb(0, 100, 0);
                color: rgb(0, 150, 0);
                border-style: inset;
            }

            QPushButton:pressed {
                background-color:  rgb(0, 150, 0);
                color: rgb(0, 230, 0);
                border-style: inset;
            }
            """)
            self.clientThread.stop()
            ## Debug Log ##
            prev_text = self.gui.textEdit_debug_log.toPlainText()
            prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> stop Chat client"
            self.gui.textEdit_debug_log.setText(prev_text)
            ## Debug Log - End ##
        else:
            pass

    
    def setConnectButton(self, text):
        self.gui.pushButton_chat_connection.setText(text)


    def addEntry(self, text):
        playSound = PlayNotificationSound()
        label_text = text.toUtf8()
        label_text = str(label_text).decode('utf-8')
        parts = label_text.split("::::")

        text = parts[0]
        text_ip = parts[1]


        random.seed(text_ip + text_ip)
        rand_rgb = random.randint(0, 200)

        i = self.gui.listWidget_chat_in.rowCount()
        self.gui.listWidget_chat_in.setRowCount(i + 1)

        chat_label = QLabel(text)


        chat_label.setMinimumWidth(430)
        chat_label.setMinimumHeight(30)
        chat_cellWidget = QWidget()

        if label_text.find("##") == -1:
            if label_text.find(" joined the Chat. Welcome.") != -1:
                chat_cellWidget.setStyleSheet('''
                            QLabel{
                            background-color: rgb(0, 50, 100);
                            color: rgb(0, 140, 240);
                            }''')
            elif label_text.find(" leaved the Chat. Bye.") != -1:
                chat_cellWidget.setStyleSheet('''
                            QLabel{
                            background-color: rgb(100, 0, 0);
                            color: rgb(230, 0 ,0);
                            }''')
            else:
                chat_cellWidget.setStyleSheet('''
                            QLabel{
                            background-color: rgb(''' + str(rand_rgb) + ''', ''' + str(rand_rgb/2) + ''',''' +  str(rand_rgb) + ''');
                            color: rgb(255, 255, 255);
                            }''')
                chat_label.setTextInteractionFlags(Qt.TextEditorInteraction)
        else:
            if label_text.find("## Chat Client cant connect. ##") != -1:
                chat_cellWidget.setStyleSheet('''
                            QLabel{
                            background-color: rgb(150, 0, 0);
                            color: rgb(255, 0, 0);
                            }''')
            elif label_text.find("## Chat Client stopped Connection. ##") != -1:
                chat_cellWidget.setStyleSheet('''
                            QLabel{
                            background-color: rgb(150, 0, 0);
                            color: rgb(255, 0, 0);
                            }''')
                self.gui.pushButton_chat_connection.setText("Disconnected")
                self.gui.pushButton_chat_connection.setStyleSheet("""
                QPushButton{
                color: rgb(230 ,0 ,0);
                background-color: rgb(31, 31, 31);
                border-radius: 10px;
                }

                QPushButton:hover {
                    background-color: rgb(0, 100, 0);
                    color: rgb(0, 150, 0);
                    border-style: inset;
                }

                QPushButton:pressed {
                    background-color:  rgb(0, 150, 0);
                    color: rgb(0, 230, 0);
                    border-style: inset;
                }
                """)
                self.clientThread.stop()
            else:
                chat_cellWidget.setStyleSheet('''
                            QLabel{
                            background-color: rgb(0, 100, 0);
                            color: rgb(0, 230, 0);
                            }''')


        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(chat_label)
        chat_cellWidget.setLayout(layout)
        self.gui.listWidget_chat_in.setCellWidget(i, 0, chat_cellWidget)

        ## Notification ##
        if label_text.find("##") == -1:
            if self.gui.checkBox_chat_notifications.isChecked():
                if self.gui.tabWidget.currentIndex() != 2:
                    trayIcon.showMessage("ns_Startup " + version + " Chat", text, icon=QSystemTrayIcon.Information, msecs=10000)

        ## Sounds ##
        if label_text.find(" joined the Chat. Welcome.") != -1:
            if self.gui.checkBox_chat_notifications_sound.isChecked():
                try:
                    playSound.run("enter")
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        if label_text.find(" leaved the Chat. Bye.") != -1:
            if self.gui.checkBox_chat_notifications_sound.isChecked():
                try:
                    playSound.run("left")
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


        if label_text.find("## Chat Client cant connect. ##") != -1:
            if self.gui.checkBox_chat_notifications_sound.isChecked():
                try:
                    playSound.run("holy")
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


    def sendMessage(self):
        global MESSAGE
        global SEND_FLAG
        MESSAGE = unicode(self.gui.textEdit_chat_out.text()).encode('utf-8')
        SEND_FLAG = True
        self.gui.textEdit_chat_out.setText("")


    def tabChange(self, index):
        if index == 1:
            self.checkStartupVersion(notify=False)


    def checkStartupVersion(self, notify):
        button = self.gui.pushButton_update
        if os.path.exists(maintenanceScriptPath):
            button.setEnabled(True)
            try:
                devScript = open(maintenanceScriptPath + os.sep + "ns_Startup.pyw", "r")
                tmp = devScript.readline().split("\"")
                devScript.close()
                alarm = True

                if tmp[1] == version:
                    if notify:
                        trayIcon.showMessage("ns_Startup " + version, "Scripts are up-to-date.", icon=QSystemTrayIcon.Information, msecs=10000)
                    alarm = False
                else:
                    if notify:
                        trayIcon.showMessage("ns_Startup " + version, "Please update to Version: " + tmp[1], icon=QSystemTrayIcon.Information, msecs=10000)

                if alarm:
                    button.setText("Update ns_Startup to " + tmp[1])
                    button.setStyleSheet("""
                    QPushButton{
                    color: rgb(255 ,0 ,0);
                    background-color: rgb(50, 50, 50);
                    border-radius: 5px;
                    border: 1px solid rgb(40, 40, 40);
                    }
        
                    QPushButton:hover {
                    background-color: rgb(255, 0, 0);
                    }
        
                    QPushButton:pressed {
                    background-color: rgb(255, 0, 0);
                    }
                    """)
                    button.effect = QGraphicsColorizeEffect(button)
                    button.setGraphicsEffect(button.effect)
                    button.anim = QtCore.QPropertyAnimation(button.effect, "color", button)
                    button.anim.setStartValue(QtGui.QColor(0, 0, 0))
                    button.anim.setEndValue(QtGui.QColor(0, 0, 0))
                    button.anim.setKeyValueAt(0.5, QtGui.QColor(150, 0, 0))
                    button.anim.setDuration(250)
                    button.anim.setLoopCount(-1)
                    button.effect.setStrength(1)
                    button.anim.start()
                else:
                    button.setText("ns_Startup is up-to-date")
                    try:
                        button.anim.stop()
                        button.effect.setStrength(0)
                        button.setStyleSheet("""
                        QPushButton{
                        background-color: rgb(50, 50, 50);
                        border-radius: 5px;
                        border: 1px solid rgb(40, 40, 40);
                        }
                        
                        QPushButton:hover {
                            background-color: rgb(80, 80, 80);
                            color: rgb(0, 50, 0);
                        }
                        
                        QPushButton:pressed {
                            background-color:  rgb(0, 255, 0);
                            color: rgb(0, 255, 0);
                        }
                        """)
                    except:
                        button.setStyleSheet("""
                        QPushButton{
                        color: rgb(0 ,255 ,0);
                        background-color: rgb(0, 100, 0);
                        border-radius: 5px;
                        border: 1px solid rgb(40, 40, 40);
                        }
        
                        QPushButton:hover {
                            background-color: rgb(80, 80, 80);
                            color: rgb(0, 255, 0);
                        }
        
                        QPushButton:pressed {
                            background-color:  rgb(0, 255, 0);
                            color: rgb(0,230,0);
                        }
                        """)
            except Exception as e:
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        else:
            button.setText("Nothing to update")
            button.setEnabled(False)

        ## Debug Log ##
        prev_text = self.gui.textEdit_debug_log.toPlainText()
        prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> perform a Version check"
        self.gui.textEdit_debug_log.setText(prev_text)
        ## Debug Log - End ##


    def clearLog(self):
        self.gui.textEdit_debug_log.setText("")
        self.gui.textEdit_debug_log.setText(datetime.now().strftime("%H:%M:%S") + "> ns_Startup " + version + "\n------------------------------------------")


    def clearArrays(self):
        self.workgroups = []
        self.workgroups_xml = []
        self.workgroups_path = []
        self.workgroups_path_xml = []
        self.renderer = []
        self.renderer_xml = []
        self.renderer_path = []
        self.renderer_path_xml = []
        self.apps = []
        self.apps_xml = []
        self.apps_path = []
        self.apps_path_xml = []


    def clearArrays_xml(self):
        self.workgroups_xml = []
        self.workgroups_path_xml = []
        self.renderer_xml = []
        self.renderer_path_xml = []
        self.apps_xml = []
        self.apps_path_xml = []


    def checkEnv(self):
        ## Debug Log ##
        prev_text = self.gui.textEdit_debug_log.toPlainText()
        prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> ENV checkup"
        self.gui.textEdit_debug_log.setText(prev_text)
        ## Debug Log - End ##

        alarm = False
        button = self.gui.pushButton_check
        self.envDialog.listWidget.clear()

        ## Apps ##
        x = 0
        for i in self.apps_xml:
            present = False
            xx = 0
            for ii in self.apps:
                if os.path.exists(self.apps_path_xml[x]):
                    present = True
                
                xx = xx + 1

            envDialogItem = loadUi("UI" + os.sep + "ns_EnvCheck_Item.ui")
            envDialogItem.label_name.setText(i)
            path = self.apps_path_xml[x]
            envDialogItem.label_path.setText(path)
            itemN = QtGui.QListWidgetItem()
            widget = QtGui.QWidget()
            widgetLayout = QtGui.QHBoxLayout()
            widgetLayout.addWidget(envDialogItem)
            widget.setLayout(widgetLayout)
            widgetLayout.addStretch()
            itemN.setSizeHint(widget.sizeHint())
        
            if present:                
                envDialogItem.label_status.mouseReleaseEvent = lambda event, arg=path :self.openLocation(arg)
            else:
                alarm = True
                envDialogItem.label_status.setStyleSheet("""
                QLabel{
                background-color: rgb(200, 0, 0);
                border: 1px solid rgb(40, 40, 40);
                }
                                
                QLabel:hover{
                background-color: None;
                }
                
                QLabel:pressed{
                background-color: None;
                }
                """)

            self.envDialog.listWidget.addItem(itemN)
            self.envDialog.listWidget.setItemWidget(itemN, widget)
            x = x + 1

        ## Renderer ##
        x = 0
        for i in self.renderer_xml:
            present = False
            xx = 0
            for ii in self.renderer:
                if self.renderer_path_xml[x] == self.renderer_path[xx] and os.path.exists(self.renderer_path_xml[x]):
                    present = True
                xx = xx + 1

                envDialogItem = loadUi("UI" + os.sep + "ns_EnvCheck_Item.ui")
                envDialogItem.label_name.setText(i)
                path = self.renderer_path_xml[x]
                envDialogItem.label_path.setText(path)
                itemN = QtGui.QListWidgetItem()
                widget = QtGui.QWidget()
                widgetLayout = QtGui.QHBoxLayout()
                widgetLayout.addWidget(envDialogItem)
                widget.setLayout(widgetLayout)
                widgetLayout.addStretch()
                itemN.setSizeHint(widget.sizeHint())
            if present:
                envDialogItem.label_status.mouseReleaseEvent = lambda event, arg=path :self.openLocation(arg)
            else:
                alarm = True
                envDialogItem.label_status.setStyleSheet("""
                QLabel{
                background-color: rgb(200, 0, 0);
                }
                
                QLabel:hover{
                background-color: None;
                }
                
                QLabel:pressed{
                background-color: None;
                }
                """)

            self.envDialog.listWidget.addItem(itemN)
            self.envDialog.listWidget.setItemWidget(itemN, widget)
            x = x + 1

        ## Workgroups ##
        x = 0
        for i in self.workgroups_xml:
            present = False
            xx = 0
            for ii in self.workgroups:
                if self.workgroups_path_xml[x] in self.workgroups_path[xx] and os.path.exists(self.workgroups_path_xml[x]):
                    present = True
                xx = xx + 1

                envDialogItem = loadUi("UI" + os.sep + "ns_EnvCheck_Item.ui")
                envDialogItem.label_name.setText(i)
                path = self.workgroups_path_xml[x]
                envDialogItem.label_path.setText(path)
                itemN = QtGui.QListWidgetItem()
                widget = QtGui.QWidget()
                widgetLayout = QtGui.QHBoxLayout()
                widgetLayout.addWidget(envDialogItem)
                widget.setLayout(widgetLayout)
                widgetLayout.addStretch()
                itemN.setSizeHint(widget.sizeHint())

            if present:
                envDialogItem.label_status.mouseReleaseEvent = lambda event, arg=path :self.openLocation(arg)
            else:
                alarm = True
                envDialogItem.label_status.setStyleSheet("""
                    QLabel{
                    background-color: rgb(50, 50, 50);
                    border-radius: 5px;
                    border: 1px solid rgb(40, 40, 40);
                    }
                    
                    QLabel:hover{
                    background-color: rgb(200, 0, 0);
                    }
                    
                    QPushButton:pressed{
                    background-color: rgb(200, 0, 0);
                    }
                    """)

            self.envDialog.listWidget.addItem(itemN)
            self.envDialog.listWidget.setItemWidget(itemN, widget)
            x = x + 1

        if alarm:
            button.setStyleSheet("""
                QPushButton{
                color: rgb(255 ,0 ,0);
                background-color: rgb(50, 50, 50);
                border-radius: 5px;
                border: 1px solid rgb(40, 40, 40);
                }
        
                QPushButton:hover {
                background-color: rgb(255, 0, 0);
                }
        
                QPushButton:pressed {
                background-color: rgb(255, 0, 0);
                }
                        """)
            button.effect = QGraphicsColorizeEffect(button)
            button.setGraphicsEffect(button.effect)
            button.anim = QtCore.QPropertyAnimation(button.effect, "color", button)
            button.anim.setStartValue(QtGui.QColor(0, 0, 0))
            button.anim.setEndValue(QtGui.QColor(0, 0, 0))
            button.anim.setKeyValueAt(0.5, QtGui.QColor(150, 0, 0))
            button.anim.setDuration(250)
            button.anim.setLoopCount(-1)
            button.effect.setStrength(1)
            button.anim.start()
        else:
            try:
                button.anim.stop()
                button.effect.setStrength(0)
                button.setStyleSheet("""
                QPushButton{
                    color:  rgb(155, 155, 155);
                    background-color: rgb(50, 50, 50);
                    border-radius: 5px;
                    border: 1px solid rgb(40, 40, 40);
                }

                QPushButton:hover {
                    background-color: rgb(80, 80, 80);
                    color: rgb(0, 255, 0);
                    border-style: inset;
                }

                QPushButton:pressed {
                    background-color: rgb(50, 50, 50);
                    color: rgb(0, 255 ,0);
                    border-style: inset;
                }
                """)
            except:
                button.setStyleSheet("""
                QPushButton{
                color: rgb(0 ,255 ,0);
                background-color: rgb(0, 100, 0);
                border-radius: 5px;
                border: 1px solid rgb(40, 40, 40);
                }
    
                QPushButton:hover {
                    background-color: rgb(80, 80, 80);
                    color: rgb(0, 255, 0);
                    border-style: inset;
                }

                QPushButton:pressed {
                    background-color: rgb(50, 50, 50);
                    color: rgb(0, 255, 0);
                    border-style: inset;
                }
                """)

        self.checkStartupVersion(False)

    
    def openLocation(self, path):
        try:
            if sys.platform == "darwin":  ## macOS ##
                subprocess.Popen(["open", "--", path.replace("/", os.sep)])
            if sys.platform == "linux2":  ## Linux ##
                subprocess.Popen(["xdg-open", "--", path.replace("/", os.sep)])
            if sys.platform == "win32":  ## Windows ##
                subprocess.Popen(["explorer", path.replace("/", os.sep)])
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


    def openManagePackagesPanel(self):
        self.managePackages.show()
        self.updateManagePackagePanel()

        
    def global_moveTo_tmp(self, package_path):
        src = package_path
        src_parts = package_path.split(os.sep)

        dst = globalPresetPath + os.sep + "Packages" + os.sep + "_tmp" + os.sep + src_parts[-1]
        
        if not os.path.isdir(dst):
            os.makedirs(dst)
        
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                except Exception as e:
                    os.unlink(d)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
        shutil.rmtree(src)
        
        self.updateManagePackagePanel()


    def local_moveTo_tmp(self, package_path):
        src = package_path
        src_parts = package_path.split(os.sep)

        dst = localPackagePath + os.sep + "_tmp" + os.sep + src_parts[-1]
        
        if not os.path.isdir(dst):
            os.makedirs(dst)
        
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                except Exception as e:
                    os.unlink(d)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
        shutil.rmtree(src)
        
        self.updateManagePackagePanel()


    def global_delete(self, package_path):
        src = package_path

        shutil.rmtree(src)
        
        self.updateManagePackagePanel()


    def local_delete(self, package_path):
        src = package_path

        shutil.rmtree(src)

        self.updateManagePackagePanel()


    def global_restore(self, package_path):
        src = package_path
        src_parts = package_path.split(os.sep)

        dst = globalPresetPath + os.sep + "Packages" + os.sep + src_parts[-1]
        
        if not os.path.isdir(dst):
            os.makedirs(dst)
        
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                except Exception as e:
                    os.unlink(d)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
        shutil.rmtree(src)
        
        self.updateManagePackagePanel()


    def local_restore(self, package_path):
        src = package_path
        src_parts = package_path.split(os.sep)

        dst = localPackagePath + os.sep + src_parts[-1]
        
        if not os.path.isdir(dst):
            os.makedirs(dst)
        
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                except Exception as e:
                    os.unlink(d)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
        shutil.rmtree(src)
        
        self.updateManagePackagePanel()


    def updateManagePackagePanel(self):
        ## CLEAR ##
        self.managePackages.listWidget_packages.clear()
        self.managePackages.textEdit_json.clear()
        self.managePackages.comboBox_json_files.clear()
        self.managePackages.listWidget_packages.setRowCount(0)

        
        ## GLOBAL ##
        foundedFiles = [d for d in os.listdir(globalPresetPath + os.sep + "Packages") if os.path.isdir(os.path.join(globalPresetPath + os.sep + "Packages", d))]
        for i in range(len(foundedFiles)):
            if foundedFiles[i] not in ["_tmp"]:
                self.managePackages.listWidget_packages.insertRow(i)
                packageItem = QTableWidgetItem(foundedFiles[i])
                packageItem.setIcon(QtGui.QIcon(QtGui.QPixmap(globalPresetPath + os.sep + "Packages" + os.sep + foundedFiles[i] + os.sep + "icon.png")))
                self.managePackages.listWidget_packages.setItem(i, 0, packageItem)
                self.managePackages.listWidget_packages.setItem(i, 1, QTableWidgetItem("global"))
                self.managePackages.listWidget_packages.setItem(i, 5, QTableWidgetItem(globalPresetPath + os.sep + "Packages" + os.sep + foundedFiles[i]))
                
                ## BUTTON _TMP ##
                button_tmp_g = QPushButton("to _tmp")
                button_tmp_g.setFixedWidth(100)
                button_tmp_g.setStyleSheet("""
                QPushButton{
                    color:  rgb(155, 155, 155);
                    background-color: rgb(50, 50, 50);
                    border-radius: 5px;
                    border: 1px solid rgb(40, 40, 40);
                }

                QPushButton:hover {
                    background-color: rgb(80, 80, 80);
                    color: rgb(0,230,0);
                    border-style: inset;
                }

                QPushButton:pressed {
                    background-color: rgb(0, 150, 0);
                    color: rgb(0, 230, 0);
                    border-style: inset;
                }
                """)
                button_tmp_g_cellWidget = QWidget()
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                layout.addWidget(button_tmp_g)
                layout.setAlignment(QtCore.Qt.AlignCenter)
                button_tmp_g_cellWidget.setLayout(layout)
                
                button_tmp_g.clicked.connect(partial(self.global_moveTo_tmp, globalPresetPath + os.sep + "Packages" + os.sep + foundedFiles[i]))

                self.managePackages.listWidget_packages.setCellWidget(i, 2, button_tmp_g_cellWidget)


                ## BUTTON DEL ##
                button_del_g = QPushButton("delete")
                button_del_g.setStyleSheet("""
                QPushButton{
                    color:  rgb(155, 155, 155);
                    background-color: rgb(50, 50, 50);
                    border-radius: 5px;
                    border: 1px solid rgb(40, 40, 40);
                }

                QPushButton:hover {
                    background-color: rgb(80, 80, 80);
                    color: rgb(200, 0, 0);
                    border-style: inset;
                }

                QPushButton:pressed {
                    background-color: rgb(150, 0, 0);
                    color: rgb(230, 0, 0);
                    border-style: inset;
                }
                """)
                button_del_g.setFixedWidth(100)
                button_del_g_cellWidget = QWidget()
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                layout.addWidget(button_del_g)
                layout.setAlignment(QtCore.Qt.AlignCenter)
                button_del_g_cellWidget.setLayout(layout)
                
                button_del_g.clicked.connect(partial(self.global_delete, globalPresetPath + os.sep + "Packages" + os.sep + foundedFiles[i]))

                self.managePackages.listWidget_packages.setCellWidget(i, 3, button_del_g_cellWidget)

        
        ## LOCAL ##
        foundedFiles = [d for d in os.listdir(localPackagePath) if os.path.isdir(os.path.join(localPackagePath, d))]
        for i in range(len(foundedFiles)):
            if foundedFiles[i] not in ["_tmp"]:
                self.managePackages.listWidget_packages.insertRow(i)
                packageItem = QTableWidgetItem(foundedFiles[i])
                packageItem.setIcon(QtGui.QIcon(QtGui.QPixmap(localPackagePath + os.sep + foundedFiles[i] + os.sep + "icon.png")))
                self.managePackages.listWidget_packages.setItem(i, 0, packageItem)
                self.managePackages.listWidget_packages.setItem(i, 1, QTableWidgetItem("local"))
                self.managePackages.listWidget_packages.setItem(i, 5, QTableWidgetItem(localPackagePath + os.sep + foundedFiles[i]))
                
                ## BUTTON _TMP ##
                button_tmp = QPushButton("to _tmp")
                button_tmp.setFixedWidth(100)
                button_tmp.setStyleSheet("""
                QPushButton{
                    color:  rgb(155, 155, 155);
                    background-color: rgb(50, 50, 50);
                    border-radius: 5px;
                    border: 1px solid rgb(40, 40, 40);
                }

                QPushButton:hover {
                    background-color: rgb(80, 80, 80);
                    color: rgb(0,230,0);
                    border-style: inset;
                }

                QPushButton:pressed {
                    background-color: rgb(0, 150, 0);
                    color: rgb(0, 230, 0);
                    border-style: inset;
                }
                """)
                button_tmp_cellWidget = QWidget()
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                layout.addWidget(button_tmp)
                layout.setAlignment(QtCore.Qt.AlignCenter)
                button_tmp_cellWidget.setLayout(layout)
                
                button_tmp.clicked.connect(partial(self.local_moveTo_tmp, localPackagePath + os.sep + foundedFiles[i]))

                self.managePackages.listWidget_packages.setCellWidget(i, 2, button_tmp_cellWidget)


                ## BUTTON DEL ##
                button_del = QPushButton("delete")
                button_del.setStyleSheet("""
                QPushButton{
                    color:  rgb(155, 155, 155);
                    background-color: rgb(50, 50, 50);
                    border-radius: 5px;
                    border: 1px solid rgb(40, 40, 40);
                }

                QPushButton:hover {
                    background-color: rgb(80, 80, 80);
                    color: rgb(200, 0, 0);
                    border-style: inset;
                }

                QPushButton:pressed {
                    background-color: rgb(150, 0, 0);
                    color: rgb(230, 0, 0);
                    border-style: inset;
                }
                """)
                button_del.setFixedWidth(100)
                button_del_cellWidget = QWidget()
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                layout.addWidget(button_del)
                layout.setAlignment(QtCore.Qt.AlignCenter)
                button_del_cellWidget.setLayout(layout)
                
                button_del.clicked.connect(partial(self.local_delete, localPackagePath + os.sep + foundedFiles[i]))

                self.managePackages.listWidget_packages.setCellWidget(i, 3, button_del_cellWidget)
        
        ## GLOBAL _TMP ##     
        foundedFiles = [d for d in os.listdir(globalPresetPath + os.sep + "Packages" + os.sep + "_tmp") if os.path.isdir(os.path.join(globalPresetPath + os.sep + "Packages" + os.sep + "_tmp", d))]
        for i in range(len(foundedFiles)):
            self.managePackages.listWidget_packages.insertRow(i)
            packageItem = QTableWidgetItem(foundedFiles[i])
            packageItem.setIcon(QtGui.QIcon(QtGui.QPixmap(globalPresetPath + os.sep + "Packages" + os.sep + "_tmp" + os.sep + foundedFiles[i] + os.sep + "icon.png")))
            self.managePackages.listWidget_packages.setItem(i, 0, packageItem)
            self.managePackages.listWidget_packages.setItem(i, 1, QTableWidgetItem("global"))
            self.managePackages.listWidget_packages.setItem(i, 5, QTableWidgetItem(globalPresetPath + os.sep + "Packages" + os.sep + "_tmp" + os.sep + foundedFiles[i]))
            
            #  ## BUTTON RESTORE ##
            button_restore_g = QPushButton("restore")
            button_restore_g.setFixedWidth(100)
            button_restore_g.setStyleSheet("""
            QPushButton{
                color:  rgb(155, 155, 155);
                background-color: rgb(50, 50, 50);
                border-radius: 5px;
                border: 1px solid rgb(40, 40, 40);
            }

            QPushButton:hover {
                background-color: rgb(80, 80, 80);
                color: rgb(0,230,0);
                border-style: inset;
            }

            QPushButton:pressed {
                background-color: rgb(0, 150, 0);
                color: rgb(0, 230, 0);
                border-style: inset;
            }
            """)
            button_restore_g_cellWidget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(button_restore_g)
            layout.setAlignment(QtCore.Qt.AlignCenter)
            button_restore_g_cellWidget.setLayout(layout)

            button_restore_g.clicked.connect(partial(self.global_restore, globalPresetPath + os.sep + "Packages" + os.sep + "_tmp" + os.sep + foundedFiles[i]))

            self.managePackages.listWidget_packages.setCellWidget(i, 4, button_restore_g_cellWidget)
   
        ## LOCAL _TMP ##
        foundedFiles = [d for d in os.listdir(localPackagePath + os.sep + "_tmp") if os.path.isdir(os.path.join(localPackagePath + os.sep + "_tmp", d))]
        for i in range(len(foundedFiles)):
            self.managePackages.listWidget_packages.insertRow(i)
            packageItem = QTableWidgetItem(foundedFiles[i])
            packageItem.setIcon(QtGui.QIcon(QtGui.QPixmap(localPackagePath + os.sep + "_tmp" + os.sep + foundedFiles[i] + os.sep + "icon.png")))
            self.managePackages.listWidget_packages.setItem(i, 0, packageItem)
            self.managePackages.listWidget_packages.setItem(i, 1, QTableWidgetItem("local"))
            self.managePackages.listWidget_packages.setItem(i, 5, QTableWidgetItem(localPackagePath + os.sep + "_tmp" + os.sep + foundedFiles[i]))
            
            #  ## BUTTON RESTORE ##
            button_restore = QPushButton("restore")
            button_restore.setFixedWidth(100)
            button_restore.setStyleSheet("""
            QPushButton{
                color:  rgb(155, 155, 155);
                background-color: rgb(50, 50, 50);
                border-radius: 5px;
                border: 1px solid rgb(40, 40, 40);
            }

            QPushButton:hover {
                background-color: rgb(80, 80, 80);
                color: rgb(0,230,0);
                border-style: inset;
            }

            QPushButton:pressed {
                background-color: rgb(0, 150, 0);
                color: rgb(0, 230, 0);
                border-style: inset;
            }
            """)
            button_restore_cellWidget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(button_restore)
            layout.setAlignment(QtCore.Qt.AlignCenter)
            button_restore_cellWidget.setLayout(layout)
            
            button_restore.clicked.connect(partial(self.local_restore, localPackagePath + os.sep + "_tmp" + os.sep + foundedFiles[i]))

            self.managePackages.listWidget_packages.setCellWidget(i, 4, button_restore_cellWidget)
   


        self.managePackages.listWidget_packages.setColumnWidth(0, 300)
        self.managePackages.listWidget_packages.setColumnWidth(1, 50)


        ## SIGNALS LISTWIDGET ##
        self.connect(self.managePackages.listWidget_packages, QtCore.SIGNAL("cellClicked(int, int)"), self.managePackages_listwidget_cellClicked)
        self.managePackages.listWidget_packages.selectRow(0)
        self.managePackages_listwidget_cellClicked(0, 0)

    
    def managePackages_listwidget_cellClicked(self, row, col):
        currentItem = self.managePackages.listWidget_packages.item(row, 5)
        packagePath = str(currentItem.text())
        foundedFiles = [d for d in os.listdir(packagePath) if os.path.isfile(os.path.join(packagePath, d))]
        
        self.managePackages.comboBox_json_files.clear()
        
        for i in foundedFiles:
            if i.find(".json") != -1:
                self.managePackages.comboBox_json_files.addItem(i)

    
    def loadJSONFile_PackageManager(self, index):
        self.managePackages.textEdit_json.clear()
        currentItem = self.managePackages.listWidget_packages.item(self.managePackages.listWidget_packages.currentRow(), 5)

        try:
            jsonPath = str(currentItem.text()) + "/" + str(self.managePackages.comboBox_json_files.currentText())
            f = open(jsonPath, "r")
            self.managePackages.textEdit_json.setText(f.read())
            f.close()
        except:
            pass


    def openEnvPanel(self):
        button = self.gui.pushButton_check
        indexedPreset = self.gui.comboBox_preset.currentText()
        self.gui.comboBox_preset.setCurrentIndex(self.gui.comboBox_preset.findText(indexedPreset))

        try:
            button.anim.stop()
            button.effect.setStrength(0)
            button.setStyleSheet("""
            QPushButton{
            color:  rgb(155, 155, 155);
            background-color: rgb(50, 50, 50);
            border-radius: 5px;
            border: 1px solid rgb(40, 40, 40);
            }
    
            QPushButton:hover {
                background-color: rgb(80, 80, 80);
                color: rgb(0,150,0);
                border-style: inset;
            }
    
            QPushButton:pressed {
                background-color:  rgb(0,150,0);
                color: rgb(0, 255, 0);
                border-style: inset;
            }
            """)
        except:
            button.setStyleSheet("""
            QPushButton{
            color:  rgb(155, 155, 155);
            background-color: rgb(50, 50, 50);
            border-radius: 5px;
            border: 1px solid rgb(40, 40, 40);
            }
            
            QPushButton:hover {
                background-color: rgb(80, 80, 80);
                color: rgb(0, 255, 0);
                border-style: inset;
            }
            
            QPushButton:pressed {
                background-color:  rgb(0,150,0);
                color: rgb(0, 255, 0);
                border-style: inset;
            }
                    """)
        pos = self.gui.pos()
        self.envDialog.move(pos.x() - 530, pos.y())
        self.envDialog.show()


    def setRenderServiceLocation(self):
        defaultPath = renderServicePath
        self.gui.lineEdit_renderService.setText(QFileDialog.getExistingDirectory(None, str("set Path"), defaultPath))
 

    def setGlobalPresetLocation(self):
        defaultPath = searchPathWorkgroups
        self.gui.lineEdit_globalPresetLocation.setText(QFileDialog.getExistingDirectory(None, str("set Path"), defaultPath))
        self.update()


    def closeEvent(self, event):
        event.ignore()
        self.gui.tabWidget.setCurrentIndex(0)
        self.gui.hide()


    def hideEvent(self, event):
        self.gui.closeEvent(event)


    def loadConfigSettings(self):
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
                globalPresetPath = root.find("Global_Preset_Location")
                renderService = root.find("Render_Service")
                chat_host = root.find("Chat_Host")
                chat_alias = root.find("Chat_Alias")
                chat_notify = root.find("Chat_Notify")
                chat_notify_sound = root.find("Chat_Notify_Sound")
                local_rs_lic = root.find("Use_Local_RS_License")
                use_houdini_packages = root.find("Use_Houdini_Packages_Mode")
                use_global_preset_for_packages = root.find("Use_Global_Preset_Location_For_Packages")
                delete_bat = root.find("Delete_Exec_Bat")

                self.gui.lineEdit_arnoldLic.setText(arnoldLic.text)
                self.gui.lineEdit_chat_host.setText(chat_host.get("Host"))
                self.gui.lineEdit_alias.setText(chat_alias.get("Name"))
                self.gui.lineEdit_WOL_MAC_0.setText(wol0.get("Address"))
                self.gui.lineEdit_WOL_Des_0.setText(wol0.get("Description"))
                if wol0.get("StartUp") ==  "True":
                    ns_Utility.wake_on_lan(str(wol0.get("Address")))
                    self.gui.checkBox_startUp_0.setChecked(True)
                self.gui.lineEdit_WOL_MAC_1.setText(wol1.get("Address"))
                self.gui.lineEdit_WOL_Des_1.setText(wol1.get("Description"))
                if wol1.get("StartUp") == "True":
                    ns_Utility.wake_on_lan(str(wol1.get("Address")))
                    self.gui.checkBox_startUp_1.setChecked(True)
                self.gui.lineEdit_WOL_MAC_2.setText(wol2.get("Address"))
                self.gui.lineEdit_WOL_Des_2.setText(wol2.get("Description"))
                if wol2.get("StartUp") == "True":
                    ns_Utility.wake_on_lan(str(wol2.get("Address")))
                    self.gui.checkBox_startUp_3.setChecked(True)
                self.gui.lineEdit_WOL_MAC_3.setText(wol3.get("Address"))
                self.gui.lineEdit_WOL_Des_3.setText(wol3.get("Description"))
                if wol3.get("StartUp") == "True":
                    ns_Utility.wake_on_lan(str(wol3.get("Address")))
                    self.gui.checkBox_startUp_3.setChecked(True)

                try:
                    self.gui.lineEdit_globalPresetLocation.setText(globalPresetPath.get("Path"))
                    self.gui.lineEdit_renderService.setText(renderService.get("Path"))
                except:
                    self.gui.lineEdit_renderService.setText(renderServicePath)

                if chat_notify.get("Value") == "True":
                    self.gui.checkBox_chat_notifications.setChecked(True)
                if chat_notify_sound.get("Value") == "True":
                    self.gui.checkBox_chat_notifications_sound.setChecked(True)
                if local_rs_lic.get("Value") == "True":
                    self.gui.checkBox_local_rs_lic.setChecked(True)
                if use_houdini_packages.get("Value") == "True":
                    self.gui.checkBox_hou_packages.setChecked(True)
                if use_global_preset_for_packages.get("Value") == "True":
                    self.gui.checkBox_hou_packages_global.setChecked(True)
                if delete_bat.get("Value") == "True":
                    self.gui.checkBox_deleteBat.setChecked(True)

                os.environ["solidangle_LICENSE"] = str(self.gui.lineEdit_arnoldLic.text())

                ## Debug Log ##
                prev_text = self.gui.textEdit_debug_log.toPlainText()
                prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> load Config.xml"
                self.gui.textEdit_debug_log.setText(prev_text)
                ## Debug Log - End ##
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


    def getPresetLogo(self, event):
        try:
            logoFile = QFileDialog.getOpenFileName(None, str("Logo location"), scriptRoot, "Image files (*.jpg *.png)")
            picPixmap = QtGui.QPixmap(logoFile)
            picPixmapSize = picPixmap.size()
            factor = float(picPixmapSize.width())/float(picPixmapSize.height())
            picPixmap = picPixmap.scaledToWidth(50, mode = Qt.SmoothTransformation)
            picPixmap = picPixmap.scaledToHeight(50/factor, mode = Qt.SmoothTransformation)
            self.presetSaveDialog.label_presetLogo.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
            self.presetSaveDialog.label_presetLogo.setPixmap(picPixmap);
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


    def loadPresetsToCombo(self, presetName):
        self.disconnect(self.gui.comboBox_preset, QtCore.SIGNAL('currentIndexChanged(int)'), self.setPresetValues)
        self.disconnect(self.gui.comboBox_preset, QtCore.SIGNAL('activated(int)'), self.setPresetValues)
        
        self.gui.comboBox_preset.clear()
        preset_counter = 0
        try:
            preset = None
            presets_global = None
            presetIcon = None
            
            if os.path.exists(presetPath):
                presets = os.listdir(presetPath)
            
            presetPathGlobal = self.gui.lineEdit_globalPresetLocation.text()
            
            if os.path.exists(presetPathGlobal):
                presets_global = os.listdir(self.gui.lineEdit_globalPresetLocation.text())

            presetIcon = QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "noicon.png"))

            

            if presets:
                for i in presets:
                    if i.find(".xml") != -1:
                        if os.path.exists(presetPath + os.sep + i.replace("xml", "jpg")):
                            presetIcon = QtGui.QIcon(QtGui.QPixmap(presetPath + os.sep + i.replace("xml", "jpg")))
                        elif os.path.exists(presetPath + os.sep + i.replace("xml", "png")):
                            presetIcon = QtGui.QIcon(QtGui.QPixmap(presetPath + os.sep + i.replace("xml", "png")))
                            
                        self.gui.comboBox_preset.addItem(presetIcon, i.replace(".xml", ""))
                        preset_counter += 1
            if presets_global:
                for i in presets_global:
                    if i.find(".xml") != -1:
                        if os.path.exists(presetPathGlobal + os.sep + i.replace("xml", "jpg")):
                            presetIcon = QtGui.QIcon(QtGui.QPixmap(self.gui.lineEdit_globalPresetLocation.text() + os.sep + i.replace("xml", "jpg")))
                        elif os.path.exists(presetPathGlobal + os.sep + i.replace("xml", "png")):
                            presetIcon = QtGui.QIcon(QtGui.QPixmap(self.gui.lineEdit_globalPresetLocation.text() + os.sep + i.replace("xml", "png")))
                        self.gui.comboBox_preset.addItem(presetIcon, i.replace(".xml", ""))
                        preset_counter += 1


        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        self.connect(self.gui.comboBox_preset, QtCore.SIGNAL('activated(int)'), self.setPresetValues)      
        self.connect(self.gui.comboBox_preset, QtCore.SIGNAL('currentIndexChanged(int)'), self.setPresetValues)
        
        try:
            if presetName != "":
                self.gui.comboBox_preset.setCurrentIndex(self.gui.comboBox_preset.findText(presetName)) ## Preset Item ##
            else:
                self.gui.comboBox_preset.setCurrentIndex(preset_counter - 1) ## Last Item ##
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


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

            ET.SubElement(app, "Application", name="Houdini", version=str(self.gui.comboBox_HOUVersion.currentText()))

            for i in range(0, len(self.selectedRenderer)):
                ET.SubElement(renderer, "Renderer",  name=self.selectedRenderer[i][0], version=self.selectedRenderer[i][1], plugin=self.selectedRenderer[i][2], path=self.selectedRenderer[i][3])

            for i in range(0, len(self.selectedWorkgroups)):
                ET.SubElement(workgroup, "Workgroup", name=self.selectedWorkgroups[i][0], path=self.selectedWorkgroups[i][1])

            ET.SubElement(addParas, "AdditionalParameters", value=str(self.gui.textEdit_addParameters.toPlainText()).replace("\n", "[/n]"))
            ET.SubElement(exeVersion, "exeVersion", value=str(self.gui.comboBox_exeVersion.currentText()))

            xmlBeauty = xml.dom.minidom.parseString(ET.tostring(root, encoding='utf8', method='xml'))
            xmlFile = open(presetPath + os.sep + str(self.presetSaveDialog.lineEdit_presetName.text()) + ".xml", "w")
            xmlFile.write(xmlBeauty.toprettyxml())
            xmlFile.close()

            pic = self.presetSaveDialog.label_presetLogo.pixmap()
            pic.save(presetPath + os.sep + str(self.presetSaveDialog.lineEdit_presetName.text()) + ".png", "png")

            ## Debug Log ##
            prev_text = self.gui.textEdit_debug_log.toPlainText()
            prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> create preset: " + str(self.presetSaveDialog.lineEdit_presetName.text())
            self.gui.textEdit_debug_log.setText(prev_text)
            ## Debug Log - End ##

            self.loadPresetsToCombo(self.presetSaveDialog.lineEdit_presetName.text())
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        presetName = self.presetSaveDialog.lineEdit_presetName.text()
        self.presetSaveDialog.close()
        self.loadPresetsToCombo(presetName)

        if self.presetFlag:
            self.saveDefaultPreset()
            self.presetFlag = False


    def overwritePresetNameAndSave(self):
        presetName = str(self.gui.comboBox_preset.currentText())
        globalPresetPath = str(self.gui.lineEdit_globalPresetLocation.text())

        try:
            root = ET.Element(presetName)
            app = ET.SubElement(root, "Application")
            renderer = ET.SubElement(root, "Renderer")
            workgroup = ET.SubElement(root, "Workgroup")
            addParas = ET.SubElement(root, "AdditionalParameters")
            exeVersion = ET.SubElement(root, "exeVersion")

            ET.SubElement(app, "Application", name="Houdini", version=str(self.gui.comboBox_HOUVersion.currentText()))

            for i in range(0, len(self.selectedRenderer)):
                ET.SubElement(renderer, "Renderer", name=self.selectedRenderer[i][0],
                              version=self.selectedRenderer[i][1], plugin=self.selectedRenderer[i][2],
                              path=self.selectedRenderer[i][3])

            for i in range(0, len(self.selectedWorkgroups)):
                ET.SubElement(workgroup, "Workgroup", name=self.selectedWorkgroups[i][0],
                              path=self.selectedWorkgroups[i][1])

            ET.SubElement(addParas, "AdditionalParameters",
                          value=str(self.gui.textEdit_addParameters.toPlainText().replace("\n", "[/n]")))
            ET.SubElement(exeVersion, "exeVersion", value=str(self.gui.comboBox_exeVersion.currentText()))

            xmlBeauty = xml.dom.minidom.parseString(ET.tostring(root, encoding='utf8', method='xml'))
            if presetName[0] == "_":
                xmlFile = open(globalPresetPath + os.sep + presetName + ".xml", "w")
            else:
                xmlFile = open(presetPath + os.sep + presetName + ".xml", "w")
            xmlFile.write(xmlBeauty.toprettyxml())
            xmlFile.close()

            ## Debug Log ##
            prev_text = self.gui.textEdit_debug_log.toPlainText()
            prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> overwrite preset: " + presetName
            self.gui.textEdit_debug_log.setText(prev_text)
            ## Debug Log - End ##
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


    def deleteCurrentPreset(self):
        presetName = str(self.gui.comboBox_preset.currentText())
        globalPresetPath = str(self.gui.lineEdit_globalPresetLocation.text())

        if presetName and globalPresetPath:
            if presetName[0] == "_":
                reply = QtGui.QMessageBox.warning(self, "ns_Startup - Preset", "You want delete a global preset: " + presetName + "?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.Yes:
                    try:
                        if os.path.exists(globalPresetPath + os.sep + presetName + ".xml"):
                            os.remove(globalPresetPath + os.sep + presetName + ".xml")
                        if os.path.exists(globalPresetPath + os.sep + presetName + ".png"):
                            os.remove(globalPresetPath + os.sep + presetName + ".png")
                        if os.path.exists(globalPresetPath + os.sep + presetName + ".jpg"):
                            os.remove(globalPresetPath + os.sep + presetName + ".jpg")

                        ## Debug Log ##
                        prev_text = self.gui.textEdit_debug_log.toPlainText()
                        prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> delete preset: " + presetName
                        self.gui.textEdit_debug_log.setText(prev_text)
                        ## Debug Log - End ##
                    except Exception as e:
                        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            else:
                try:
                    reply = QtGui.QMessageBox.warning(self, "ns_Startup - Preset", "You want delete a local preset: " + presetName + "?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        if os.path.exists(presetPath + os.sep + presetName + ".xml"):
                            os.remove(presetPath + os.sep + presetName + ".xml")
                        if os.path.exists(presetPath + os.sep + presetName + ".png"):
                            os.remove(presetPath + os.sep + presetName + ".png")
                        if os.path.exists(presetPath + os.sep + presetName + ".jpg"):
                            os.remove(presetPath + os.sep + presetName + ".jpg")

                        ## Debug Log ##
                        prev_text = self.gui.textEdit_debug_log.toPlainText()
                        prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> delete preset: " + presetName
                        self.gui.textEdit_debug_log.setText(prev_text)
                    ## Debug Log - End ##
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

            self.loadPresetsToCombo("")


    def pushCurrentPreset(self):
        presetName = str(self.gui.comboBox_preset.currentText())
        globalPresetPath = str(self.gui.lineEdit_globalPresetLocation.text())

        if presetName:
            if os.path.exists(globalPresetPath):
                if not os.path.exists(globalPresetPath + os.sep + "_" + presetName + ".xml"):
                    if presetName[0] is not "_":
                        if os.path.exists(presetPath + os.sep + presetName + ".png"):
                            shutil.copy2(presetPath + os.sep + presetName + ".png", globalPresetPath + os.sep + "_" + presetName + ".png")
                        if os.path.exists(presetPath + os.sep + presetName + ".jpg"):
                            shutil.copy2(presetPath + os.sep + presetName + ".jpg", globalPresetPath + os.sep + "_" + presetName + ".jpg")

                        xmlFile = open(presetPath + os.sep + presetName + ".xml")
                        xmlFileMod = open(globalPresetPath + os.sep + "_" + presetName + ".xml" ,"wt")

                        for line in xmlFile:
                            xmlFileMod.write(line.replace(presetName, "_" + presetName))

                        xmlFile.close()
                        xmlFileMod.close()
                    else:
                        reply = QtGui.QMessageBox.warning(self, "ns_Startup - Preset", presetName + " is allready pushed.", QtGui.QMessageBox.Ok)
                else:
                    reply = QtGui.QMessageBox.warning(self, "ns_Startup - Preset", presetName + " is allready pushed. Overwrite?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        if presetName[0] is not "_":
                            shutil.copy2(presetPath + os.sep + presetName + ".png",
                                         globalPresetPath + os.sep + "_" + presetName + ".png")

                            xmlFile = open(presetPath + os.sep + presetName + ".xml")
                            xmlFileMod = open(globalPresetPath + os.sep + "_" + presetName + ".xml", "wt")

                            for line in xmlFile:
                                xmlFileMod.write(line.replace(presetName, "_" + presetName))

                            xmlFile.close()
                            xmlFileMod.close()

        ## Debug Log ##
        prev_text = self.gui.textEdit_debug_log.toPlainText()
        prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> push preset: " + presetName
        self.gui.textEdit_debug_log.setText(prev_text)
        ## Debug Log - End ##

        self.loadPresetsToCombo("")


    def savePresetButton(self):
        selectedRenderer = []
        selectedWorkgroups = []

        ## Look at Lists & AppVersion ##
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
        currentSelectedPreset = self.gui.comboBox_preset.currentText()

        if currentSelectedPreset != "" or None:
            reply = QtGui.QMessageBox.warning(self, "ns_Startup - Save", "Overwrite current preset?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.overwritePresetNameAndSave()
            else:
                self.presetSaveDialog.lineEdit_presetName.setText("")
                self.presetSaveDialog.label_presetLogo.setPixmap(QtGui.QPixmap(scriptRoot + os.sep + "Icons" + os.sep + "noicon.png"));
                pos = self.gui.pos()
                self.presetSaveDialog.move(pos.x() + 20, pos.y() + 20)
                self.presetSaveDialog.show()
        else:
            self.presetSaveDialog.lineEdit_presetName.setText("")
            self.presetSaveDialog.label_presetLogo.setPixmap(QtGui.QPixmap(scriptRoot + os.sep + "Icons" + os.sep + "noicon.png"));
            self.presetSaveDialog.show()


    def saveDefaultPreset(self):
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

                    ET.SubElement(app, "Application", name="Houdini", version=str(self.gui.comboBox_HOUVersion.currentText()))

                    for i in range(0, len(self.selectedRenderer)):
                        ET.SubElement(renderer, "Renderer", name=self.selectedRenderer[i][0], version=self.selectedRenderer[i][1], plugin=self.selectedRenderer[i][2], path=self.selectedRenderer[i][3])

                    for i in range(0, len(self.selectedWorkgroups)):
                        ET.SubElement(workgroup, "Workgroup", name=self.selectedWorkgroups[i][0], path=self.selectedWorkgroups[i][1])

                    ET.SubElement(addParas, "AdditionalParameters", value=str(self.gui.textEdit_addParameters.toPlainText().replace("\n", "[/n]")))
                    ET.SubElement(exeVersion, "exeVersion", value=str(self.gui.comboBox_exeVersion.currentText()))

                    xmlBeauty = xml.dom.minidom.parseString(ET.tostring(root, encoding='utf8', method='xml'))
                    xmlFile = open(configPath + os.sep + "Default.xml", "w")
                    xmlFile.write(xmlBeauty.toprettyxml())
                    xmlFile.close()
                    ## Debug Log ##
                    prev_text = self.gui.textEdit_debug_log.toPlainText()
                    prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> save Default.xml"
                    self.gui.textEdit_debug_log.setText(prev_text)
                    ## Debug Log - End ##
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        else:
            try:
                if os.path.exists(configPath):
                    pass
                else:
                    os.makedirs(configPath)

                root = ET.Element(str(presetName.replace("..", "")))
                app = ET.SubElement(root, "Application")
                renderer = ET.SubElement(root, "Renderer")
                workgroup = ET.SubElement(root, "Workgroup")
                addParas = ET.SubElement(root, "AdditionalParameters")
                exeVersion = ET.SubElement(root, "exeVersion")

                ET.SubElement(app, "Application", name="Houdini", version=str(self.gui.comboBox_HOUVersion.currentText()))

                for i in range(0, len(self.selectedRenderer)):
                    ET.SubElement(renderer, "Renderer", name=self.selectedRenderer[i][0], version=self.selectedRenderer[i][1], plugin=self.selectedRenderer[i][2], path=self.selectedRenderer[i][3])

                for i in range(0, len(self.selectedWorkgroups)):
                    ET.SubElement(workgroup, "Workgroup", name=self.selectedWorkgroups[i][0], path=self.selectedWorkgroups[i][1])

                ET.SubElement(addParas, "AdditionalParameters", value=str(self.gui.textEdit_addParameters.toPlainText().replace("\n", "[/n]")))
                ET.SubElement(exeVersion, "exeVersion", value=str(self.gui.comboBox_exeVersion.currentText()))

                xmlBeauty = xml.dom.minidom.parseString(ET.tostring(root, encoding='utf8', method='xml'))
                xmlFile = open(configPath + os.sep + "Default.xml", "w")
                xmlFile.write(xmlBeauty.toprettyxml())
                xmlFile.close()
                ## Debug Log ##
                prev_text = self.gui.textEdit_debug_log.toPlainText()
                prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> save Default.xml"
                self.gui.textEdit_debug_log.setText(prev_text)
                ## Debug Log - End ##

                prev_text = self.gui.textEdit_debug_log.toPlainText()
                prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> write Default.xml"
                self.gui.textEdit_debug_log.setText(prev_text)
            except Exception as e:
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


    def setDefaultPresetValues(self):
        for i in range(self.gui.listWidget_workgroup.rowCount()): ## Set all FALSE in Workgroups ##
            workgroup_checkBox = QCheckBox()
            workgroup_checkBox.setChecked(False)
            workgroup_cellWidget = QWidget()
            workgroup_cellWidget.setStyleSheet('''
                                            background-color: rgb(50, 50, 50);
                                            color: rgb(155, 155, 155);
                                            border-radius: 5px;
                                            border: 0px solid rgb(40, 40, 40);
                                                ''')
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(workgroup_checkBox)
            layout.setAlignment(QtCore.Qt.AlignCenter)

            workgroup_cellWidget.setLayout(layout)

            self.gui.listWidget_workgroup.setCellWidget(i, 1, workgroup_cellWidget)
            workgroup_checkBox.stateChanged.connect(partial(self.ns_workgroup_checkBoxChanged, i, workgroup_checkBox, workgroup_cellWidget))

        for i in range(self.gui.listWidget_renderer.rowCount()): ## Set all FALSE in Renderer ##
            renderer_checkBox = QCheckBox()
            renderer_checkBox.setChecked(False)
            renderer_cellWidget = QWidget()

            renderer_cellWidget.setStyleSheet('''
                                            background-color: rgb(50, 50, 50);
                                            color: rgb(155, 155, 155);
                                            border-radius: 5px;
                                            border: 0px solid rgb(40, 40, 40);
                                                ''')

            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(renderer_checkBox)
            layout.setAlignment(QtCore.Qt.AlignCenter)

            renderer_cellWidget.setLayout(layout)

            self.gui.listWidget_renderer.setCellWidget(i, 3, renderer_cellWidget)
            renderer_checkBox.stateChanged.connect(partial(self.ns_renderer_checkBoxChanged, i, renderer_checkBox, renderer_cellWidget))
        
        if os.path.exists(configPath + os.sep + "Default.xml"):
            try:
                root = ET.parse(configPath + os.sep + "Default.xml").getroot()
                ## Debug Log ##
                prev_text = self.gui.textEdit_debug_log.toPlainText()
                prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> load Default.xml"
                self.gui.textEdit_debug_log.setText(prev_text)
                ## Debug Log - End ##
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
                                                                    background-color: rgb(80, 80, 80);
                                                                    color: rgb(155, 155, 155);
                                                                    border-radius: 5px;
                                                                    border: 0px solid rgb(40, 40, 40);
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
                                                                        background-color: rgb(80, 80, 80);
                                                                        color: rgb(155, 155, 155);
                                                                        border-radius: 5px;
                                                                        border: 0px solid rgb(40, 40, 40);
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
                            self.gui.textEdit_addParameters.setText((ii.attrib['value']).replace("[/n]", "\n"))
                    if child.tag == "exeVersion":
                        for ii in child:
                            self.gui.comboBox_exeVersion.setCurrentIndex(self.gui.comboBox_exeVersion.findText(ii.attrib['value'].replace(" ", "\n")))

                self.gui.comboBox_preset.setCurrentIndex(self.gui.comboBox_preset.findText(root.tag))
            except Exception as e:
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        self.selectedPresetCombo = self.gui.comboBox_preset.currentIndex()


    def setPresetValues(self, index):
        self.clearArrays_xml()
        try:
            presetName = str(self.gui.comboBox_preset.itemText(index))
            globalPresetPath = str(self.gui.lineEdit_globalPresetLocation.text())
 
            if len(presetName) > 0:
                if presetName[0] == "_":
                    root = ET.parse(globalPresetPath + os.sep + str(presetName) + ".xml").getroot()
                else:
                    root = ET.parse(presetPath + os.sep + str(presetName) + ".xml").getroot()

                self.gui.textEdit_addParameters.clear()
                for i in range(self.gui.listWidget_workgroup.rowCount()):  ## Set all FALSE in Workgroups ##
                    workgroup_checkBox = QCheckBox()
                    workgroup_checkBox.setChecked(False)
                    workgroup_cellWidget = QWidget()
                    workgroup_cellWidget.setStyleSheet('''
                                                        background-color: rgb(50, 50, 50);
                                                        color: rgb(155, 155, 155);
                                                        border-radius: 5px;
                                                        border: 0px solid rgb(40, 40, 40);
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

                for i in range(self.gui.listWidget_renderer.rowCount()):  ## Set all FALSE in Renderer ##
                    renderer_checkBox = QCheckBox()
                    renderer_checkBox.setChecked(False)
                    renderer_cellWidget = QWidget()
                    renderer_cellWidget.setStyleSheet('''
                                                        background-color: rgb(50, 50, 50);
                                                        color: rgb(155, 155, 155);
                                                        border-radius: 5px;
                                                        border: 0px solid rgb(40, 40, 40);
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
                            index = self.gui.comboBox_HOUVersion.findText(i.attrib['version'])
                            self.gui.comboBox_HOUVersion.setCurrentIndex(index)
                            self.apps_xml.append(i.attrib['version'])
                            self.apps_path_xml.append(searchPathHoudiniWIN + os.sep + i.attrib['version'])
                    if child.tag == "Renderer":
                        for ii in child:
                            self.renderer_xml.append(ii.attrib['name'])
                            self.renderer_path_xml.append(ii.attrib['path'])
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
                                                        background-color: rgb(100, 100, 100);
                                                        color: rgb(155, 155, 155);
                                                        border-radius: 5px;
                                                        border: 0px solid rgb(40, 40, 40);
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
                            self.workgroups_path_xml.append(ii.attrib['path'])
                            self.workgroups_xml.append(ii.attrib['name'])
                            for i in range(self.gui.listWidget_workgroup.rowCount()):
                                if str(self.gui.listWidget_workgroup.item(i, 0).text()) == ii.attrib['name'] and str(self.gui.listWidget_workgroup.item(i, 2).text()) == ii.attrib['path']:
                                    workgroup_checkBox = QCheckBox()
                                    workgroup_checkBox.setChecked(True)
                                    workgroup_cellWidget = QWidget()
                                    workgroup_cellWidget.setStyleSheet('''
                                                        background-color: rgb(100, 100, 100);
                                                        color: rgb(155, 155, 155);
                                                        border-radius: 5px;
                                                        border: 0px solid rgb(40, 40, 40);
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
                            self.gui.textEdit_addParameters.setText((ii.attrib['value']).replace("[/n]", "\n"))

                    self.gui.comboBox_preset.setCurrentIndex(self.gui.comboBox_preset.findText(root.tag))
                    if child.tag == "exeVersion":
                        for ii in child:
                            self.gui.comboBox_exeVersion.setCurrentIndex(self.gui.comboBox_exeVersion.findText(ii.attrib['value'].replace(" ", "\n")))

                ## Debug Log ##
                prev_text = self.gui.textEdit_debug_log.toPlainText()
                prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> load preset values from: " + presetName
                self.gui.textEdit_debug_log.setText(prev_text)
                ## Debug Log - End ##

        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        
        self.checkEnv()
        self.selectedPresetCombo = self.gui.comboBox_preset.currentIndex()


    def openGUI(self):
        self.gui.show()
        self.update()
        self.setDefaultPresetValues()


    def update(self):
        ## Icons ##
        iconRS = QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "rsIcon.png"))
        iconRS_Local = QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "rsIcon_Local.png"))
        iconArnold = QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "arnoldIcon.png"))
        iconVray = QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "vrayIcon.png"))
        iconOctane = QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "octaneIcon.png"))
        iconHou = QtGui.QIcon(QtGui.QPixmap("Icons" + os.sep + "houIcon.png"))

        houTypes_win = ["hindie.exe", "houdini.exe", "houdinifx.exe", "houdinicore.exe", "happrentice.exe"]
        houTypes_lin = []

        self.clearArrays()
        self.envDialog.listWidget.clear()
        self.gui.comboBox_HOUVersion.clear()
        self.gui.comboBox_exeVersion.clear()
        self.gui.listWidget_renderer.setRowCount(0)
        self.gui.listWidget_workgroup.setRowCount(0)
        
        #################################################################################################################
        ## Get Houdini Versions #########################################################################################
        houdiniVersions = []
        houdiniEntryPathes = []

        if sys.platform == "darwin": ## macOS ##
                pass
                #TODO macOS version
        if sys.platform == "linux2": ## Linux ##
                pass
                #TODO linux version
        if sys.platform == "win32": ## Windows ##
            foundedFiles = [d for d in os.listdir(searchPathHoudiniWIN) if os.path.isdir(os.path.join(searchPathHoudiniWIN, d))]

            for i in foundedFiles:
                if i.find("Houdini") != -1:
                    houdiniVersions.append(i)
                    self.apps.append(i)
                    houdiniEntryPathes.append(searchPathHoudiniWIN + os.sep + i)
                    self.apps_path.append(searchPathHoudiniWIN + os.sep + i)
                    self.gui.comboBox_HOUVersion.addItem(iconHou, i)

            for i in houTypes_win:
                self.gui.comboBox_exeVersion.addItem(iconHou, i)
        
        ############################################################################################################
        ## Get Octane ##############################################################################################
        try:
            octaneVersions = []
            octaneBridgeVersions = []
            octaneEntryPathes = []

            if sys.platform == "darwin":  ## macOS ##
                pass
            if sys.platform == "linux2":  ## Linux ##
                pass
            if sys.platform == "win32":  ## Windows ##
                foundedFiles = [d for d in os.listdir(searchPathOctane) if os.path.isdir(os.path.join(searchPathOctane, d))]
                for i in foundedFiles:
                    if i.find("Octane") != -1:
                        parts = i.split("_")

                        octaneBridgeVersions.append(parts[-1])
                        octaneVersions.append(parts[1])
                        octaneEntryPathes.append(searchPathOctane + os.sep + i)
                        self.renderer.append("Octane")
                        self.renderer_path.append(searchPathOctane + os.sep + i)

            for i in range(len(octaneVersions)):
                self.gui.listWidget_renderer.insertRow(i)

                octaneItem = QTableWidgetItem("Octane")
                octaneItem.setIcon(iconOctane)

                self.gui.listWidget_renderer.setItem(i, 0, octaneItem)
                self.gui.listWidget_renderer.setItem(i, 1, QTableWidgetItem(octaneVersions[i]))
                self.gui.listWidget_renderer.setItem(i, 2, QTableWidgetItem(octaneBridgeVersions[i]))
                self.gui.listWidget_renderer.setItem(i, 4, QTableWidgetItem(octaneEntryPathes[i]))

                if os.path.exists(octaneEntryPathes[i] + os.sep + "_install.txt"):
                    button_install = QPushButton("[ install dependencies ]")
                    button_install.setFixedWidth(400)
                    button_install.setStyleSheet("""
                    QPushButton{
                        color:  rgb(155, 155, 155);
                        background-color: rgb(50, 50, 50);
                        border-radius: 5px;
                        border: 1px solid rgb(40, 40, 40);
                    }

                    QPushButton:hover {
                        background-color: rgb(80, 80, 80);
                        color: rgb(0,230,0);
                        border-style: inset;
                    }

                    QPushButton:pressed {
                        background-color: rgb(0, 150, 0);
                        color: rgb(0, 230, 0);
                        border-style: inset;
                    }
                    """)
                    button_install_cellWidget = QWidget()
                    layout = QHBoxLayout()
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setSpacing(0)
                    layout.addWidget(button_install)
                    layout.setAlignment(QtCore.Qt.AlignCenter)
                    button_install_cellWidget.setLayout(layout)
                    
                    lines = []
                    with open(octaneEntryPathes[i] + os.sep + "_install.txt") as f:
                        lines = f.readlines()

                    button_install.clicked.connect(partial(self.openLocation, lines))
                    self.gui.listWidget_renderer.setCellWidget(i, 5, button_install_cellWidget)

                ## Checkboxes ##
                renderer_checkBox = QCheckBox()
                renderer_checkBox.setChecked(False)
                renderer_cellWidget = QWidget()

                if renderer_checkBox.checkState() == QtCore.Qt.Checked:
                    renderer_cellWidget.setStyleSheet('''
                                                    background-color: rgb(100, 100, 100);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);
                                                        ''')
                else:
                    renderer_cellWidget.setStyleSheet('''
                                                    background-color: rgb(50, 50, 50);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);
                                                        ''')
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                layout.addWidget(renderer_checkBox)
                layout.setAlignment(QtCore.Qt.AlignCenter)

                renderer_cellWidget.setLayout(layout)

                renderer_checkBox.stateChanged.connect(partial(self.ns_renderer_checkBoxChanged, i, renderer_checkBox, renderer_cellWidget))
                self.gui.listWidget_renderer.setCellWidget(i, 3, renderer_cellWidget)
                self.gui.listWidget_renderer.setColumnWidth(3, 60)
                self.gui.listWidget_renderer.setColumnWidth(4, 500)
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        ###########################################################################################################
        ## Get V-Ray ##############################################################################################
        try:
            vrayVersions = []
            vrayBridgeVersions = []
            vrayEntryPathes = []

            if sys.platform == "darwin":  ## macOS ##
                pass
            if sys.platform == "linux2":  ## Linux ##
                pass
            if sys.platform == "win32":  ## Windows ##
                foundedFiles = [d for d in os.listdir(searchPathVray) if os.path.isdir(os.path.join(searchPathVray, d))]
                for i in foundedFiles:
                    if i.find("vray") != -1:
                        parts = i.split("_")

                        vrayBridgeVersions.append(parts[-1])
                        vrayVersions.append(parts[2])
                        vrayEntryPathes.append(searchPathVray + os.sep + i)
                        self.renderer.append("V-Ray")
                        self.renderer_path.append(searchPathVray + os.sep + i)

            for i in range(len(vrayVersions)):
                self.gui.listWidget_renderer.insertRow(i)

                vrayItem = QTableWidgetItem("V-Ray")
                vrayItem.setIcon(iconVray)

                self.gui.listWidget_renderer.setItem(i, 0, vrayItem)
                self.gui.listWidget_renderer.setItem(i, 1, QTableWidgetItem(vrayVersions[i]))
                self.gui.listWidget_renderer.setItem(i, 2, QTableWidgetItem(vrayBridgeVersions[i]))
                self.gui.listWidget_renderer.setItem(i, 4, QTableWidgetItem(vrayEntryPathes[i]))

                if os.path.exists(vrayEntryPathes[i] + os.sep + "_install.txt"):
                    button_install = QPushButton("[ install dependencies ]")
                    button_install.setFixedWidth(400)
                    button_install.setStyleSheet("""
                    QPushButton{
                        color:  rgb(155, 155, 155);
                        background-color: rgb(50, 50, 50);
                        border-radius: 5px;
                        border: 1px solid rgb(40, 40, 40);
                    }

                    QPushButton:hover {
                        background-color: rgb(80, 80, 80);
                        color: rgb(0,230,0);
                        border-style: inset;
                    }

                    QPushButton:pressed {
                        background-color: rgb(0, 150, 0);
                        color: rgb(0, 230, 0);
                        border-style: inset;
                    }
                    """)
                    button_install_cellWidget = QWidget()
                    layout = QHBoxLayout()
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setSpacing(0)
                    layout.addWidget(button_install)
                    layout.setAlignment(QtCore.Qt.AlignCenter)
                    button_install_cellWidget.setLayout(layout)
                    
                    lines = []
                    with open(vrayEntryPathes[i] + os.sep + "_install.txt") as f:
                        lines = f.readlines()

                    button_install.clicked.connect(partial(self.openLocation, lines))
                    self.gui.listWidget_renderer.setCellWidget(i, 5, button_install_cellWidget)

                ## Checkboxes ##
                renderer_checkBox = QCheckBox()
                renderer_checkBox.setChecked(False)
                renderer_cellWidget = QWidget()

                if renderer_checkBox.checkState() == QtCore.Qt.Checked:
                    renderer_cellWidget.setStyleSheet('''
                                                    background-color: rgb(100, 100, 100);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);

                                                        ''')
                else:
                    renderer_cellWidget.setStyleSheet('''
                                                    background-color: rgb(50, 50, 50);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);
                                                        ''')
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                layout.addWidget(renderer_checkBox)
                layout.setAlignment(QtCore.Qt.AlignCenter)

                renderer_cellWidget.setLayout(layout)

                renderer_checkBox.stateChanged.connect(partial(self.ns_renderer_checkBoxChanged, i, renderer_checkBox, renderer_cellWidget))
                self.gui.listWidget_renderer.setCellWidget(i, 3, renderer_cellWidget)
                self.gui.listWidget_renderer.setColumnWidth(3, 60)
                self.gui.listWidget_renderer.setColumnWidth(4, 500)
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        ###########################################################################################################
        ## Get Arnold HTOA ########################################################################################
        try:
            arnoldVersions = []
            arnoldHTOAVersions = []
            arnoldEntryPathes = []

            if sys.platform == "darwin": ## macOS ##
                    pass
            if sys.platform == "linux2": ## Linux ##
                    pass
            if sys.platform == "win32": ## Windows ##
                foundedFiles = [d for d in os.listdir(searchPathArnold) if os.path.isdir(os.path.join(searchPathArnold, d))]
                for i in foundedFiles:
                    if i.find("htoa") != -1:
                        parts = i.split("_")
                        arnoldParts = parts[0].split("-")
                        houdiniParts = parts[-1].split("-")
                        
                        arnoldHTOAVersions.append(houdiniParts[1])
                        self.renderer.append("Arnold")
                        arnoldVersions.append(arnoldParts[1])
                        arnoldEntryPathes.append(searchPathArnold + os.sep + i)
                        self.renderer_path.append(searchPathArnold + os.sep + i)


            for i in range(len(arnoldVersions)):
                self.gui.listWidget_renderer.insertRow(i)
                
                arnoldItem = QTableWidgetItem("Arnold")
                arnoldItem.setIcon(iconArnold)

                
                self.gui.listWidget_renderer.setItem(i, 0, arnoldItem)
                self.gui.listWidget_renderer.setItem(i, 1, QTableWidgetItem(arnoldVersions[i]))
                self.gui.listWidget_renderer.setItem(i, 2, QTableWidgetItem(arnoldHTOAVersions[i]))
                self.gui.listWidget_renderer.setItem(i, 4, QTableWidgetItem(arnoldEntryPathes[i]))


                if os.path.exists(arnoldEntryPathes[i] + os.sep + "_install.txt"):
                    button_install = QPushButton("[ install dependencies ]")
                    button_install.setFixedWidth(400)
                    button_install.setStyleSheet("""
                    QPushButton{
                        color:  rgb(155, 155, 155);
                        background-color: rgb(50, 50, 50);
                        border-radius: 5px;
                        border: 1px solid rgb(40, 40, 40);
                    }

                    QPushButton:hover {
                        background-color: rgb(80, 80, 80);
                        color: rgb(0,230,0);
                        border-style: inset;
                    }

                    QPushButton:pressed {
                        background-color: rgb(0, 150, 0);
                        color: rgb(0, 230, 0);
                        border-style: inset;
                    }
                    """)
                    button_install_cellWidget = QWidget()
                    layout = QHBoxLayout()
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setSpacing(0)
                    layout.addWidget(button_install)
                    layout.setAlignment(QtCore.Qt.AlignCenter)
                    button_install_cellWidget.setLayout(layout)
                    
                    lines = []
                    with open(arnoldEntryPathes[i] + os.sep + "_install.txt") as f:
                        lines = f.readlines()

                    button_install.clicked.connect(partial(self.openLocation, lines))
                    self.gui.listWidget_renderer.setCellWidget(i, 5, button_install_cellWidget)



                ## Checkboxes ##
                renderer_checkBox = QCheckBox()
                renderer_checkBox.setChecked(False)
                renderer_cellWidget = QWidget()

                if renderer_checkBox.checkState() == QtCore.Qt.Checked:
                    renderer_cellWidget.setStyleSheet('''
                                                    background-color: rgb(100, 100, 100);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);
                                                        ''')
                else:
                    renderer_cellWidget.setStyleSheet('''
                                                    background-color: rgb(50, 50, 50);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);
                                                        ''')
                layout = QHBoxLayout()
                layout.setContentsMargins(0,0,0,0)
                layout.setSpacing(0)
                layout.addWidget(renderer_checkBox)
                layout.setAlignment(QtCore.Qt.AlignCenter)
                
                renderer_cellWidget.setLayout(layout)

                renderer_checkBox.stateChanged.connect(partial(self.ns_renderer_checkBoxChanged, i, renderer_checkBox,  renderer_cellWidget))
                self.gui.listWidget_renderer.setCellWidget(i, 3, renderer_cellWidget)
                self.gui.listWidget_renderer.setColumnWidth(3, 60)
                self.gui.listWidget_renderer.setColumnWidth(4, 500)
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        ###########################################################################################################
        ## Get Redshift ###########################################################################################
        try:
            rsVersions = []
            rsEntryPathes = []

            if sys.platform == "darwin":  ## macOS ##
                pass
            if sys.platform == "linux2":  ## Linux ##
                pass
            if sys.platform == "win32":  ## Windows ##
                foundedFiles = [d for d in os.listdir(searchPathRedshift) if os.path.isdir(os.path.join(searchPathRedshift, d))]

                for i in foundedFiles:
                    if i.find("Redshift") != -1:
                        parts = i.split("_")
                        rsVersions.append(parts[1])
                        self.renderer.append("Redshift")
                        rsEntryPathes.append(searchPathRedshift + os.sep + i)
                        self.renderer_path.append(searchPathRedshift + os.sep + i)

            if sys.platform == "darwin":  ## macOS ##
                pass
            if sys.platform == "linux2":  ## Linux ##
                pass
            if sys.platform == "win32":  ## Windows ##
                for i in range(len(rsVersions)):
                    rsPluginVersions = [d for d in os.listdir(rsEntryPathes[i] + os.sep + "plugins" + os.sep + "houdini") if os.path.isdir(os.path.join(rsEntryPathes[i] + os.sep + "plugins" + os.sep + "houdini", d))]
                    rsItem = QTableWidgetItem("Redshift")
                    rsItem.setIcon(iconRS)

                    self.gui.listWidget_renderer.insertRow(self.gui.listWidget_renderer.rowCount())
                    self.gui.listWidget_renderer.setItem(self.gui.listWidget_renderer.rowCount()-1, 0, rsItem)
                    self.gui.listWidget_renderer.setItem(self.gui.listWidget_renderer.rowCount()-1, 1, QTableWidgetItem(rsVersions[i]))
                    self.gui.listWidget_renderer.setItem(self.gui.listWidget_renderer.rowCount()-1, 2, QTableWidgetItem("combo"))
                    self.gui.listWidget_renderer.setItem(self.gui.listWidget_renderer.rowCount()-1, 4, QTableWidgetItem(rsEntryPathes[i]))

                    if os.path.exists(rsEntryPathes[i] + os.sep + "_install.txt"):
                        button_install = QPushButton("[ install dependencies ]")
                        button_install.setFixedWidth(400)
                        button_install.setStyleSheet("""
                        QPushButton{
                            color:  rgb(155, 155, 155);
                            background-color: rgb(50, 50, 50);
                            border-radius: 5px;
                            border: 1px solid rgb(40, 40, 40);
                        }

                        QPushButton:hover {
                            background-color: rgb(80, 80, 80);
                            color: rgb(0,230,0);
                            border-style: inset;
                        }

                        QPushButton:pressed {
                            background-color: rgb(0, 150, 0);
                            color: rgb(0, 230, 0);
                            border-style: inset;
                        }
                        """)
                        button_install_cellWidget = QWidget()
                        layout = QHBoxLayout()
                        layout.setContentsMargins(0, 0, 0, 0)
                        layout.setSpacing(0)
                        layout.addWidget(button_install)
                        layout.setAlignment(QtCore.Qt.AlignCenter)
                        button_install_cellWidget.setLayout(layout)
                        
                        lines = []
                        with open(rsEntryPathes[i] + os.sep + "_install.txt") as f:
                            lines = f.readlines()

                        button_install.clicked.connect(partial(self.openLocation, lines))
                        self.gui.listWidget_renderer.setCellWidget(i, 5, button_install_cellWidget)

                    ## Checkboxes ##
                    renderer_checkBox = QCheckBox()
                    renderer_checkBox.setChecked(False)
                    renderer_cellWidget = QWidget()

                    if renderer_checkBox.checkState() == QtCore.Qt.Checked:
                        renderer_cellWidget.setStyleSheet('''
                                                    background-color: rgb(100, 100, 100);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);
                                                            ''')
                    else:
                        renderer_cellWidget.setStyleSheet('''
                                                    background-color: rgb(50, 50, 50);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);
                                                            ''')
                    layout = QHBoxLayout()
                    layout.addWidget(renderer_checkBox)
                    renderer_cellWidget.setLayout(layout)
                    renderer_checkBox.stateChanged.connect(partial(self.ns_renderer_checkBoxChanged, self.gui.listWidget_renderer.rowCount()-1, renderer_checkBox, renderer_cellWidget))
                    self.gui.listWidget_renderer.setCellWidget(self.gui.listWidget_renderer.rowCount()-1, 3, renderer_cellWidget)


                    ## Combobox ##
                    renderer_comboBox = QComboBox()
                    for i in rsPluginVersions:
                        renderer_comboBox.addItem(i)
                    renderer_cellWidget = QWidget()

                    renderer_cellWidget.setStyleSheet('''
                                                    QComboBox::drop-down {
                                                        image: url(:/UI/arrow.png);
                                                        right: 5px;
                                                        top: 5 px;
                                                    }
                                                        ''')

                    layout = QHBoxLayout()
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setSpacing(0)
                    layout.addWidget(renderer_comboBox)
                    renderer_comboBox.setFixedWidth(100)
                    layout.setAlignment(QtCore.Qt.AlignCenter)

                    renderer_cellWidget.setLayout(layout)

                    self.gui.listWidget_renderer.setCellWidget(self.gui.listWidget_renderer.rowCount()-1, 2, renderer_cellWidget)
                    self.gui.listWidget_renderer.setColumnWidth(0, 120)
                    self.gui.listWidget_renderer.setColumnWidth(1, 60)
                    self.gui.listWidget_renderer.setColumnWidth(2, 100)
                    self.gui.listWidget_renderer.setColumnWidth(3, 50)
                    self.gui.listWidget_renderer.setColumnWidth(4, 500)
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        ###########################################################################################################    
        ## Workgroups #############################################################################################    
        try:
            workgroupEntryPathes = []
            workgroupName = []

            if sys.platform == "darwin": ## macOS ##
                    pass
            if sys.platform == "linux2": ## Linux ##
                    pass
            if sys.platform == "win32": ## Windows ##

                foundedFiles = [d for d in os.listdir(searchPathWorkgroups) if os.path.isdir(os.path.join(searchPathWorkgroups, d))]
                for i in foundedFiles:

                    if i.find("Houdini") != -1:

                        self.workgroups_path.append(searchPathWorkgroups + os.sep + i)
                        workgroupEntryPathes.append(searchPathWorkgroups + os.sep + i)
                        self.workgroups.append(i)
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

                if os.path.exists(workgroupEntryPathes[i] + os.sep + "_install.txt"):
                    button_install = QPushButton("[ install dependencies ]")
                    button_install.setFixedWidth(400)
                    button_install.setStyleSheet("""
                    QPushButton{
                        color:  rgb(155, 155, 155);
                        background-color: rgb(50, 50, 50);
                        border-radius: 5px;
                        border: 1px solid rgb(40, 40, 40);
                    }

                    QPushButton:hover {
                        background-color: rgb(80, 80, 80);
                        color: rgb(0,230,0);
                        border-style: inset;
                    }

                    QPushButton:pressed {
                        background-color: rgb(0, 150, 0);
                        color: rgb(0, 230, 0);
                        border-style: inset;
                    }
                    """)
                    button_install_cellWidget = QWidget()
                    layout = QHBoxLayout()
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setSpacing(0)
                    layout.addWidget(button_install)
                    layout.setAlignment(QtCore.Qt.AlignCenter)
                    button_install_cellWidget.setLayout(layout)
                    
                    lines = []
                    with open(workgroupEntryPathes[i] + os.sep + "_install.txt") as f:
                        lines = f.readlines()

                    button_install.clicked.connect(partial(self.openLocation, lines))
                    self.gui.listWidget_workgroup.setCellWidget(i, 3, button_install_cellWidget)                   

                ## Checkboxes ##
                workgroup_checkBox = QCheckBox()
                workgroup_checkBox.setChecked(False)
                workgroup_cellWidget = QWidget()

                if renderer_checkBox.checkState() == QtCore.Qt.Checked:
                    workgroup_cellWidget.setStyleSheet('''
                                                    background-color: rgb(100, 100, 100);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);
                                                        ''')
                else:
                    workgroup_cellWidget.setStyleSheet('''
                                                    background-color: rgb(50, 50, 50);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);
                                                        ''')
                layout = QHBoxLayout()
                layout.setContentsMargins(0,0,0,0)
                layout.setSpacing(0)
                layout.addWidget(workgroup_checkBox)
                layout.setAlignment(QtCore.Qt.AlignCenter)

                workgroup_cellWidget.setLayout(layout)

                workgroup_checkBox.stateChanged.connect(partial(self.ns_workgroup_checkBoxChanged, i, workgroup_checkBox,  workgroup_cellWidget))
                self.gui.listWidget_workgroup.setCellWidget(i, 1, workgroup_cellWidget)
                self.gui.listWidget_workgroup.setColumnWidth(0, 280)
                self.gui.listWidget_workgroup.setColumnWidth(1, 50)
                self.gui.listWidget_workgroup.setColumnWidth(2, 500)
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        self.loadPresetsToCombo("")


    def ns_renderer_checkBoxChanged(self, rowIndex, renderer_checkBox, renderer_cellWidget):
        typeRenderer = self.gui.listWidget_renderer.item(rowIndex, 0)

        if renderer_checkBox.checkState() == QtCore.Qt.Checked:
            renderer_cellWidget.setStyleSheet('''
                                                    background-color: rgb(100, 100, 100);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);
                                                ''')
            renderer_cellWidget.setToolTip("Active")
        else:
            renderer_cellWidget.setStyleSheet('''
                                                    background-color: rgb(50, 50, 50);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);
                                                ''')

        for i in range(self.gui.listWidget_renderer.rowCount()):
            currentItemType = self.gui.listWidget_renderer.item(i, 0)
            if currentItemType.text() == typeRenderer.text():
                if i != rowIndex:
                    renderer_checkBox = QCheckBox()
                    renderer_checkBox.setChecked(False)
                    renderer_cellWidget = QWidget()

                    if renderer_checkBox.checkState() == QtCore.Qt.Checked:
                        renderer_cellWidget.setStyleSheet('''
                                                    background-color: rgb(100, 100, 100);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);
                                                            ''')
                    else:
                        renderer_cellWidget.setStyleSheet('''
                                                    background-color: rgb(50, 50, 50);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);
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
                                                    background-color: rgb(100, 100, 100);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40); 
                                                ''')
        else:
            workgroup_cellWidget.setStyleSheet('''
                                                    background-color: rgb(50, 50, 50);
                                                    color: rgb(155, 155, 155);
                                                    border-radius: 5px;
                                                    border: 0px solid rgb(40, 40, 40);
                                                ''')


    def openApplication(self):
        if not self.gui.checkBox_hou_packages.isChecked():
            self.openApplication_legacy()
        else:
            self.openApplication_packages()


    def openApplication_packages(self):
        path = ""
        exe_path = ""
        link_path = ""
        flag = False
        globalPresetPath = self.gui.lineEdit_globalPresetLocation.text().replace(os.sep, "/")

        if self.gui.checkBox_hou_packages_global.isChecked(): ## check if global ##
            
            if os.path.exists(globalPresetPath): ## check global preset path ##
                if not os.path.exists(globalPresetPath + "/Packages"):
                    os.mkdir(globalPresetPath + "/Packages")
                    
                reply = QtGui.QMessageBox.warning(self, "ns_Startup - Package", "Use current preset name?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.Yes: ## use current global preset name ##
                    
                    path = str(globalPresetPath + "/Packages/" + self.gui.comboBox_preset.currentText())
                    
                    if os.path.exists(path):
                        reply = QtGui.QMessageBox.warning(self, "ns_Startup - Package", "Global folder " + path.replace(os.sep, "/") + " already exist. Delete?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                        if reply == QtGui.QMessageBox.Yes:
                            
                            shutil.rmtree(path, ignore_errors=True)
                            
                            while os.path.exists(path):
                                time.sleep(1)
                         
                            os.mkdir(path)
                            ## Icon ##
                            pIcon = self.gui.comboBox_preset.itemIcon(self.gui.comboBox_preset.currentIndex()).pixmap(QSize(50 ,50))
                            pIcon.save(path + os.sep + "icon" + ".png", "png")
                            flag = True
                            exe_path = path

                        else:
                            reply = QtGui.QMessageBox.warning(self, "ns_Startup - Package", "Be aware, in this local folder are some older existing packages.", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                            if reply == QtGui.QMessageBox.Yes:
                                flag = True
                            exe_path = path

                    else:
                        os.mkdir(path)
                        ## Icon ##
                        pIcon = self.gui.comboBox_preset.itemIcon(self.gui.comboBox_preset.currentIndex()).pixmap(QSize(50 ,50))
                        pIcon.save(path + os.sep + "icon" + ".png", "png")
                        flag = True
                        exe_path = path
                
                else:  ## use current _global folder ##
                    
                    path = str(globalPresetPath + "/Packages/_global")
                    
                    if os.path.exists(path): ## check _global folder exist ##
                        reply = QtGui.QMessageBox.warning(self, "ns_Startup - Package", "Global folder " + path.replace(os.sep, "/") + " already exist. Delete?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                        if reply == QtGui.QMessageBox.Yes:
                            
                            shutil.rmtree(path, ignore_errors=True)
                            
                            while os.path.exists(path):
                                time.sleep(1)

                            os.mkdir(path.replace("/", os.sep))
                            ## Icon ##
                            pIcon = self.gui.comboBox_preset.itemIcon(self.gui.comboBox_preset.currentIndex()).pixmap(QSize(50 ,50))
                            pIcon.save(path + os.sep + "icon" + ".png", "png")
                            flag = True
                            exe_path = path

                        else:
                            reply = QtGui.QMessageBox.warning(self, "ns_Startup - Package", "Be aware, in this global folder are some older existing packages.", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                            if reply == QtGui.QMessageBox.Yes:
                                flag = True
                            exe_path = path

                    else:
                        os.mkdir(path.replace("/", os.sep))
                        ## Icon ##
                        pIcon = self.gui.comboBox_preset.itemIcon(self.gui.comboBox_preset.currentIndex()).pixmap(QSize(50 ,50))
                        pIcon.save(path + os.sep + "icon" + ".png", "png")
                        flag = True
                        exe_path = path
                      
            else:
                trayIcon.showMessage("Add a proper global preset path. Or use the local location.", icon=QSystemTrayIcon.Information, msecs=10000)
        
        else:
            
            if not os.path.exists(scriptRoot + "/Packages"):
                os.mkdir(scriptRoot + "/Packages")
                
            reply = QtGui.QMessageBox.warning(self, "ns_Startup - Package", "Use current preset name?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                
                path = str(scriptRoot + "/Packages/" + self.gui.comboBox_preset.currentText())
                
                if os.path.exists(path):
                    reply = QtGui.QMessageBox.warning(self, "ns_Startup - Package", "Local folder " + path.replace(os.sep, "/") + " already exist. Delete?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        shutil.rmtree(path, ignore_errors=True)
                        while os.path.exists(path):
                            time.sleep(1)
                        os.mkdir(path.replace("/", os.sep))
                        ## Icon ##
                        pIcon = self.gui.comboBox_preset.itemIcon(self.gui.comboBox_preset.currentIndex()).pixmap(QSize(50 ,50))
                        pIcon.save(path + os.sep + "icon" + ".png", "png")
                        flag = True
                        exe_path = path

                    else:
                        reply = QtGui.QMessageBox.warning(self, "ns_Startup - Package", "Be aware, in this local folder are some older existing packages.", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                        if reply == QtGui.QMessageBox.Yes:
                            flag = True
                        exe_path = path


                else:
                    os.mkdir(path)
                    ## Icon ##
                    pIcon = self.gui.comboBox_preset.itemIcon(self.gui.comboBox_preset.currentIndex()).pixmap(QSize(50 ,50))
                    pIcon.save(path + os.sep + "icon" + ".png", "png")
                    flag = True
                    exe_path = path
            
            else:
                
                path = str(scriptRoot + "/Packages/_local")
                
                if os.path.exists(path):
                    reply = QtGui.QMessageBox.warning(self, "ns_Startup - Package", "Local folder " + path.replace(os.sep, "/") + " already exist. Delete?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        shutil.rmtree(path, ignore_errors=True)
                        while os.path.exists(path):
                            time.sleep(1)
                        os.mkdir(path.replace("/", os.sep))
                        ## Icon ##
                        pIcon = self.gui.comboBox_preset.itemIcon(self.gui.comboBox_preset.currentIndex()).pixmap(QSize(50 ,50))
                        pIcon.save(path + os.sep + "icon" + ".png", "png")
                        flag = True
                        exe_path = path
                    else:
                        reply = QtGui.QMessageBox.warning(self, "ns_Startup - Package", "Be aware, in this local folder are some older existing packages.", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                        if reply == QtGui.QMessageBox.Yes:
                            flag = True
                        exe_path = path
                
                else:
                    os.mkdir(path)
                    ## Icon ##
                    pIcon = self.gui.comboBox_preset.itemIcon(self.gui.comboBox_preset.currentIndex()).pixmap(QSize(50 ,50))
                    pIcon.save(path + os.sep + "icon" + ".png", "png")
                    flag = True
                    exe_path = path

        if flag:
            exe_path = exe_path.replace("/", os.sep)
            ## prepare packages ##
            houVersion = self.gui.comboBox_HOUVersion.currentText()
            exeVersion = self.gui.comboBox_exeVersion.currentText()
            self.write_package_hou_link_json(self.gui.comboBox_HOUVersion.currentText(), self.gui.comboBox_exeVersion.currentText(), searchPathHoudiniWIN + os.sep + houVersion + os.sep + "bin" + os.sep + exeVersion, exe_path.replace("/", os.sep))
            self.write_packages(exe_path)

            ## execute ##
            executeString = "\necho ns_Startup " + version + " \n\n"
            executeString = executeString + "SET " + "\"HOUDINI_PACKAGE_DIR=" + path + "\"" + "\n"
            executeString = executeString + "START /d " + "\"" + searchPathHoudiniWIN + os.sep + houVersion + os.sep + "bin" + "\" " + exeVersion

            ## Debug Log ##
            prev_text = self.gui.textEdit_debug_log.toPlainText()
            prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> create startup.bat:\n------------------------------------------" + executeString + "\n------------------------------------------"
            self.gui.textEdit_debug_log.setText(prev_text)
            ## Debug Log - End ##

            if sys.platform == "darwin": ## macOS ##
                pass
                #TODO macOS version
            if sys.platform == "linux2": ## Linux ##
                pass
                #TODO linux version
            if sys.platform == "win32": ## Windows ##
                batFile = open(scriptRoot + os.sep + "startup.bat", "w")
                batFile.write(executeString)
                batFile.close()

                p = subprocess.Popen(scriptRoot + os.sep + "startup.bat", shell=True, stdout=subprocess.PIPE)
                ## Debug Log ##
                prev_text = self.gui.textEdit_debug_log.toPlainText()
                prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> open startup.bat"
                self.gui.textEdit_debug_log.setText(prev_text)
                ## Debug Log - End ##

                stdout, stderr = p.communicate()
                if p.returncode == 0:
                    trayIcon.showMessage("", "ns_Startup> is starting a Houdini session.", icon=QSystemTrayIcon.Information)
                else:
                    trayIcon.showMessage("", "ns_Startup> something went wrong!", icon=QSystemTrayIcon.Information)

                if self.gui.checkBox_deleteBat.isChecked():
                    try:
                        os.remove(scriptRoot + os.sep + "startup.bat")
                        ## Debug Log ##
                        prev_text = self.gui.textEdit_debug_log.toPlainText()
                        prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> delete startup.bat"
                        self.gui.textEdit_debug_log.setText(prev_text)
                        ## Debug Log - End ##
                    except Exception as e:
                        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


    def write_packages(self, path):
        json_db_path = path
        ## look at Lists & AppVersion ##
        selectedRenderer = []
        selectedWorkgroups = []
        houVersion = str(self.gui.comboBox_HOUVersion.currentText())
        exeVersion = str(self.gui.comboBox_exeVersion.currentText())
        renderService = str(self.gui.lineEdit_renderService.text())

        additionalParameters = str(self.gui.textEdit_addParameters.toPlainText()).split("\n")

        ## selected Renderer ##
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

        ## selected Workgroups ##
        for i in range(self.gui.listWidget_workgroup.rowCount()):
            nameItem = self.gui.listWidget_workgroup.item(i, 0)
            pathItem = self.gui.listWidget_workgroup.item(i, 2)

            cellItem = self.gui.listWidget_workgroup.cellWidget(i, 1)
            cellLayout = cellItem.layout()
            layoutItem = cellLayout.itemAt(0)
            checkboxItem = layoutItem.widget()
            if checkboxItem.isChecked():
                selectedWorkgroups.append([str(nameItem.text()), str(pathItem.text())])

        ## write additional env-para(s) json(s) ##      
        with open(json_db_path + os.sep + "_Add.json", 'w') as outfile:
            out = {}
            out['env'] = []
            for add_para in additionalParameters:
                para_parts = add_para.split("=")
                out['env'].append({
                        para_parts[0]: para_parts[1].replace("\"", ""),
                    })
            json.dump(out, outfile, indent=4)
        
        ## write Workgroup(s) json(s) ##
        for i in range(len(selectedWorkgroups)):
            ## HSITE ##
            if "Workgroup_Houdini_H" in selectedWorkgroups[i][0]:
                ## init Paths ##
                paths = []
                houdiniPaths = []
                houdiniOtlScanPaths = []
                houdiniToolbarPaths = []
                houdiniGalleryPaths = []
                houdiniScriptPaths = []
                houdiniPythonPanelsPaths = []

                houdiniPaths.append(selectedWorkgroups[i][1])

                # subfolders check in otls folder ##
                y=0
                for x in os.walk(selectedWorkgroups[i][1] + os.sep + "otls"): 
                    allFolders = x[0].split(os.sep)
                    if allFolders[-1] != "backup":
                        houdiniOtlScanPaths.append(x[0])
                        y=y+1

                

                with open(json_db_path + os.sep + "_" + selectedWorkgroups[i][0] + ".json", 'w') as outfile:
                    houdiniHsite = [selectedWorkgroups[i][1]]
                    houdiniToolbarPaths.append(selectedWorkgroups[i][1] + os.sep + "toolbar")
                    houdiniGalleryPaths.append(selectedWorkgroups[i][1] + os.sep + "gallery")
                    houdiniScriptPaths.append(selectedWorkgroups[i][1] + os.sep + "scripts")
                    houdiniPythonPanelsPaths.append(selectedWorkgroups[i][1] + os.sep + "python_panels")
                    out = {}
                    out['env'] = [
                            {'PATH': []}
                        ]

                    for i in houdiniHsite:
                        split_i = i.split(":")
                        linux_i = "/mnt/Library" + split_i[1].replace("\\", "/")
                        out['env'].append(
                                        {'HSITE': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })
                        out['env'].append(
                                        {'HOUDINI_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })

                    for i in houdiniOtlScanPaths:
                        split_i = i.split(":")
                        linux_i = "/mnt/Library" + split_i[1].replace("\\", "/")
                        out['env'].append(
                                        {'HSITE_OTLSCAN_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })
                        out['env'].append(
                                        {'HOUDINI_OTLSCAN_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })

                    for i in houdiniGalleryPaths:
                        split_i = i.split(":")
                        linux_i = "/mnt/Library" + split_i[1].replace("\\", "/")
                        out['env'].append(
                                        {'HSITE_GALLERY_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })
                        out['env'].append(
                                        {'HOUDINI_GALLERY_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })

                    for i in houdiniToolbarPaths:
                        split_i = i.split(":")
                        linux_i = "/mnt/Library" + split_i[1].replace("\\", "/")
                        out['env'].append(
                                        {'HSITE_TOOLBAR_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })
                        out['env'].append(
                                        {'HOUDINI_TOOLBAR_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })

                    for i in houdiniScriptPaths:
                        split_i = i.split(":")
                        linux_i = "/mnt/Library" + split_i[1].replace("\\", "/")
                        out['env'].append(
                                        {'HSITE_SCRIPT_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })
                        out['env'].append(
                                        {'HOUDINI_SCRIPT_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })
                    
                    for i in houdiniPythonPanelsPaths:
                        split_i = i.split(":")
                        linux_i = "/mnt/Library" + split_i[1].replace("\\", "/")
                        out['env'].append(
                                        {'HSITE_PYTHON_PANEL_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })
                        out['env'].append(
                                        {'HOUDINI_PYTHON_PANEL_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })
                        out['env'].append(
                                        {'HOUDINI_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })

                    json.dump(out, outfile, indent=4)

            ## not HSITE ##    
            else:
                # init Paths ##
                paths = []
                houdiniPaths = []
                houdiniOtlScanPaths = []
                houdiniToolbarPaths = []
                houdiniGalleryPaths = []
                houdiniScriptPaths = []
                houdiniPythonPanelsPaths = []

                houdiniPaths.append(selectedWorkgroups[i][1])

                ## subfolders check in otls folder QLIB etc.##
                y=0
                for x in os.walk(selectedWorkgroups[i][1] + os.sep + "otls"):
                    allFolders = x[0].split(os.sep)
                    if allFolders[-1] != "backup":
                        houdiniOtlScanPaths.append(x[0])
                        y=y+1


                with open(json_db_path + os.sep + selectedWorkgroups[i][0] + ".json", 'w') as outfile:
                    houdiniPath = [selectedWorkgroups[i][1]]
                    houdiniToolbarPaths.append(selectedWorkgroups[i][1] + os.sep + "toolbar")
                    houdiniGalleryPaths.append(selectedWorkgroups[i][1] + os.sep + "gallery")
                    houdiniScriptPaths.append(selectedWorkgroups[i][1] + os.sep + "scripts")
                    houdiniPythonPanelsPaths.append(selectedWorkgroups[i][1] + os.sep + "python_panels")
                    
                    if selectedWorkgroups[i][1].find("FXLabs") != -1 or selectedWorkgroups[i][1].find("GDT") != -1:
                        paths.append(selectedWorkgroups[i][1] + os.sep + "bin")

                    out = {}
                    out['env'] = [
                            {'PATH': []},
                        ]
                    
                    try:
                        for i in paths:
                            split_i = i.split(":")
                            linux_i = "/mnt/Library" + split_i[1].replace("\\", "/")
                            out['env'].append(
                                            {'PATH': 
                                                {
                                                'value': [{"houdini_os == 'windows'" : i},
                                                          {"houdini_os == 'linux'" : linux_i}],
                                                'method': 'prepend'
                                                }
                                            })
                    except:
                        pass
                    
                    for i in houdiniPath:
                        split_i = i.split(":")
                        linux_i = "/mnt/Library" + split_i[1].replace("\\", "/")
                        out['env'].append(
                                        {'HOUDINI_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })

                    for i in houdiniOtlScanPaths:
                        split_i = i.split(":")
                        linux_i = "/mnt/Library" + split_i[1].replace("\\", "/")
                        out['env'].append(
                                        {'HOUDINI_OTLSCAN_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })

                    for i in houdiniGalleryPaths:
                        split_i = i.split(":")
                        linux_i = "/mnt/Library" + split_i[1].replace("\\", "/")
                        out['env'].append(
                                        {'HOUDINI_GALLERY_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })

                    for i in houdiniToolbarPaths:
                        split_i = i.split(":")
                        linux_i = "/mnt/Library" + split_i[1].replace("\\", "/")
                        out['env'].append(
                                        {'HOUDINI_TOOLBAR_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })

                    for i in houdiniScriptPaths:
                        split_i = i.split(":")
                        linux_i = "/mnt/Library" + split_i[1].replace("\\", "/")
                        out['env'].append(
                                        {'HOUDINI_SCRIPT_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })
                    
                    for i in houdiniPythonPanelsPaths:
                        split_i = i.split(":")
                        linux_i = "/mnt/Library" + split_i[1].replace("\\", "/")
                        out['env'].append(
                                        {'HOUDINI_PYTHON_PANEL_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })
                        out['env'].append(
                                        {'HOUDINI_PATH': 
                                            {
                                            'value': [{"houdini_os == 'windows'" : i},
                                                      {"houdini_os == 'linux'" : linux_i}],
                                            'method': 'append'
                                            }
                                        })



                    json.dump(out, outfile, indent=4)
        
        ## write Rendere(r) json(s) ##
        for i in range(len(selectedRenderer)):        
            ## Redshift ##
            ## TODO HYDRA ##
            if selectedRenderer[i][0] == "Redshift":
                with open(json_db_path + os.sep + selectedRenderer[i][0] + ".json", 'w') as outfile:
                    out = {}
                    out['env'] = [
                            {'PATH': 
                                {
                                'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "bin"},
                                          {"houdini_os == 'linux'" : "TODO"}],
                                'method': 'append'
                                }
                            }
                        ]
                    out['env'].append(
                                    {'HOUDINI_PATH': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "Plugins" + os.sep + "Houdini" + os.sep + selectedRenderer[i][2]},
                                                  {"houdini_os == 'linux'" : "TODO"}],
                                        'method': 'append'
                                        }
                                    })
                    out['env'].append(
                                    {'RS_CMD': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "bin" + os.sep + "redshiftCmdLine.exe"},
                                                  {"houdini_os == 'linux'" : "TODO"}],
                                        'method': 'append'
                                        }
                                    })
                    json.dump(out, outfile, indent=4)
                    ## Additional Redshift ENV variables ##
                    with open(json_db_path + os.sep + selectedRenderer[i][0] + "_Add" + ".json", 'w') as outfile:
                        out = {}
                        out['env'] = [## Redshift ##
                                {'REDSHIFT_COREDATAPATH': [selectedRenderer[i][3]],
                                 'REDSHIFT_LOCALDATAPATH': [selectedRenderer[i][3]],
                                 'REDSHIFT_PROCEDURALSPATH': [selectedRenderer[i][3] + os.sep + "Procedurals"],
                                }
                            ]
                        if self.gui.checkBox_local_rs_lic.isChecked():
                            out['env'].append(
                                {
                                'REDSHIFT_LICENSEPATH': [("C:/ProgramData/Redshift").replace(("/"), os.sep)],
                                'REDSHIFT_PREFSPATH': [("C:/ProgramData/Redshift/preferences.xml").replace(("/"), os.sep)],
                                'REDSHIFT_LOGPATH': [("C:/ProgramData/Redshift/Log").replace(("/"), os.sep)],
                                })
                        json.dump(out, outfile, indent=4)

            ## Arnold ##
            ## TODO HYDRA ##
            if selectedRenderer[i][0] == "Arnold":
                split_renderPath = selectedRenderer[i][3].split(":")
                linux_renderPath = "/mnt/Library" + split_renderPath[1].replace("\\", "/")
                
                with open(json_db_path + os.sep + selectedRenderer[i][0] + ".json", 'w') as outfile:
                    out = {}
                    out['env'] = [
                            {'PATH': 
                                {
                                'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "scripts" + os.sep + "bin"},
                                          {"houdini_os == 'linux'" :   linux_renderPath + os.sep + "scripts" + os.sep + "bin"}],
                                'method': 'append'
                                }
                            }
                        ]

                    out['env'].append(
                                    {'HOUDINI_PATH': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3]},
                                                  {"houdini_os == 'linux'" :   linux_renderPath}],
                                        'method': 'append'
                                        }
                                    })

                    out['env'].append(
                                    {'HOUDINI_OTLSCAN_PATH': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "otls"},
                                                  {"houdini_os == 'linux'" :   linux_renderPath + os.sep + "otls"}],
                                        'method': 'append'
                                        }
                                    })

                    out['env'].append(
                                    {'HOUDINI_TOOLBAR_PATH': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "toolbar"},
                                                  {"houdini_os == 'linux'" :   linux_renderPath + os.sep + "toolbar"}],
                                        'method': 'append'
                                        }
                                    })

                    out['env'].append(
                                    {'HOUDINI_SCRIPT_PATH': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "scripts"},
                                                  {"houdini_os == 'linux'" :   linux_renderPath + os.sep + "scripts"}],
                                        'method': 'append'
                                        }
                                    })
                    out['env'].append(
                                    {'ARNOLD_KICKPATH': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "scripts" + os.sep + "bin" + os.sep + "kick.exe"},
                                                  {"houdini_os == 'linux'" :   "TODO"}],
                                        'method': 'append'
                                        }
                                    })
                    json.dump(out, outfile, indent=4)
                
                with open(json_db_path + os.sep + selectedRenderer[i][0] + "_Add" + ".json", 'w') as outfile:
                    out = {}
                    out['env'] = [
                            {'solidangle_LICENSE': [str(self.gui.lineEdit_arnoldLic.text())]}
                            ]
                        
                    json.dump(out, outfile, indent=4)
            
            ## V-Ray ##
            ## TODO HYDRA ##
            if selectedRenderer[i][0] == "V-Ray":
                split_renderPath = selectedRenderer[i][3].split(":")
                linux_renderPath = "/mnt/Library" + split_renderPath[1].replace("\\", "/")
                
                with open(json_db_path + os.sep + selectedRenderer[i][0] + ".json", 'w') as outfile:
                    out = {}
                    out['env'] = [
                            {'PATH': 
                                {
                                'value': [{"houdini_os == 'windows'" : [selectedRenderer[i][3] + os.sep + "vfh_home" + os.sep + "bin", selectedRenderer[i][3] + os.sep + "appsdk" + os.sep + "bin", selectedRenderer[i][3] + os.sep + "vfh_home" + os.sep + "libs"]},
                                          {"houdini_os == 'linux'" : [linux_renderPath + os.sep + "vfh_home" + os.sep + "bin", linux_renderPath + os.sep + "appsdk" + os.sep + "bin", linux_renderPath + os.sep + "vfh_home" + os.sep + "libs"]}],
                                'method': 'append'
                                }
                            }
                        ]
                    out['env'].append(
                                    {'HOUDINI_PATH': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "vfh_home"},
                                                  {"houdini_os == 'linux'" : linux_renderPath + os.sep + "vfh_home"}],
                                        'method': 'append'
                                        }
                                    })
                    out['env'].append(
                                    {'VRAY_APPSDK': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "appsdk"},
                                                  {"houdini_os == 'linux'" : linux_renderPath + os.sep + "appsdk"}],
                                        'method': 'append'
                                        }
                                    })
                    out['env'].append(
                                    {'VRAY_OSL_PATH': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "appsdk" + os.sep + "bin"},
                                                  {"houdini_os == 'linux'" : linux_renderPath + os.sep + "appsdk" + os.sep + "bin"}],
                                        'method': 'append'
                                        }
                                    })
                    out['env'].append(
                                    {'VRAY_UI_DS_PATH': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "ui"},
                                                  {"houdini_os == 'linux'" : linux_renderPath + os.sep + "ui"}],
                                        'method': 'append'
                                        }
                                    })
                    out['env'].append(
                                    {'VFH_HOME': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "vfh_home"},
                                                  {"houdini_os == 'linux'" : linux_renderPath + os.sep + "vfh_home"}],
                                        'method': 'append'
                                        }
                                    })
                    out['env'].append(
                                    {'VRAY_FOR_HOUDINI_AURA_LOADERS': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "vfh_home" + os.sep + "libs"},
                                                  {"houdini_os == 'linux'" : linux_renderPath + os.sep + "vfh_home" + os.sep + "libs"}],
                                        'method': 'append'
                                        }
                                    })
                    out['env'].append(
                                    {'VFH_PATH': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "vfh_home" + os.sep + "libs"},
                                                  {"houdini_os == 'linux'" : linux_renderPath + os.sep + "vfh_home" + os.sep + "libs"}],
                                        'method': 'append'
                                        }
                                    })
                    json.dump(out, outfile, indent=4)
    
            ## Octane ##
            ## TODO HYDRA ##
            if selectedRenderer[i][0] == "Octane":
                split_renderPath = selectedRenderer[i][3].split(":")
                linux_renderPath = "/mnt/Library" + split_renderPath[1].replace("\\", "/")
                
                with open(json_db_path + os.sep + selectedRenderer[i][0] + ".json", 'w') as outfile:
                    out = {}
                    out['env'] = [
                            {'PATH': 
                                {
                                'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3] + os.sep + "bin"},
                                          {"houdini_os == 'linux'" :   linux_renderPath + os.sep + "bin"}],
                                'method': 'append'
                                }
                            }
                        ]
                    out['env'].append(
                                    {'HOUDINI_PATH': 
                                        {
                                        'value': [{"houdini_os == 'windows'" : selectedRenderer[i][3]},
                                                  {"houdini_os == 'linux'" :   linux_renderPath}],
                                        'method': 'append'
                                        }
                                    })
                    json.dump(out, outfile, indent=4)

            ## Renderservice ##
            split_renderService = renderService.split(":")
            linux_renderService = "/mnt/Library" + split_renderService[1].replace("\\", "/")
            with open(json_db_path + os.sep + "_RenderService.json", 'w') as outfile:
                out = {}
                out['env'] = [
                        {'HOUDINI_PATH_RENDER_SERVICE': 
                            {
                            'value': [{"houdini_os == 'windows'" : renderService},
                                      {"houdini_os == 'linux'" : "TODO"}],
                            }
                        },
                        {'HOUDINI_PATH': 
                            {
                            'value': [{"houdini_os == 'windows'" : renderService},
                                      {"houdini_os == 'linux'" : "TODO"}],
                            'method': 'append'
                            }
                        },
                        {'HOUDINI_MENU_PATH': 
                            {
                            'value': [{"houdini_os == 'windows'" : renderService},
                                      {"houdini_os == 'linux'" : "TODO"}],
                            'method': 'append'
                            }
                        }
                        ]
                json.dump(out, outfile, indent=4)


    def write_package_hou_link_json(self, hou_version, hou_bin, hou_path, package_path):
        package_name = package_path.split(os.sep)
        dest_path = ""

        if self.gui.checkBox_hou_packages_global.isChecked():
            dest_path = globalPresetPath + "/Packages"
        else:
            dest_path = scriptRoot + "/Packages"

        json_db_path = dest_path.replace("/", os.sep) + os.sep + "hou_references.json"    
        packages = []
        hou_versions = []
        hou_bins = []
        hou_paths = []
        hou_paths_linux = []

        ## try read existing ##
        try:
            with open(json_db_path) as f:
                json_db_data = json.load(f)

            ## Fill Arrays ##
            for items in json_db_data['data']:
                if items['package'] != package_name[-1]:
                    packages.append(items['package'])
                    hou_versions.append(items['hou_version'])
                    hou_bins.append(items['hou_bin'])
                    hou_paths.append(items['hou_path'])
                    hou_paths_linux.append(items['hou_path_linux'])
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


        ## write ##
        try:    
            with open(json_db_path, 'w') as outfile:
                hou_path_linux = "TODO"
                out = {}
                out['data'] = []
                out['data'].append({
                        'package': str(package_name[-1]),
                        'hou_version': str(hou_version),
                        'hou_bin': str(hou_bin),
                        'hou_path': str(hou_path),
                        'hou_path_linux': str(hou_path_linux),
                    })
                

                ## write existing ##
                i = 0
                for package in packages:
                    out['data'].append({
                        'package': str(packages[i]),
                        'hou_version': str(hou_versions[i]),
                        'hou_bin': str(hou_bins[i]),
                        'hou_path': str(hou_paths[i]),
                        'hou_path_linux': str(hou_path_linux),
                    })
                    i = i + 1
                json.dump(out, outfile, indent=4)
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
    

    def openApplication_legacy(self):
        executeString = "\necho ns_Startup " + version + " \n\n"
        additionalParameters = str(self.gui.textEdit_addParameters.toPlainText()).split("\n")
        for i in range(len(additionalParameters)):
            executeString = executeString + "SET " + "\"" + additionalParameters[i] + "\"" + "\n"

        ## Look at Lists & AppVersion ##
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
        houdiniPythonPanelsPaths = []
        vrayAdds = []

        ## Reset package location##
        os.environ["HOUDINI_PACKAGE_DIR"] = ""

        ## Renderer ##
        for i in range(len(selectedRenderer)):
            if selectedRenderer[i][0] == "Redshift":
                executeString = executeString + "SET " + "\"" + "PATH_RENDERER_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + os.sep + "bin" + "\"" + "\n"
                paths.append("%PATH_RENDERER_" + selectedRenderer[i][0].upper() + "%")
                executeString = executeString + "SET " + "\"" + "HOUDINI_PATH_RENDERER_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + os.sep + "Plugins" + os.sep + "Houdini" + os.sep + selectedRenderer[i][2] + "\"" + "\n"
                houdiniPaths.append("%HOUDINI_PATH_RENDERER_" + selectedRenderer[i][0].upper() + "%")
                #######################################################################################
                ## set ENVs ###########################################################################
                os.environ["REDSHIFT_COREDATAPATH"] = selectedRenderer[i][3]
                os.environ["REDSHIFT_LOCALDATAPATH"] = selectedRenderer[i][3]
                os.environ["REDSHIFT_PROCEDURALSPATH"] = selectedRenderer[i][3] + os.sep + "Procedurals"
                ## local only workaround ##
                if self.gui.checkBox_local_rs_lic.isChecked():
                    os.environ["REDSHIFT_LICENSEPATH"] = ("C:/ProgramData/Redshift").replace(("/"), os.sep)
                    os.environ["REDSHIFT_PREFSPATH"] = ("C:/ProgramData/Redshift/preferences.xml").replace(("/"), os.sep)
                    os.environ["REDSHIFT_LOGPATH"] = ("C:/ProgramData/Redshift/Log").replace(("/"), os.sep)

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

                executeString = executeString + "SET " + "\"" + "ARNOLD_KICKPATH_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + os.sep + "scripts" + os.sep + "bin" + os.sep + "kick.exe" + "\"" + "\n"
                houdiniScriptPaths.append("%HOUDINI_SCRIPT_PATH_" + selectedRenderer[i][0].upper() + "%")

            if selectedRenderer[i][0] == "V-Ray":
                path = selectedRenderer[i][3].split(os.sep)

                executeString = executeString + "SET " + "\"" + "PATH_RENDERER_0_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + os.sep + "vfh_home" + os.sep + "bin" + "\"" + "\n"
                paths.append("%PATH_RENDERER_0_" + selectedRenderer[i][0].upper() + "%")

                executeString = executeString + "SET " + "\"" + "PATH_RENDERER_1_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + os.sep + "appsdk" + os.sep + "bin" + "\"" + "\n"
                paths.append("%PATH_RENDERER_1_" + selectedRenderer[i][0].upper() + "%")

                executeString = executeString + "SET " + "\"" + "PATH_RENDERER_2_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + os.sep + "vfh_home" + os.sep + "libs" + "\"" + "\n"
                paths.append("%PATH_RENDERER_2_" + selectedRenderer[i][0].upper() + "%")

                executeString = executeString + "SET " + "\"" + "HOUDINI_PATH_RENDERER_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + os.sep + "vfh_home" + "\"" + "\n"
                houdiniPaths.append("%HOUDINI_PATH_RENDERER_" + selectedRenderer[i][0].upper() + "%")

                executeString = executeString + "SET " + "\"" + "VRAY_APPSDK" + "=" + selectedRenderer[i][3] + os.sep + "appsdk" + "\"" + "\n"
                vrayAdds.append("%VRAY_OSL_PATH" + "%")

                executeString = executeString + "SET " + "\"" + "VRAY_OSL_PATH" + "=" + selectedRenderer[i][3] + os.sep + "appsdk" + os.sep + "bin" + "\"" + "\n"
                vrayAdds.append("%VRAY_OSL_PATH" + "%")

                executeString = executeString + "SET " + "\"" + "VRAY_UI_DS_PATH" + "=" + selectedRenderer[i][3] + os.sep + "ui" + "\"" + "\n"
                vrayAdds.append("%VRAY_UI_DS_PATH" + "%")

                executeString = executeString + "SET " + "\"" + "VFH_HOME" + "=" + selectedRenderer[i][3] + os.sep + "vfh_home" + "\"" + "\n"
                vrayAdds.append("VFH_HOME" + "%")

                executeString = executeString + "SET " + "\"" + "VRAY_FOR_HOUDINI_AURA_LOADERS" + "=" + selectedRenderer[i][3] + os.sep + "vfh_home" + os.sep + "libs" + "\"" + "\n"
                vrayAdds.append("VRAY_FOR_HOUDINI_AURA_LOADERS" + "%")

                executeString = executeString + "SET " + "\"" + "VFH_PATH" + "=" + selectedRenderer[i][3] + os.sep + "vfh_home" + os.sep + "bin" + "\"" + "\n"
                vrayAdds.append("VFH_PATH" + "%")

            if selectedRenderer[i][0] == "Octane":
                executeString = executeString + "SET " + "\"" + "PATH_RENDERER_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + os.sep + "bin" + "\"" + "\n"
                paths.append("%PATH_RENDERER_" + selectedRenderer[i][0].upper() + "%")
                executeString = executeString + "SET " + "\"" + "HOUDINI_PATH_RENDERER_" + selectedRenderer[i][0].upper() + "=" + selectedRenderer[i][3] + "\"" + "\n"
                houdiniPaths.append("%HOUDINI_PATH_RENDERER_" + selectedRenderer[i][0].upper() + "%")

        ## Workgroups ##
        for i in range(len(selectedWorkgroups)):
            if "Workgroup_Houdini_H" in selectedWorkgroups[i][0]:
                executeString = executeString + "SET " + "\"" + "HSITE=" + selectedWorkgroups[i][1] + "\"" + "\n"
                houdiniPaths.append("%HSITE%")

                y=0
                for x in os.walk(selectedWorkgroups[i][1] + os.sep + "otls"): ## subfolders check in otls folder ##
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

                executeString = executeString + "SET " + "\"" + "HSITE_PYTHON_PANEL_PATH_" + selectedWorkgroups[i][0].upper() + "=%HSITE%" + os.sep + "python_panels" + "\"" + "\n"
                houdiniPaths.append("%HSITE_PYTHON_PANEL_PATH_" + selectedWorkgroups[i][0].upper() + "%")

            else:
                executeString = executeString + "SET " + "\"" + "HOUDINI_PATH_" + selectedWorkgroups[i][0].upper() + "=" + selectedWorkgroups[i][1] + "\"" + "\n"
                houdiniPaths.append("%HOUDINI_PATH_" + selectedWorkgroups[i][0].upper()+"%")

                y=0
                for x in os.walk(selectedWorkgroups[i][1] + os.sep + "otls"): ## subfolders check in otls folder QLIB##
                    allFolders = x[0].split(os.sep)
                    if allFolders[-1] != "backup":
                        executeString = executeString + "SET " + "\"" + "HOUDINI_OTLSCAN_PATH_" + selectedWorkgroups[i][0].upper() + "_" + str(y) + "=" + x[0] + "\"" + "\n"
                        houdiniOtlScanPaths.append("%HOUDINI_OTLSCAN_PATH_" + selectedWorkgroups[i][0].upper() + "_" + str(y) + "%")
                        y=y+1

                executeString = executeString + "SET " +  "\"" + "HOUDINI_TOOLBAR_PATH_" + selectedWorkgroups[i][0].upper() + "=%PATH_" + selectedWorkgroups[i][0].upper() + "%" + os.sep + "toolbar"  + "\"" + "\n"
                houdiniToolbarPaths.append("%HOUDINI_TOOLBAR_PATH_" + selectedWorkgroups[i][0].upper() + "%")

                if selectedWorkgroups[i][0].find("FXLabs") != -1 or selectedWorkgroups[i][0].find("GDT") != -1 :
                    executeString = executeString + "SET " + "\"" + "PATH_WORK_" + selectedWorkgroups[i][0].upper() + "=" + selectedWorkgroups[i][1] + os.sep + "bin" + "\"" + "\n"
                    paths.append("%PATH_WORK_" + selectedWorkgroups[i][0].upper()+"%")

        ## RenderService ##
        executeString = executeString + "SET " + "\"" + "HOUDINI_PATH_RENDER_SERVICE=" + renderService + "\"" + "\n"
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

        ## Debug Log ##
        prev_text = self.gui.textEdit_debug_log.toPlainText()
        prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> create startup.bat:\n------------------------------------------" + executeString + "\n------------------------------------------"
        self.gui.textEdit_debug_log.setText(prev_text)
        ## Debug Log - End ##


        if sys.platform == "darwin": ## macOS ##
            pass
            #TODO macOS version
        if sys.platform == "linux2": ## Linux ##
            pass
            #TODO linux version
        if sys.platform == "win32": ## Windows ##
            batFile = open(scriptRoot + os.sep + "startup.bat", "w")
            batFile.write(executeString)
            batFile.close()

            p = subprocess.Popen(scriptRoot + os.sep + "startup.bat", shell=True, stdout=subprocess.PIPE)
            ## Debug Log ##
            prev_text = self.gui.textEdit_debug_log.toPlainText()
            prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> open startup.bat"
            self.gui.textEdit_debug_log.setText(prev_text)
            ## Debug Log - End ##

            stdout, stderr = p.communicate()
            if p.returncode == 0:
                trayIcon.showMessage("", "ns_Startup> is starting a Houdini session.", icon=QSystemTrayIcon.Information)
            else:
                trayIcon.showMessage("", "ns_Startup> something went wrong!", icon=QSystemTrayIcon.Information)

            if self.gui.checkBox_deleteBat.isChecked():
                try:
                    os.remove(scriptRoot + os.sep + "startup.bat")
                    ## Debug Log ##
                    prev_text = self.gui.textEdit_debug_log.toPlainText()
                    prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> delete startup.bat"
                    self.gui.textEdit_debug_log.setText(prev_text)
                    ## Debug Log - End ##
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


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
                ## Debug Log ##
                prev_text = self.gui.textEdit_debug_log.toPlainText()
                prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> set Arnold license server to " + str(self.gui.lineEdit_arnoldLic.text())
                self.gui.textEdit_debug_log.setText(prev_text)
                ## Debug Log - End ##
            except Exception as e:
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


    def send_WOL_0(self):
        try:
            ns_Utility.wake_on_lan(str(self.gui.lineEdit_WOL_MAC_0.text()))
            trayIcon.showMessage("ns_Startup", "Send WOL: " + self.gui.lineEdit_WOL_MAC_0.text(), icon=QSystemTrayIcon.Information, msecs=10000)
            ## Debug Log ##
            prev_text = self.gui.textEdit_debug_log.toPlainText()
            prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> send WOL 0 to " + self.gui.lineEdit_WOL_MAC_0.text()
            self.gui.textEdit_debug_log.setText(prev_text)
            ## Debug Log - End ##
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            trayIcon.showMessage("ns_Startup", "Incorrect MAC address format." + self.gui.lineEdit_WOL_MAC_0.text(), icon=QSystemTrayIcon.Information, msecs=10000)


    def send_WOL_1(self):
        try:
            ns_Utility.wake_on_lan(str(self.gui.lineEdit_WOL_MAC_1.text()))
            trayIcon.showMessage("ns_Startup", "Send WOL: " + self.gui.lineEdit_WOL_MAC_1.text(), icon=QSystemTrayIcon.Information, msecs=10000)
            ## Debug Log ##
            prev_text = self.gui.textEdit_debug_log.toPlainText()
            prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> send WOL 1 to " + self.gui.lineEdit_WOL_MAC_1.text()
            self.gui.textEdit_debug_log.setText(prev_text)
            ## Debug Log - End ##
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            trayIcon.showMessage("ns_Startup", "Incorrect MAC address format." + self.gui.lineEdit_WOL_MAC_1.text(), icon=QSystemTrayIcon.Information, msecs=10000)


    def send_WOL_2(self):
        try:
            ns_Utility.wake_on_lan(str(self.gui.lineEdit_WOL_MAC_2.text()))
            trayIcon.showMessage("ns_Startup", "Send WOL: " + self.gui.lineEdit_WOL_MAC_2.text(), icon=QSystemTrayIcon.Information, msecs=10000)
            ## Debug Log ##
            prev_text = self.gui.textEdit_debug_log.toPlainText()
            prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> send WOL 2 to " + self.gui.lineEdit_WOL_MAC_2.text()
            self.gui.textEdit_debug_log.setText(prev_text)
            ## Debug Log - End ##
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            trayIcon.showMessage("ns_Startup", "Incorrect MAC address format." + self.gui.lineEdit_WOL_MAC_2.text(), icon=QSystemTrayIcon.Information, msecs=10000)


    def send_WOL_3(self):
        try:
            ns_Utility.wake_on_lan(str(self.gui.lineEdit_WOL_MAC_3.text()))
            trayIcon.showMessage("ns_Startup", "Send WOL: " + self.gui.lineEdit_WOL_MAC_3.text(), icon=QSystemTrayIcon.Information, msecs=10000)
            ## Debug Log ##
            prev_text = self.gui.textEdit_debug_log.toPlainText()
            prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> send WOL 3 to " + self.gui.lineEdit_WOL_MAC_3.text()
            self.gui.textEdit_debug_log.setText(prev_text)
            ## Debug Log - End ##
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            trayIcon.showMessage("ns_Startup", "Incorrect MAC address format." + self.gui.lineEdit_WOL_MAC_3.text(), icon=QSystemTrayIcon.Information, msecs=10000)


    def saveConfig(self):
        try:
            root = ET.Element("ns_Startup__settings")
            arnoldLic = ET.Element("Arnold_RLM")
            arnoldLic.text = str(self.gui.lineEdit_arnoldLic.text())
            wol0 = ET.Element("WOL_0", Address=str(self.gui.lineEdit_WOL_MAC_0.text()), Description=str(self.gui.lineEdit_WOL_Des_0.text()), StartUp=str(self.gui.checkBox_startUp_0.isChecked()))
            wol1 = ET.Element("WOL_1", Address=str(self.gui.lineEdit_WOL_MAC_1.text()), Description=str(self.gui.lineEdit_WOL_Des_1.text()), StartUp=str(self.gui.checkBox_startUp_1.isChecked()))
            wol2 = ET.Element("WOL_2", Address=str(self.gui.lineEdit_WOL_MAC_2.text()), Description=str(self.gui.lineEdit_WOL_Des_2.text()), StartUp=str(self.gui.checkBox_startUp_2.isChecked()))
            wol3 = ET.Element("WOL_3", Address=str(self.gui.lineEdit_WOL_MAC_3.text()), Description=str(self.gui.lineEdit_WOL_Des_3.text()), StartUp=str(self.gui.checkBox_startUp_3.isChecked()))
            globalPresetPath = ET.Element("Global_Preset_Location", Path=str(self.gui.lineEdit_globalPresetLocation.text()))
            renderService = ET.Element("Render_Service", Path=str(self.gui.lineEdit_renderService.text()))
            chat_host = ET.Element("Chat_Host", Host=str(self.gui.lineEdit_chat_host.text()))
            chat_alias = ET.Element("Chat_Alias", Name=str(self.gui.lineEdit_alias.text()))
            chat_notify = ET.Element("Chat_Notify", Value=str(self.gui.checkBox_chat_notifications.isChecked()))
            chat_notify_sound = ET.Element("Chat_Notify_Sound", Value=str(self.gui.checkBox_chat_notifications_sound.isChecked()))
            local_rs_lic = ET.Element("Use_Local_RS_License", Value=str(self.gui.checkBox_local_rs_lic.isChecked()))
            use_houdini_packages = ET.Element("Use_Houdini_Packages_Mode", Value=str(self.gui.checkBox_hou_packages.isChecked()))
            use_global_preset_for_packages = ET.Element("Use_Global_Preset_Location_For_Packages", Value=str(self.gui.checkBox_hou_packages_global.isChecked()))
            delete_bat = ET.Element("Delete_Exec_Bat", Value=str(self.gui.checkBox_deleteBat.isChecked()))

            root.append(arnoldLic)
            root.append(wol0)
            root.append(wol1)
            root.append(wol2)
            root.append(wol3)
            root.append(globalPresetPath)
            root.append(renderService)
            root.append(chat_host)
            root.append(chat_alias)
            root.append(chat_notify)
            root.append(chat_notify_sound)
            root.append(local_rs_lic)
            root.append(use_houdini_packages)
            root.append(use_global_preset_for_packages)
            root.append(delete_bat)

            xml_beauty = xml.dom.minidom.parseString(ET.tostring(root, encoding='utf8', method='xml'))

            if os.path.exists(configPath):
                pass
            else:
                os.makedirs(configPath)

            xml_file = open(configPath + os.sep + "Config.xml", "w")
            xml_file.write(xml_beauty.toprettyxml())
            xml_file.close()

            ## Debug Log ##
            prev_text = self.gui.textEdit_debug_log.toPlainText()
            prev_text = prev_text + "\n" + datetime.now().strftime("%H:%M:%S") + "> save Config.xml"
            self.gui.textEdit_debug_log.setText(prev_text)
            ## Debug Log - End ##

            os.environ["solidangle_LICENSE"] = str(self.gui.lineEdit_arnoldLic.text())
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


    def fireRoboCopy(self):
        if sys.platform == "darwin":  ## macOS ##
            pass
        if sys.platform == "linux2":  ## Linux ##
            pass
        if sys.platform == "win32":  ## Windows ##
            trayIcon.showMessage("ns_Startup", "Robocopy latest version & restart.", icon=QSystemTrayIcon.Information, msecs=10000)
            time.sleep(3)
            app.quit()
            ## Main ##
            if os.path.exists(maintenanceScriptPath):
                subprocess.call(["robocopy", maintenanceScriptPath, scriptRoot, "/S", "/xd", ".git",  "/xd", ".idea", "/LOG:robocopy_main_log.txt"])
            ## SubmissionScript-User ##
            if os.path.exists(maintenanceRenderScriptPath) and os.path.exists(localRenderSubmitterScripLocationDEADLINE):
                subprocess.call(["robocopy", maintenanceRenderScriptPath, localRenderSubmitterScripLocationDEADLINE, "/S", "/xd", ".git",  "/xd", ".idea", "/LOG:robocopy_main_log.txt"])
            subprocess.Popen(scriptRoot + os.sep + "run_ns_Startup.bat 1", shell=False)


    def openLocation(self, ns_path): 
        for i in range(len(ns_path)):   
            try:
                if os.path.exists(ns_path[i].replace("/", os.sep)):
                    if sys.platform == "darwin": #macOS 
                        subprocess.Popen(["open", "--", ns_path[i].replace("/", os.sep)])
                    if sys.platform == "linux2": #Linux
                        subprocess.Popen(["xdg-open", "--", ns_path[i].replace("/", os.sep)])
                    if sys.platform == "win32": #Windows
                        subprocess.Popen(["explorer", ns_path[i].replace("/", os.sep)])
            except Exception as e:
                pass
                # print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)



###########################################################################################################################################################################################################
## MAIN ###################################################################################################################################################################################################

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    guiTray = uic.loadUi("UI" + os.sep + "ns_Startup.ui")
    trayIcon = SystemTrayIcon(QtGui.QIcon("Logo" + os.sep + "Logo.png"), guiTray)
    trayIcon.show()
    gui = MainWindow()
    sys.exit(app.exec_())
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox, QStackedLayout, QComboBox, QFormLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtCore
from datetime import datetime
from filemng import Filemng
import os
import userdata
import bcrypt
import multi_line
import base64
import socket
from identify import Identify
from threading import Thread
import _thread
import io

batterylevel = [5, 1, 3]
powerlevel = [2, 5, 1]

# Set input file location
input_location = os.getcwd() + '/inputs/'

check_list = ['power.txt', 'alert.txt', 'water.txt', 'diagnostic.txt', 'signal_strength.txt', 'battery_level.txt']
for i in range(len(check_list)):
    check_list[i] = input_location + check_list[i]

class ExtendedQLabel(QLabel):
    def __init(self, parent):
        super().__init__(parent)

    clicked = QtCore.pyqtSignal()
    rightClicked = QtCore.pyqtSignal()

    def mousePressEvent(self, ev):
        if ev.button() == Qt.RightButton:
            self.rightClicked.emit()
        else:
            self.clicked.emit()


class LoginForm(QWidget):

    def __init__(self, parent=None):
        super(LoginForm, self).__init__(parent)
        self.initUI()

    def initUI(self):

        # Place username and password widget
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        self.setLayout(hbox)
        hbox.addItem(QSpacerItem(4, 4, QSizePolicy.Expanding))
        hbox.addLayout(vbox)
        hbox.addItem(QSpacerItem(4, 4,  QSizePolicy.Expanding))
        space1 = QSpacerItem(4, 4, QSizePolicy.Minimum,  QSizePolicy.Expanding)
        vbox.addSpacerItem(space1)
        vbox.setContentsMargins(0, 0, 40, 0)
        grid = QGridLayout()
        grid.addWidget(QLabel('Username:'), 0, 0)
        grid.addWidget(QLabel('Password:'), 1, 0)

        self.userInput = QLineEdit()
        grid.addWidget(self.userInput, 0, 1)
        self.pwdInput = QLineEdit()
        # For password input, set as mask input mode
        self.pwdInput.setEchoMode(QLineEdit.Password)
        grid.addWidget(self.pwdInput, 1, 1)
        vbox.addLayout(grid)

        self.loginBtn = QPushButton('Login')
        # Connect login clicked event
        #self.loginBtn.clicked.connect(self.loginClicked)
        vbox.addWidget(self.loginBtn)
        self.logerrorlabel = QLabel()
        vbox.addWidget(self.logerrorlabel)

        space2 = QSpacerItem(2, 2, QSizePolicy.Minimum,  QSizePolicy.Expanding)
        vbox.addSpacerItem(space2)

        self.show()
        #self.setWindowTitle('Login Form')

    def showErrorLogin(self):
        self.logerrorlabel.setText('Incorrect username and password')

    def loginClicked(self):
        # Check username and password, if matched, then
        # close login form and show main form
        username = self.userInput.text()
        password = self.pwdInput.text()

        #check whether username/password stored
        #in the userdata module checks ok
        #userdata module can be extended to include mysql database
        if (not checkPass(username, password)):
          #user pass do not match
          #print an error message in the mainform
          self.showErrorLogin()
        else:
           #login success
           #generate an event for TopForm
           stxt = 'Login success for ' + username
           self.logerrorlabel.setText(stxt)
           if self.firststack.currentIndex() == 0:
              self.firststack.setCurrentIndex(1)

class TopForm(QMainWindow):

    def __init__(self, parent=None,client_list= None):
        #super(TopForm, self).__init__()
        #super().__init__()
        QMainWindow.__init__(self)
        self.client_list = client_list
        self.initUI(client_list)

    def initUI(self,client=None):

        # Hide default system buttons
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint |
                           Qt.WindowCloseButtonHint)

        #self.screen = QDesktopWidget().screenGeometry()
        #self.setGeometry(0,0,50,40)
        #self.resize(self.screen.width(),self.screen.height())
        self.cwid = QWidget(self)
        self.setCentralWidget(self.cwid)
        self.layout = QGridLayout()
        self.cwid.setLayout(self.layout)

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 20, 0)

        self.mainForm = MainForm(self,client_list=client)
        self.loginForm = LoginForm(self)
        self.loginForm.loginBtn.clicked.connect(self.loginClicked)

        self.firststack = QStackedLayout()
        self.firststack.addWidget(self.loginForm)
        self.firststack.addWidget(self.mainForm)
        self.layout.addLayout(self.firststack, 1, 1)
        #self.layout.addLayout(self.firststack)

        #self.layout.insertStretch(1, 1)
        self.showFullScreen()

    def loginClicked(self):
        # Check username and password, if matched, then
        # close login form and show main form
        username = self.loginForm.userInput.text()
        password = self.loginForm.pwdInput.text()

        #check whether username/password stored
        #in the userdata module checks ok
        #userdata module can be extended to include mysql database
        #if ( 1== 0  ):
        if (not checkPass(username, password)):
          #user pass do not match
          #print an error message in the mainform
          self.loginForm.showErrorLogin()
        else:
           if self.firststack.currentIndex() == 0:
              self.firststack.setCurrentIndex(1)

        if username == password or username == 'admin':
            pass

        change_location(0,self.client_list)

        for i in range(len(check_list)):
            file_changed(check_list[i])

    # Function for place center

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # Default function for close event
    def closeEvent(self, event):
        # Show confirm prompt for exit
        reply = QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class MainForm(QWidget):

    def __init__(self, parent=None,client_list = None):
        super(MainForm, self).__init__()
        self.initUI(client_list)

    def initUI(self,client):

        self.formWidget = FormWidget(self,client_list = client)

        #self.setCentralWidget(self.formWidget)
        #self.statusBar().showMessage('Ready')

        self.setWindowTitle('Ingram Readymix')

        # Setup timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start()

        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.addWidget(self.formWidget)
        self.setLayout(self.vbox)

        self.show()

    def tick(self):
        # Get current time
        now = datetime.now().strftime('%H:%M:%S')
        self.formWidget.clockLabel.setText(now)


class FormWidget(QWidget):

    # General function for get pixmap label
    #opt = 0 give a filename
    #opt = 1 give a png-image-data
    def __get_pixmap(self, pixmap, height=None, opt=0):
        label = QLabel()
        if (opt == 1):
          qimg = QImage.fromData(pixmap)
          pixmap = QPixmap.fromImage(qimg)
        else:
          #qimg  = QImage(pixmap)
          #pixmap = QPixmap.fromImage(qimg)
          pixmap = QPixmap(pixmap)

        if (height):
           pixmap = pixmap.scaledToHeight(height)
        label.setPixmap(pixmap)
        return label

    def __init__(self, parent,client_list):
        super(FormWidget, self).__init__(parent)
        self.locations = []
        self.client_list = client_list
        for client in client_list:
            self.locations.append(client.id)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        headerLayout = QHBoxLayout()
        headerLayout.setContentsMargins(0, 0, 0, 0)

        signalLayout = QHBoxLayout()
        signalLabel = QLabel('Singal Strength')
        signalLabel.setAlignment(Qt.AlignCenter)
        signalLabel.setStyleSheet("color: white;"
                                  "font-size: 16px;"
                                  "background-color: #585858;")
        signalLayout.addWidget(signalLabel)
        level = powerlevel[0]
        fname = 'Icons/' + 'signal' + " " + str(level) + '.png'
        signalImage = self.__get_pixmap(fname, 30)
        signalImage.setAlignment(Qt.AlignRight)
        signalImage.setStyleSheet("color: white;"
                                  "padding-right: 8px;"
                                  "background-color: #585858;")
        self.signalImage = signalImage

        signalLayout.addWidget(signalImage)
        signalLayout.setSpacing(0)
        headerLayout.addLayout(signalLayout)

        locationLayout = QHBoxLayout()
        self.locationLabel = QLabel('Location')
        self.locationLabel.setAlignment(Qt.AlignCenter)
        self.locationLabel.setStyleSheet("color: white;"
                                         "font-size: 16px;"
                                         "background-color: black;")
        locationLayout.addWidget(self.locationLabel)
        locationLayout.setSpacing(0)
        locationLayout.setContentsMargins(0, 0, 0, 0)
        headerLayout.addLayout(locationLayout)

        batteryLayout = QHBoxLayout()
        level = batterylevel[0]
        level = 1
        fname = 'Icons/' + 'Battery' + " " + str(level) + '.png'
        batteryImage = self.__get_pixmap(fname, 30)
        batteryImage.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        batteryImage.setStyleSheet("color: white;"
                                   "background-color: #585858;")
        batteryLayout.addWidget(batteryImage)
        batteryLabel = QLabel('Battery Level')
        batteryLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        batteryLabel.setStyleSheet("color: white;"
                                   "font-size: 16px;"
                                   "background-color: #585858;")
        batteryLayout.addWidget(batteryLabel)
        self.batteryImage = batteryImage

        now = datetime.now().strftime('%H:%M:%S')
        self.clockLabel = QLabel(now)
        self.clockLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.clockLabel.setStyleSheet("color: white;"
                                      "font-size: 16px;"
                                      "padding-left: 24px;"
                                      "padding-right: 8px;"
                                      "background-color: #585858;")
        batteryLayout.addWidget(self.clockLabel)

        batteryLayout.setSpacing(0)
        headerLayout.addLayout(batteryLayout)
        self.layout.addLayout(headerLayout)

        self.displaylayout = self.getDisplay()
        #add the location area to the stacklayout
        self.layout.addLayout(self.displaylayout)

        self.setLayout(self.layout)
        self.show()

    #this layout is the main dispaly area
    #this is divided into grapharea (left) and infoarea(right)
    def getDisplay(self):
        layout = QHBoxLayout()

        #infoarea will be infostack
        self.infostack = QStackedLayout()

        #create and add the grapharea here
        pmap = multi_line.multi_line(0,self.client_list)
        pmap = base64.b64decode(pmap)
        self.grapharea = self.__get_pixmap(pmap, None, 1)
        self.grapharea.setContentsMargins(0, 0, 0, 0)
        self.infostack.addWidget(self.grapharea)

        #power  item
        self.powerinfo = QLabel()
        self.infostack.addWidget(self.powerinfo)
        self.powerinfo.setText("Power Level")
        self.powerinfo.setAlignment(Qt.AlignCenter)

        #alert item
        self.alertinfo = QLabel()
        self.infostack.addWidget(self.alertinfo)
        self.alertinfo.setText("Following Alerts Received!")
        self.alertinfo.setAlignment(Qt.AlignCenter)

        #water item
        pmap = multi_line.multi_line(0,self.client_list)
        pmap = base64.b64decode(pmap)
        self.waterarea = self.__get_pixmap(pmap, None, 1)
        self.infostack.addWidget(self.waterarea)

        #diagnostic item
        self.diaginfo = QLabel()
        self.infostack.addWidget(self.diaginfo)
        self.diaginfo.setText("Diagnostic Info")
        self.diaginfo.setAlignment(Qt.AlignCenter)

        layout.addLayout(self.infostack, 2)

        controlsLayout = QVBoxLayout()

        #Buttons for Power, Alert, Water Level, Diagnostic
        self.powerBtn = ExtendedQLabel('Power')
        self.powerBtn.setFixedHeight(40)
        self.powerBtn.setAlignment(Qt.AlignCenter)
        self.powerBtn.setStyleSheet("color: white;"
                                    "font-size: 16px;"
                                    "background-color: #585858;")
        self.powerBtn.clicked.connect(self.powerClicked)
        controlsLayout.addWidget(self.powerBtn)

        self.alertBtn = ExtendedQLabel('Alert')
        self.alertBtn.setFixedHeight(40)
        self.alertBtn.setAlignment(Qt.AlignCenter)
        self.alertBtn.setStyleSheet("color: white;"
                                    "font-size: 16px;"
                                    "background-color: #585858;")
        self.alertBtn.clicked.connect(self.alertClicked)
        controlsLayout.addWidget(self.alertBtn)

        self.waterBtn = ExtendedQLabel('Water Level')
        self.waterBtn.setFixedHeight(40)
        self.waterBtn.setAlignment(Qt.AlignCenter)
        self.waterBtn.setStyleSheet("color: white;"
                                    "font-size: 16px;"
                                    "background-color: #585858;")
        self.waterBtn.clicked.connect(self.waterClicked)
        controlsLayout.addWidget(self.waterBtn)

        self.diagnosticBtn = ExtendedQLabel('Diagnostic')
        self.diagnosticBtn.setFixedHeight(40)
        self.diagnosticBtn.setAlignment(Qt.AlignCenter)
        self.diagnosticBtn.setStyleSheet("color: white;"
                                         "font-size: 16px;"
                                         "background-color: #585858;")
        self.diagnosticBtn.clicked.connect(self.diagnosticClicked)
        controlsLayout.addWidget(self.diagnosticBtn)

        self.locationsBtn = ExtendedQLabel('Locations')
        self.locationsBtn.setFixedHeight(40)
        self.locationsBtn.setAlignment(Qt.AlignCenter)
        self.locationsBtn.setStyleSheet("color: white;"
                                        "font-size: 16px;"
                                        "background-color: #585858;")
        self.locationsBtn.clicked.connect(self.locationClicked)
        controlsLayout.addWidget(self.locationsBtn)

        # create and fill the combo box to choose the locations
        locationbox = QComboBox(self)
        locationbox.addItems(self.locations)
        locationbox.currentIndexChanged.connect(self.locationSelected)
        self.locationlayout = QFormLayout()
        self.locationlayout.addRow('Locations', locationbox)
        controlsLayout.addLayout(self.locationlayout)

        layout.addLayout(controlsLayout)

        return layout

    # different location selected
    def locationSelected(self, i):
        change_location(i,self.client_list)

    # When click each button, show empty window

    def powerClicked(self):
        self.infostack.setCurrentIndex(1)

    def alertClicked(self):
        self.infostack.setCurrentIndex(2)

    def waterClicked(self):
        self.infostack.setCurrentIndex(3)

    def diagnosticClicked(self):
        self.infostack.setCurrentIndex(4)

    def locationClicked(self):
        self.infostack.setCurrentIndex(0)


#check whether the hashed password
#and the username matches with the
#data in the userdata module
def checkPass(username, password):
   logfail = True
   if (username != userdata.username):
       logfail = False
   password = password.encode("utf-8")
   if (not bcrypt.checkpw(password, userdata.hashedpass)):
       logfail = False
   return logfail


def is_pixmap_exists(fname):
    return os.path.isfile(fname)


def change_level(widget, label, level):
    fname = 'Icons/' + label + " " + str(level) + '.png'
    if (not is_pixmap_exists(fname)):
      return -1

    pixmap = QPixmap(fname)
    pixmap = pixmap.scaledToHeight(30)
    widget.setPixmap(pixmap)

    return level


def change_location(i,client = None):
    global mainWindow

    formWidget = mainWindow.mainForm.formWidget

    pmap = multi_line.multi_line(i,client)
    pmap = base64.b64decode(pmap)
    qimg = QImage.fromData(pmap)
    pixmap = QPixmap.fromImage(qimg)

    graphHeight = formWidget.grapharea.height()
    pixmap = pixmap.scaledToHeight(graphHeight)
    formWidget.grapharea.setPixmap(pixmap)

    change_level(formWidget.signalImage, 'signal',  powerlevel[i])
    change_level(formWidget.batteryImage, 'Battery',  batterylevel[i])

    formWidget.locationLabel.setText(formWidget.locations[i])

def file_changed(path):

    with open(path) as f:
        file_content = f.read().strip()

    if len(file_content) == 0:
        return

    global mainWindow
    formWidget = mainWindow.mainForm.formWidget

    if path.find('power') != -1:
        formWidget.powerBtn.setStyleSheet("color: white;"
                                          "font-size: 16px;"
                                          "background-color: " + file_content + ";")

    if path.find('alert') != -1:
        formWidget.alertBtn.setStyleSheet("color: white;"
                                          "font-size: 16px;"
                                          "background-color: " + file_content + ";")

    if path.find('water') != -1:
        formWidget.waterBtn.setStyleSheet("color: white;"
                                          "font-size: 16px;"
                                          "background-color: " + file_content + ";")

    if path.find('diagnostic') != -1:
        formWidget.diagnosticBtn.setStyleSheet("color: white;"
                                          "font-size: 16px;"
                                          "background-color: " + file_content + ";")

    if path.find('signal_strength') != -1:
        change_level(formWidget.signalImage, 'signal',  file_content)

    if path.find('battery_level') != -1:
        change_level(formWidget.batteryImage, 'Battery',  file_content)

TCP_IP = '127.0.0.1'
TCP_PORT = 2004
BUFFER_SIZE = 20  # Usually 1024, but we need quick response
# Multithreaded Python server : TCP Server Socket Thread Pool
class ClientThread(Thread):
    def __init__(self,conn,ip,port,client_list,server_key,filemng):
        Thread.__init__(self)
        self.conn = conn
        self.ip = ip
        self.port = port
        self.idenity = False
        self.client_list = client_list
        self.server_key = server_key
        self.filemng = filemng
        print( "[+] New server socket thread started for " + ip + ":" + str(port) )

    #initializes class for idenitfied client, find the key for the client, then handles basic tranmission.
    def run(self):
        while True :
            try:
                data = self.conn.recv(256)
                if(not self.idenity):
                    client = Identify(self.ip,self.port,self.server_key,self.filemng)
                    found = client.find_client_keys(data,self.client_list)

                    MESSAGE = ''
                    if(found):
                        MESSAGE = client.Encrypt(found.passphrase)
                        self.idenity = True
                        self.conn.send(MESSAGE)

                    else:
                        MESSAGE = 'Connection refused'
                        self.conn.send(MESSAGE.encode('utf-8'))
                        return
                else:
                   message = client.Decrypt(data)
                   if not message :
                       MESSAGE = 'Connection refused'
                       self.conn.send(MESSAGE.encode('utf-8'))  # echo
                       return
                   elif message == b'exit':
                       client.Save_log()
                       return
                   else:
                     client.Command(message)
                     print("here")
                     message = client.Encrypt(client.hash_last.encode('utf-8'))
                     self.conn.send(message)

            except :
                return

def socket_thread(client,filenmg,Server_Key):
    tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpServer.bind((TCP_IP, TCP_PORT))
    threads = []

    while True:
        tcpServer.listen(4)
        print( "Multithreaded Python server : Waiting for connections from TCP client..." )
        (conn, (ip,port)) = tcpServer.accept()
        newthread =  ClientThread(conn,ip,port,client_list,Server_Key,filenmg)
        newthread.start()
        threads.append(newthread)


if __name__ == '__main__':
    global mainWindow
    filenmg = Filemng("Server")
    filenmg.Set_Lock()
    try:
        client_list = filenmg.Load_Client_List()
        Server_Key = filenmg.Load_Server_Key()
    finally:
        filenmg.Release_Lock()

    _thread.start_new_thread(socket_thread,(client_list,filenmg,Server_Key,))
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    ## First show login form
    mainWindow = TopForm(QMainWindow,client_list= client_list )
    change_location(0,client_list)

    fs_watcher = QtCore.QFileSystemWatcher(check_list)
    fs_watcher.fileChanged.connect(lambda x: file_changed(x))

    sys.exit(app.exec_())

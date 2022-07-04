import sys, json
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QDialog
)
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtCore import QUrl, QSettings
from datetime import datetime
from PySide6.QtNetwork import QAbstractSocket

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("PC Client")
        self.setMinimumSize(400,200)

        self.client = QWebSocket()
        self.client.textMessageReceived.connect(self.onTextMessageReceived)
        self.client.error.connect(self.onError)
        self.client.connected.connect(self.onConnection)
        self.client.disconnected.connect(self.onDisconnection)
        self.settings = QSettings("fshangala", "PC Client")

        self.defaultAddress = "server.iitsar.com"
        self.defaultPort = "65432"
        self.defaultChromeDriver = "./chromedriver"

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Dashboard
        self.dashboard = QWidget()
        self.stack.addWidget(self.dashboard)
        self.dashboardLayout = QVBoxLayout()
        self.dashboard.setLayout(self.dashboardLayout)
        self.connectButton = QPushButton(text="Connect")
        self.connectButton.clicked.connect(self.openConnectionDialog)
        self.dashboardLayout.addWidget(self.connectButton)
        self.statusLabel = QLabel()
        self.dashboardLayout.addWidget(self.statusLabel)

        # Settings
        self.preferences = QWidget()
        self.stack.addWidget(self.preferences)
        self.preferencesLayout = QFormLayout()
        self.preferences.setLayout(self.preferencesLayout)
        self.addressInput = QLineEdit()
        self.addressInput.setText(self.settings.value("address",self.defaultAddress))
        self.preferencesLayout.addRow("Address",self.addressInput)
        self.portInput = QLineEdit()
        self.portInput.setText(self.settings.value("port",self.defaultPort))
        self.preferencesLayout.addRow("Port",self.portInput)
        self.chromeDriverInput = QLineEdit()
        self.chromeDriverInput.setText(self.settings.value("chromedriver",self.defaultChromeDriver))
        self.preferencesLayout.addRow("Chrome Driver Path",self.chromeDriverInput)
        self.saveButton = QPushButton(text="Save")
        self.saveButton.clicked.connect(self.savePreferences)
        self.preferencesLayout.addWidget(self.saveButton)

        # ToolBar
        self.menuBar().addAction("Dashboard").triggered.connect(lambda:self.stack.setCurrentIndex(0))
        self.menuBar().addAction("Preferences").triggered.connect(lambda:self.stack.setCurrentIndex(1))

    def savePreferences(self):
        address = self.addressInput.text()
        port = self.portInput.text()
        chromeDriver = self.chromeDriverInput.text()
        self.settings.setValue("address",address)
        self.settings.setValue("port",port)
        self.settings.setValue("chromedriver",chromeDriver)
        self.settings.sync()
        self.showStatus(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {address} {port} Saved!")
    
    def openConnectionDialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Open Connection")
        layout = QFormLayout(dlg)
        codeInput = QLineEdit()
        layout.addRow("Code",codeInput)
        connectButton = QPushButton(text="Connect")
        connectButton.clicked.connect(lambda: self.openConnection(codeInput.text()))
        connectButton.clicked.connect(dlg.accept)
        layout.addWidget(connectButton)

        dlg.show()

    def openConnection(self,code):

        host = "server.iitsar.com"
        port = 65432
        if code != "":
            if self.client.state() == QAbstractSocket.ConnectedState:
                self.showStatus("Closing current connection...")
                self.client.close()

            self.client.open(QUrl(f"ws://{host}:{port}/ws/pcautomation/{code}/"))
            self.showStatus("Connecting...")
        else:
            self.showStatus("Invalid code input!")
    
    def onConnection(self):
        self.showStatus("Connected!")
        ev = {
            "event_type":"connection",
            "event":"pc_connected",
            "args":[],
            "kwargs":{}
        }
        self.client.sendTextMessage(json.dumps(ev))
    
    def onDisconnection(self):
        self.showStatus("Disconnected!")
    
    def onError(self,obj):
        print(obj)
    
    def onTextMessageReceived(self,message:str):
        data = json.loads(message)
        status = f"{data['event_type']} -> {data['event']}"
        self.showStatus(status)
    
    def showStatus(self,message:str):
        self.statusLabel.setText(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
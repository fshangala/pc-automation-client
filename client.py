import sys, json, pyautogui, os
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
#from selenium.webdriver import Chrome
from PySide6.QtGui import QIcon
from PySide6.QtWebEngineWidgets import QWebEngineView
from latest_user_agents import get_latest_user_agents
from qt_material import apply_stylesheet

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.base_dir = os.path.dirname(__file__)
        
        self.setWindowTitle("PC Client")
        self.setMinimumSize(500,200)
        self.showMaximized()
        self.setWindowIcon(QIcon(self.base_dir + "/pcicon.ico"))

        #self.webdriver:Chrome = None
        self.userAgets = get_latest_user_agents()

        self.client = QWebSocket()
        self.client.textMessageReceived.connect(self.onTextMessageReceived)
        self.client.error.connect(self.onError)
        self.client.connected.connect(self.onConnection)
        self.client.disconnected.connect(self.onDisconnection)
        self.settings = QSettings("fshangala", "PC Client")

        self.defaultAddress = "server.iitsar.com"
        self.defaultPort = "65432"
        self.defaultChromeDriver = "./chromedriver"
        self.defaultTargetUrl = "https://google.com"

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
        #self.chromeDriverInput = QLineEdit()
        #self.chromeDriverInput.setText(self.settings.value("chromedriver",self.defaultChromeDriver))
        #self.preferencesLayout.addRow("Chrome Driver Path",self.chromeDriverInput)
        #self.chromeDriverBrowse = QPushButton(text="Browse")
        #self.chromeDriverBrowse.clicked.connect(self.browseChromeDriver)
        #self.preferencesLayout.addRow(self.chromeDriverBrowse)
        self.targetUrl = QLineEdit()
        self.targetUrl.setText(self.settings.value("targeturl",self.defaultTargetUrl))
        self.preferencesLayout.addRow("Target URL",self.targetUrl)
        self.saveButton = QPushButton(text="Save")
        self.saveButton.clicked.connect(self.savePreferences)
        self.preferencesLayout.addWidget(self.saveButton)

        # Browser
        self.browser = QWebEngineView()
        self.browser.page().profile().setHttpUserAgent(self.userAgets[0])
        self.browser.loadStarted.connect(lambda: self.statusBar().showMessage("Browser: Loading..."))
        self.browser.loadFinished.connect(lambda: self.statusBar().showMessage("Browser: Page Loaded!"))
        self.stack.addWidget(self.browser)
        self.loadBrowserPage()

        # ToolBar
        self.menuBar().addAction("Dashboard").triggered.connect(lambda:self.stack.setCurrentIndex(0))
        self.menuBar().addAction("Preferences").triggered.connect(lambda:self.stack.setCurrentIndex(1))
        self.menuBar().addAction("Browser").triggered.connect(lambda:self.stack.setCurrentIndex(2))

    def savePreferences(self):
        address = self.addressInput.text()
        port = self.portInput.text()
        #chromeDriver = self.chromeDriverInput.text()
        targeturl = self.targetUrl.text()
        reloadBrowser = targeturl != self.settings.value("targeturl",self.defaultTargetUrl)
        self.settings.setValue("address",address)
        self.settings.setValue("port",port)
        #self.settings.setValue("chromedriver",chromeDriver)
        self.settings.setValue("targeturl",targeturl)
        self.settings.sync()
        self.showStatus(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {address} {port} Saved!")
        if(reloadBrowser):
            self.loadBrowserPage()
        self.stack.setCurrentIndex(0)
    
    #def browseChromeDriver(self):
    #    fpath, _ = QFileDialog.getOpenFileName(self,"Select Chrome Driver")
    #    self.chromeDriverInput.setText(fpath)
    
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

    def loadBrowserPage(self):
        self.browser.load(self.settings.value("targeturl",self.defaultTargetUrl))
    
    #def startWebdriver(self):
    #    if self.webdriver == None:
    #        chromedriver = self.settings.value("chromedriver",self.defaultChromeDriver)
    #        if os.path.exists(chromedriver):
    #            self.webdriver = Chrome(chromedriver)
    #        else:
    #            self.stack.setCurrentIndex(1)
    #            return None
    #    try:
    #        self.webdriver.get(self.settings.value("targeturl",self.defaultTargetUrl))
    #    except Exception as e:
    #        chromedriver = self.settings.value("chromedriver",self.defaultChromeDriver)
    #        if os.path.exists(chromedriver):
    #            self.webdriver = Chrome(chromedriver)
    #        else:
    #            self.stack.setCurrentIndex(1)
    #            return None
    #        
    #        try:
    #            self.webdriver.get(self.settings.value("targeturl",self.defaultTargetUrl))
    #        except Exception as e:
    #            self.showStatus(str(e))

    def openConnection(self,code):

        host = self.settings.value("address",self.defaultAddress)
        port = self.settings.value("port",self.defaultPort)
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
        self.stack.setCurrentIndex(2)
    
    def onDisconnection(self):
        self.showStatus("Disconnected!")
    
    def onError(self,obj):
        print(obj)
    
    def onTextMessageReceived(self,message:str):
        data = json.loads(message)
        status = f"{data['event_type']} -> {data['event']}"
        self.showStatus(status)
        handle = f"event_{data['event_type']}"
        if hasattr(self,handle) and callable(func := getattr(self,handle)):
            func(data["event"],*data["args"],**data["kwargs"])
    
    def showStatus(self,message:str):
        #self.statusBar().showMessage(message)
        self.statusLabel.setText(message)
    
    def sendLoggedInUser(self,returnValue):
        ev = {
            "event_type":"user",
            "event":"loggedIn",
            "args":[returnValue],
            "kwargs":{}
        }
        self.client.sendTextMessage(json.dumps(ev))
        print(ev)
    
    def getLoggedInUser(self):
        #document.querySelectorAll("div.infobar ul.linkbar li")[2].innerText
        self.browser.page().runJavaScript("document.querySelectorAll(\"div.infobar ul.linkbar li\")[2].innerText", self.sendLoggedInUser)
    
    # events
    def event_mouse(self,event,*args,**kwargs):
        if event == "click":
            pyautogui.click()
        
        self.getLoggedInUser()
    
    #def event_webdriver(self,event,*args,**kwargs):
    #    if event == "close":
    #        self.webdriver.close()

    def event_connection(self,event,*args,**kwargs):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_cyan.xml')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
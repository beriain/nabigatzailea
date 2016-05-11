import sys, os
from PyQt5 import uic, QtGui, QtWidgets, QtCore, QtWebKit, QtWebKitWidgets
from urllib.parse import urlparse

form_class, base_class = uic.loadUiType("nabigatzailea.ui")

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = form_class()
        self.ui.setupUi(self)
        
        #javascript gaitu/ezgaitu
        #s = QtWebKit.QWebSettings.globalSettings()
        #s.setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, False)

        #webview huts bat gehitu fitxa batean
        contents = QtWidgets.QWidget(self.ui.tabWidget)
        layout = QtWidgets.QVBoxLayout(contents)
        layout.setContentsMargins(0,0,0,0)
        web = Nabigatzailea()
        layout.addWidget(web)
        self.ui.tabWidget.addTab(contents, "-")
        self.ui.tabWidget.tabBar().tabButton(0, QtWidgets.QTabBar.RightSide).resize(0,0)
        self.ui.tabWidget.setCurrentIndex(1)

        #seinaleak funtzioetara lotu
        self.ui.lineEdit.returnPressed.connect(lambda: self.kargatu(web))
        web.urlChanged.connect(self.urlEguneratu)
        web.loadProgress.connect(self.kargatzen)
        self.ui.tabWidget.tabCloseRequested.connect(self.fitxaItxi)
        self.ui.tabWidget.currentChanged.connect(self.fitxaAldatuta)

    def kargatu(self, web):
        url = self.ui.lineEdit.text()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        web.load(QtCore.QUrl(url))

    def urlEguneratu(self, url):
        self.ui.lineEdit.setText(url.toString())
        o = urlparse(url.toString())
        self.ui.tabWidget.setTabText(0, o.netloc)
        #print(self.ui.webView.title()) hutsik agertzen da

    def fitxaAldatuta(self):
        widgets = self.ui.tabWidget.currentWidget().findChildren(QtWebKitWidgets.QWebView)
        self.ui.lineEdit.setText(widgets[0].url().toString())

    def kargatzen(self, p):
	    self.ui.progressBar.setValue(p)

    def fitxaItxi(self, f):
        if self.ui.tabWidget.count() > 2:
            self.ui.tabWidget.removeTab(f)

class Nabigatzailea(QtWebKitWidgets.QWebView):
    def __init__(self):
        super(QtWebKitWidgets.QWebView, self).__init__()

        self.setPage(WebPage())

    #eskuineko botoiaren menua
    def contextMenuEvent(self, event):
        pos = event.pos()
        element = self.page().mainFrame().hitTestContent(pos)
        url = str(element.linkUrl().toString())
        menu = self.page().createStandardContextMenu()
        action = menu.exec_(event.globalPos())
        if action.text() == "Open in New Window":
            self.fitxaBerrianIreki(url)

    #eskuineko botoiarekin fitxa berrian ireki
    def fitxaBerrianIreki(self, url):
        contents = QtWidgets.QWidget(self.window().ui.tabWidget)
        layout = QtWidgets.QVBoxLayout(contents)
        layout.setContentsMargins(0,0,0,0)
        web = Nabigatzailea()
        web.load(QtCore.QUrl(url))
        layout.addWidget(web)
        self.window().ui.tabWidget.addTab(contents, urlparse(url).netloc)

class WebPage(QtWebKitWidgets.QWebPage):
    def userAgentForUrl(self, url):
        return "Mozilla/5.0 (Windows NT 6.1; rv:46.0) Gecko/20100101 Firefox/46.0"

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())

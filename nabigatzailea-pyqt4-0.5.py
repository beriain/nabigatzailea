import sys, os
from PyQt4 import uic, QtGui, QtCore, QtWebKit
from urllib.parse import urlparse

form_class, base_class = uic.loadUiType("nabigatzailea-0.5.ui")

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = form_class()
        self.ui.setupUi(self)

        #webview huts bat gehitu fitxa batean
        contents = QtGui.QWidget(self.ui.tabWidget)
        layout = QtGui.QVBoxLayout(contents)
        layout.setContentsMargins(0,0,0,0)
        web = Nabigatzailea()
        layout.addWidget(web)
        self.ui.tabWidget.addTab(contents, "-")

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
        widgets = self.ui.tabWidget.currentWidget().findChildren(QtWebKit.QWebView)
        self.ui.lineEdit.setText(widgets[0].url().toString())

    def kargatzen(self, p):
	    self.ui.progressBar.setValue(p)

    def fitxaItxi(self, f):
        if self.ui.tabWidget.count() > 1:
            self.ui.tabWidget.removeTab(f)

class Nabigatzailea(QtWebKit.QWebView):
    def __init__(self):
        super(QtWebKit.QWebView, self).__init__()

        self.setPage(WebPage())

    #eskuineko botoiarekin fitxa berrian ireki
    def contextMenuEvent(self, event):
        menu = self.page().createStandardContextMenu()
        menu.exec_(event.globalPos())
        pos = event.pos()
        element = self.page().mainFrame().hitTestContent(pos)
        url = str(element.linkUrl().toString())
        #print(url)
        contents = QtGui.QWidget(self.window().ui.tabWidget)
        layout = QtGui.QVBoxLayout(contents)
        layout.setContentsMargins(0,0,0,0)
        web = Nabigatzailea()
        web.load(QtCore.QUrl(url))
        layout.addWidget(web)
        self.window().ui.tabWidget.addTab(contents, urlparse(url).netloc)

class WebPage(QtWebKit.QWebPage):
    def userAgentForUrl(self, url):
        return "Mozilla/5.0 (Windows NT 6.1; rv:46.0) Gecko/20100101 Firefox/46.0"

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())
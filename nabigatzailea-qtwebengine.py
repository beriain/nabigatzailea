import sys, os, urllib.request, ntpath
from PyQt5 import uic, QtGui, QtWidgets, QtCore, QtWebEngineWidgets
from urllib.parse import urlparse

form_class, base_class = uic.loadUiType("nabigatzailea.ui")

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = form_class()
        self.ui.setupUi(self)
        
        ## Ezarpenak gaitu/ezgaitu
        #s = QtWebEngineWidgets.QWebEngineSettings.globalSettings()
        #s.setAttribute(QtWebEngineWidgets.QWebEngineSettings.JavascriptEnabled, False)
        ##s.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PrivateBrowsingEnabled, True)
        #s.setAttribute(QtWebEngineWidgets.QWebEngineSettings.XSSAuditingEnabled, True)
        #s.setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalStorageEnabled, True)
        #s.setAttribute(QtWebEngineWidgets.QWebEngineSettings.JavascriptCanAccessClipboard, False)
        #s.setAttribute(QtWebEngineWidgets.QWebEngineSettings.JavascriptCanOpenWindows, False)
        #s.setAttribute(QtWebEngineWidgets.QWebEngineSettings.ScrollAnimatorEnabled, True)
        #s.setAttribute(QtWebEngineWidgets.QWebEngineSettings.HyperlinkAuditingEnabled, True)
        #s.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, False)

        #webview huts bat gehitu fitxa batean
        contents = QtWidgets.QWidget(self.ui.tabWidget)
        layout = QtWidgets.QVBoxLayout(contents)
        layout.setContentsMargins(0,0,0,0)
        #nabigatzaile berri bat sortzerakoan, fitxa berri bat den zehaztu
        web = Nabigatzailea(False)
        layout.addWidget(web)
        self.ui.tabWidget.addTab(contents, "-")
        self.ui.tabWidget.tabBar().tabButton(0, QtWidgets.QTabBar.RightSide).resize(0,0)
        self.ui.tabWidget.setCurrentIndex(1)

        #seinaleak funtzioetara lotu
        self.ui.lineEdit.returnPressed.connect(lambda: self.kargatu(web))
        self.ui.tabWidget.tabCloseRequested.connect(self.fitxaItxi)
        self.ui.tabWidget.currentChanged.connect(self.fitxaAldatuta)

    def kargatu(self, web):
        url = self.ui.lineEdit.text()
        if not url.startswith("http://") and not url.startswith("https://") and not url.startswith("file:///"):
            url = "http://" + url
        self.ui.tabWidget.currentWidget().findChildren(QtWebEngineWidgets.QWebEngineView)[0].load(QtCore.QUrl(url))
        o = urlparse(url)
        self.ui.tabWidget.setTabText(self.window().ui.tabWidget.currentIndex(), o.netloc)

    def fitxaAldatuta(self):
        if self.ui.tabWidget.currentIndex() != 0:
            widgets = self.ui.tabWidget.currentWidget().findChildren(QtWebEngineWidgets.QWebEngineView)
            if not widgets[0].url().toString().startswith("http://") and not widgets[0].url().toString().startswith("https://"):
                self.ui.lineEdit.setText("http://")
            else:
                self.ui.lineEdit.setText(widgets[0].url().toString())
        else:
            contents = QtWidgets.QWidget(self.window().ui.tabWidget)
            layout = QtWidgets.QVBoxLayout(contents)
            layout.setContentsMargins(0,0,0,0)
            #nabigatzaile berri bat sortzerakoan, fitxa berri bat den zehaztu
            web = Nabigatzailea(True)
            layout.addWidget(web)
            self.ui.tabWidget.addTab(contents, "-")
            self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count()-1)

    def fitxaItxi(self, f):
        if self.ui.tabWidget.count() > 2:
            self.ui.tabWidget.removeTab(f)

class Nabigatzailea(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, fitxa):
        super(QtWebEngineWidgets.QWebEngineView, self).__init__()
        #nabigatzaile berri bat sortzerakoan, fitxa berri bat den zehaztu
        self.fitxaberria = fitxa

        self.setPage(WebPage())

        self.urlChanged.connect(self.urlEguneratu)
        self.loadProgress.connect(self.kargatzen)

    #eskuineko botoiaren menua
    def contextMenuEvent(self, event):
        pos = event.pos()
        element = self.page().mainFrame().hitTestContent(pos)
        url = element.linkUrl().toString()
        image = element.imageUrl().toString()
        menu = self.page().createStandardContextMenu()
        action = menu.exec_(event.globalPos())
        try:
            if action.text() == "Open in New Window":
                self.fitxaBerrianIreki(url)
            if action.text() == "Save Link...":
                f, ext = os.path.splitext(url)
                if ext != "":
                    p = QtWidgets.QFileDialog.getSaveFileName(self, "Fitxategia gorde",
                        ntpath.basename(url), "(*" + ext +")")
                    if p[0] != "":
                        urllib.request.urlretrieve(url, p[0])
            if action.text() == "Save Image":
                f, ext = os.path.splitext(image)
                p = QtWidgets.QFileDialog.getSaveFileName(self, "Irudia gorde",
                    ntpath.basename(image), "(*" + ext +")")
                if p[0] != "":
                    urllib.request.urlretrieve(image, p[0])
        except AttributeError:
            None

    #eskuineko botoiarekin fitxa berrian ireki
    def fitxaBerrianIreki(self, url):
        contents = QtWidgets.QWidget(self.window().ui.tabWidget)
        layout = QtWidgets.QVBoxLayout(contents)
        layout.setContentsMargins(0,0,0,0)
        #nabigatzaile berri bat sortzerakoan, fitxa berri bat den zehaztu
        web = Nabigatzailea(True)
        web.load(QtCore.QUrl(url))
        layout.addWidget(web)
        self.window().ui.tabWidget.addTab(contents, urlparse(url).netloc)

    def urlEguneratu(self, url):
        if not self.fitxaberria:
            self.window().ui.lineEdit.setText(url.toString())
            o = urlparse(url.toString())
            self.window().ui.tabWidget.setTabText(self.window().ui.tabWidget.currentIndex(), o.netloc)
        self.fitxaberria = False

    def kargatzen(self, p):
        #arrazoi ezezagun bategatik, p 10 baino txikiagoa denean self ez da
        #lehio nagusia, nabigatzaile klasea baizik. p 10 baino gehiago denean
        #konpontzen da. Aztertu behar da
        if p > 10:
            self.window().ui.progressBar.setValue(p)

class WebPage(QtWebEngineWidgets.QWebEnginePage):
    def userAgentForUrl(self, url):
        return "Mozilla/5.0 (Windows NT 6.1; rv:54.0) Gecko/20100101 Firefox/54.0"

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())

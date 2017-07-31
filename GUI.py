from PyQt5 import QtCore, QtGui, QtWidgets
# TODO импортируй свои функции скана векторов и распознования изображения вместо моих
#from libImage import calculate_samples, do_all
import main
import Comparison

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(201, 186)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.file_btn = QtWidgets.QPushButton(self.centralwidget)
        self.file_btn.setObjectName("file_btn")
        self.gridLayout.addWidget(self.file_btn, 0, 1, 1, 1)
        self.img = QtWidgets.QLabel(self.centralwidget)
        self.img.setText("")
        self.img.setAlignment(QtCore.Qt.AlignCenter)
        self.img.setObjectName("img")
        self.gridLayout.addWidget(self.img, 1, 0, 1, 2)
        self.start_btn = QtWidgets.QPushButton(self.centralwidget)
        self.start_btn.setEnabled(False)
        self.start_btn.setObjectName("start_btn")
        self.gridLayout.addWidget(self.start_btn, 2, 0, 1, 1)
        self.filename = QtWidgets.QLabel(self.centralwidget)
        self.filename.setObjectName("filename")
        self.gridLayout.addWidget(self.filename, 0, 0, 1, 1)
        self.progress = QtWidgets.QProgressBar(self.centralwidget)
        self.progress.setEnabled(False)
        self.progress.setProperty("value", 0)
        self.progress.setObjectName("progress")
        self.gridLayout.addWidget(self.progress, 3, 0, 1, 2)
        self.upd_btn = QtWidgets.QPushButton(self.centralwidget)
        self.upd_btn.setObjectName("upd_btn")
        self.gridLayout.addWidget(self.upd_btn, 2, 1, 1, 1)
        self.output = QtWidgets.QLineEdit(self.centralwidget)
        self.output.setReadOnly(True)
        self.output.setObjectName("output")
        self.gridLayout.addWidget(self.output, 4, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Распознаватель изображений"))
        self.file_btn.setText(_translate("MainWindow", "Обзор"))
        self.start_btn.setText(_translate("MainWindow", "Начать"))
        self.filename.setText(_translate("MainWindow", "Выберите файл"))
        self.upd_btn.setText(_translate("MainWindow", "Обновить"))


class Ui(Ui_MainWindow, QtWidgets.QMainWindow):
    sigset = QtCore.pyqtSignal(int, str)
    sigout = QtCore.pyqtSignal(str)
    sigsav = QtCore.pyqtSignal(dict)
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.sample_vectors = {}

        self.sigset.connect(self.set_st)

        self.sigout.connect(self.set_out)

        self.sigsav.connect(self.set_sav)

        self.file_btn.clicked.connect(self.file_select)
        self.start_btn.clicked.connect(self.start_processing)
        self.upd_btn.clicked.connect(self.scan)

        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.show()

        self.scan(norescan=True)
        self.statusbar.showMessage("Готов")

    def file_select(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Выбрать файл", "/", "Изображение (*.png *.jpg)")[0]
        self.progress.setValue(0)
        if file == "":
            self.start_btn.setEnabled(False)
            self.img.setPixmap(QtGui.QPixmap())
            self.filename.setText("Выберите файл")
        else:
            self.start_btn.setEnabled(True)
            pixmap = QtGui.QPixmap(file)
            pixmap = pixmap.scaled(int((pixmap.width() / pixmap.height()) * 250), 250)
            print(type(pixmap))
            self.img.setPixmap(pixmap)
            self.filename.setText(file)
            self.start_btn.setEnabled(True)

    def start_processing(self):
        self.start_enabled = self.start_btn.isEnabled()
        self.progress.setValue(0)
        self.file_btn.setEnabled(False)
        self.upd_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        filename = self.filename.text()
        self.progress.setEnabled(True)
        self.thrp = thread_proess(filename, self.sigset, self.sigout, self.sample_vectors)
        self.thrp.finished.connect(self.unlock)
        self.thrp.start()

    def scan(self, norescan=True):
        self.file_btn.setEnabled(False)
        self.upd_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.progress.setEnabled(True)
        self.progress.setValue(0)
        self.start_enabled = self.start_btn.isEnabled()
        self.thrs = thread_scan(self.sigset, self.sigsav, not norescan)
        self.thrs.finished.connect(self.unlock)
        self.thrs.start()

    def set_sav(self, sav):
        self.sample_vectors = sav

    def set_st(self, progress, stat):
        self.progress.setValue(int(progress))
        self.statusbar.showMessage(stat)

    def set_out(self, text):
        self.output.setText(text)

    def unlock(self):
        self.file_btn.setEnabled(True)
        self.start_btn.setEnabled(self.start_enabled)
        self.upd_btn.setEnabled(True)
        self.progress.setEnabled(False)
        self.statusbar.showMessage("Готов")


class thread_proess(QtCore.QThread):
    def __init__(self, filename, sigset, sigout, sample_vectors):
        QtCore.QThread.__init__(self)
        self.filename = str(filename)
        self.sigset = sigset
        self.sigout = sigout
        self.sample_vectors = sample_vectors


    def run(self):
        # TODO здесь твоя функция распознавания изображения
        vector = main.processImage(self.filename)
        self.sigset.emit(0, "Распознавание")
        result = Comparison.compareWithReferences(vector, self.sample_vectors)
        self.sigout.emit(result)
        #do_all(self.filename, self.sigset, self.sigout, self.sample_vectors)


class thread_scan(QtCore.QThread):
    def __init__(self, sigset, sigsav, rescan):
        QtCore.QThread.__init__(self)
        self.sigset = sigset
        self.rescan = rescan
        self.sigsav = sigsav


    def run(self):
        main.calculateSamples(self.sigset, self.sigsav, self.rescan)
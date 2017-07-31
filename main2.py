import sys
from PyQt5.QtWidgets import QApplication
from GUI import Ui


app = QApplication(sys.argv)
gui = Ui()
sys.exit(app.exec_())

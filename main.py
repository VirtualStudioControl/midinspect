from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

from midinspect.ui.MainWindow import MainWindow

import sys

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        app.setStyle('Fusion')

        try:
            window.show()
            app.exec_()
        finally:
            window.cleanup()

    except Exception as ex:
        print("UNHANDLED Exception Occured !", ex.__traceback__())
#endregion
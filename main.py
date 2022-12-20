import sys

from PyQt6.QtWidgets import QApplication

from app_widgets import *

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = AuthorizationWindow()
    window.show()

    app.exec()

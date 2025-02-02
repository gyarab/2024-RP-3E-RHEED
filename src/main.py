from qtpy.QtWidgets import QApplication
from GUI.rheed import Rheed

if __name__ == "__main__":
    app = QApplication([])
    window = Rheed()
    window.show()
    app.exec_()
    app.quitOnLastWindowClosed(1)
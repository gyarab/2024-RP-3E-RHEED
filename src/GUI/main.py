from qtpy.QtWidgets import QApplication
from rheed import Rheed

if __name__ == "__main__":
    app = QApplication([])
    window = Rheed()
    window.show()
    app.exec_()
    

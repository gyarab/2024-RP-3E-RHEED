from qtpy.QtWidgets import QApplication
import gui.plotROIStats as plotROIStats
import sys

if __name__ == "__main__":
    #app = QApplication([])
    #window = Rheed()
    #window.show()
    #app.exec_()
    #app.quitOnLastWindowClosed(1)
    plotROIStats.main(sys.argv)

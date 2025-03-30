import sys
import numpy as np
from silx.gui import qt
from silx.gui.plot import StackView, Plot2D
from silx.gui.plot.ROIStatsWidget import ROIStatsWidget
from silx.gui.plot.tools.roi import RegionOfInterestTableWidget
from silx.gui.plot.tools.roi import RegionOfInterestManager, RegionOfInterest, RoiModeSelectorAction

class App(qt.QMainWindow):
    def __init__(self):
        super().__init__()

        # Generate sample stack
        self.stack = np.random.rand(10, 300, 400).astype(np.float32)

        # StackView shown to user
        self.stackView = StackView()
        self.stackView.setStack(self.stack)

        # Hidden Plot2D (for stats only)
        self.hiddenPlot = Plot2D()
        self.hiddenPlot.hide()  # Keep it completely hidden

        # Stats widget bound to hidden plot
        self.statsWidget = ROIStatsWidget(plot=self.hiddenPlot)
        self.statsWidget.setStats([("mean", np.mean)])
        self.statsWidget._setUpdateMode("auto")

        # ROI manager shown in StackView plot
        self.roiManager = RegionOfInterestManager(parent=self.stackView.getPlotWidget())
        self.roiManager.sigRoiAdded.connect(self.on_roi_added)
        self.roiTable = RegionOfInterestTableWidget()
        self.roiTable.setRegionOfInterestManager(self.roiManager)

        self.roiToolbar = qt.QToolBar()
        self.roiToolbar.setIconSize(qt.QSize(16, 16))

        for roiClass in self.roiManager.getSupportedRoiClasses():
        # Create a tool button and associate it with the QAction of each mode
            self.roiToolbar.addAction(self.roiManager.getInteractionModeAction(roiClass))

        modeSelectorAction = RoiModeSelectorAction()
        modeSelectorAction.setRoiManager(self.roiManager)

        # Layout
        central = qt.QWidget()
        layout = qt.QVBoxLayout(central)
        layout.addWidget(self.stackView)
        layout.addWidget(self.statsWidget)
        layout.addWidget(self.roiToolbar)
        layout.addWidget(self.roiTable)
        self.setCentralWidget(central)

        # Initial image to hidden plot
        self.stackView.sigFrameChanged.connect(self.update_hidden_plot)
        self.update_hidden_plot(self.stackView.getFrameNumber())

    def update_hidden_plot(self, index):
        print(f"Frame changed: {index}")
        """Copy current frame to hidden Plot2D"""
        frame = self.stack[self.stackView.getFrameNumber()]
        print(frame)
        self.hiddenPlot.clear()
        self.hiddenPlot.addImage(frame, legend="analysis_frame")
        self.hiddenPlot.hide()
        self.statsWidget._updateAllStats()

        # Rebind all ROIs to new image)
        #image = self.hiddenPlot
        #for roi in self.roiManager.getRois():
        #    self.statsWidget.addItem(roi=roi, plotItem=image)
        #    self.statsWidget._updateAllStats()

    def on_roi_added(self, roi):
        """When ROI is added, bind it to hidden plot image"""
        print(f"ROI added: {roi.getName()}")
        self.statsWidget.registerROI(roi)
        #image = self.hiddenPlot.getImage("analysis_frame")
        #if image is not None:
        #    self.statsWidget.addItem(roi=roi, plotItem=image)
        #else:
        #    print("⚠️ No image in hidden plot")

if __name__ == "__main__":
    app = qt.QApplication(sys.argv)
    win = App()
    win.resize(800, 600)
    win.show()
    sys.exit(app.exec())

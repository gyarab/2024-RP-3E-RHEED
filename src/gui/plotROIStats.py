#timeframe of plotting is better is from origin of capture
#in time series add a feature of viewing and unviewing the curves and time plots of the images
#how to save locations of ROIs? easy solution
from silx.gui import qt
from silx.gui.plot.tools.roi import RegionOfInterestManager
from silx.gui.plot.tools.roi import RegionOfInterestTableWidget
from silx.gui.plot import Plot2D
from silx.gui.plot.ROIStatsWidget import ROIStatsWidget
from silx.gui.plot.StatsWidget import UpdateModeWidget
import sys
from silx.gui import qt
from silx.gui.plot import Plot2D
from silx.gui.plot.StackView import StackView
from silx.gui.plot.tools.roi import RegionOfInterestManager
from silx.gui.plot.tools.roi import RegionOfInterestTableWidget
from silx.gui.plot.tools.roi import RoiModeSelectorAction
from silx.gui.plot.ROIStatsWidget import ROIStatsWidget
from silx.gui.plot.StatsWidget import UpdateModeWidget
import argparse
import functools
import numpy
import concurrent.futures
import threading
from silx.gui.utils import concurrent
import time
from camera.opencv_capture import CameraInit
from gui.roiwidget import roiManagerWidget
from gui.statswindow import roiStatsWindow

class plotUpdateThread(qt.QThread):
    """Thread updating the stack in the stack view.`

    :param plot2d: The StackView to update."""

    """Signal to emit when the data is resized"""
    dataResized = qt.Signal(object, object)

    def __init__(self, window):
        self.window = window
        self.plot = window.plot
        self.plot2d = self.plot.getPlotWidget()
        self.running = False
        super(plotUpdateThread, self).__init__()
        self.camera = CameraInit(720, 1280, 100)
        self.camera.on_resize = lambda new_dataset: self.dataResized.emit(self.plot, new_dataset)
        self.dataResized.connect(self.update_dataset)


    def start(self):
        """Start the update thread"""
        self.running = True
        super(plotUpdateThread, self).start()
        concurrent.submitToQtMainThread(self.plot.setStack, self.camera.image_dataset)

    def run(self):
        """Method implementing thread loop that updates the plot"""
        while self.running:
            self.camera.capture_frame()
            time.sleep((self.camera.getFPS())/1000)
            #_framenum = self.plot2d.getFrameNumber()
            #self.plot2d.setFrameNumber(_framenum)
            #if frame is not None:
            #    concurrent.submitToQtMainThread(self.plot2d, frame, legend="opencv_capture")

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
    
    def update_dataset(self, plot, dataset):
        """Update the plot with the new dataset"""
        framenum = plot.getFrameNumber()
        plot.setStack(dataset)
        plot.setFrameNumber(framenum)

class _RoiStatsDisplayExWindow(qt.QMainWindow):
    """
    Simple window to group the different statistics actors
    """

    def __init__(self, parent=None, mode=None):
        qt.QMainWindow.__init__(self, parent)
        self.plot = StackView(parent=self, backend="gl")
        self.setCentralWidget(self.plot)

        # hidden plot2D for stats
        self._hiddenPlot2D = Plot2D()  # not added to layout
        self._hiddenPlot2D.hide()

        # widget for displaying stats results and update mode
        self._statsWidget = roiStatsWindow(parent=self, plot=self._hiddenPlot2D, stackview=self.plot)
        self.plot.sigFrameChanged.connect(self._update_hidden_plot)

        self.plot.sigFrameChanged.connect(self._statsWidget.updateTimeseriesAsync)

        # 1D roi management
        self._curveRoiWidget = self.plot.getPlotWidget().getCurvesRoiDockWidget()
        # hide last columns which are of no use now
        #for index in (5, 6, 7, 8):
        #self._curveRoiWidget.roiTable.setColumnHidden(index, True)

        # 2D - 3D roi manager
        self._regionManagerWidget = roiManagerWidget(parent=self, plot=self.plot.getPlotWidget())
        
        # tabWidget for displaying the rois
        self._roisTabWidget = qt.QTabWidget(parent=self)
        #if hasattr(self._roisTabWidget, "setTabBarAutoHide"):
        #    self._roisTabWidget.setTabBarAutoHide(True)

        # create Dock widgets
        self._roisTabWidgetDockWidget = qt.QDockWidget(parent=self)
        self._roisTabWidgetDockWidget.setWidget(self._roisTabWidget)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._roisTabWidgetDockWidget)

        # create Dock widgets
        self._roiStatsWindowDockWidget = qt.QDockWidget(parent=self)
        self._roiStatsWindowDockWidget.setWidget(self._statsWidget)
        # move the docker contain in the parent widget
        #self.addDockWidget(qt.Qt.RightDockWidgetArea, self._statsWidget._docker)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._roiStatsWindowDockWidget)

        # Connect ROI signal to register ROI automatically
        self._regionManagerWidget.roiManager.sigRoiAdded.connect(self.onRoiAdded)
        self._regionManagerWidget.roiManager.sigRoiAboutToBeRemoved.connect(self._statsWidget.unregisterRoi)

        self._roisTabWidget.addTab(self._regionManagerWidget, "2D roi(s)")
        self._roisTabWidget.addTab(self._curveRoiWidget, "1D roi(s)")

    def onRoiAdded(self, roi):
        self._statsWidget.registerRoi(roi)
        image = self._hiddenPlot2D.addImage(self.plot._stack[self.plot.getFrameNumber()])
        if image is not None:
            print(image)
            self._statsWidget.addItem(roi=roi, item=image)
            self._statsWidget.statsWidget._updateAllStats()

    def _update_hidden_plot(self, index):
        #print(self.plot.getStack())
        self._hiddenPlot2D.addImage(self.plot._stack[self.plot.getFrameNumber()])
        #frame = self.plot._plot.getAllImages()[index]
        #if frame is not None:
        #    self._hiddenPlot2D.clear()
        #    self._hiddenPlot2D.addImage(frame, legend="analysis_frame")
        self._statsWidget.statsWidget._updateAllStats()

def example_image(mode):
    """set up the roi stats example for images"""
    app = qt.QApplication([])
    window = _RoiStatsDisplayExWindow()
    updateThread = plotUpdateThread(window)
    updateThread.start()
    window.show()
    window.plot.setKeepDataAspectRatio(True)
    window.plot.setYAxisInverted(True)
    app.exec()
    updateThread.stop()

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--items",
        dest="items",
        default="curves+images",
        help="items type(s), can be curve, image, curves+images",
    )
    parser.add_argument(
        "--mode", dest="mode", default="manual", help="valid modes are `auto` or `manual`"
    )
    options = parser.parse_args(argv[1:])

    items = options.items.lower()
    if items == "curves+images":  
        example_image(mode=options.mode)
    else:
        raise ValueError("invalid entry for item type")
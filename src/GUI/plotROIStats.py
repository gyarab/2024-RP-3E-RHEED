#timeframe of plotting is better is from origin of capture
#in time series add a feature of viewing and unviewing the curves and time plots of the images
#how to save locations of ROIs? easy solution

from silx.gui import qt
from silx.gui.plot.tools.roi import RegionOfInterestManager
from silx.gui.plot.tools.roi import RegionOfInterestTableWidget
from silx.gui.plot.items.roi import RectangleROI, PolygonROI, ArcROI
from silx.gui.plot import Plot2D
from silx.gui.plot.CurvesROIWidget import ROI
from silx.gui.plot.ROIStatsWidget import ROIStatsWidget
from silx.gui.plot.StatsWidget import UpdateModeWidget
import sys
from silx.gui import qt
from silx.gui.plot import Plot2D
from silx.gui.plot.tools.roi import RegionOfInterestManager
from silx.gui.plot.tools.roi import RegionOfInterestTableWidget
from silx.gui.plot.tools.roi import RoiModeSelectorAction
from silx.gui.plot.items.roi import RectangleROI
from silx.gui.plot.items import LineMixIn, SymbolMixIn
from silx.gui.plot.actions import control as control_actions
from silx.gui.plot.ROIStatsWidget import ROIStatsWidget
from silx.gui.plot.StatsWidget import UpdateModeWidget
import argparse
import functools
import numpy
import threading
from silx.gui.utils import concurrent
import random
import time
import src.camera.opencv_capture as camera

class UpdateThread(threading.Thread):
    """Thread updating the image of a :class:`~silx.gui.plot.Plot2D`

    :param plot2d: The Plot2D to update."""

    def __init__(self, plot2d):
        self.plot2d = plot2d
        self.running = False
        super(UpdateThread, self).__init__()
        camera.CameraInit(100, 100, 10000)

    def start(self):
        """Start the update thread"""
        self.running = True
        super(UpdateThread, self).start()

    def run(self):
        """Method implementing thread loop that updates the plot"""
        while self.running:
            time.sleep(1)
            # Run plot update asynchronously
            concurrent.submitToQtMainThread(
                self.plot2d.addImage,
                camera.CameraInit(100, 100, 10000).image_dataset[0],
                legend="opencv_capture",
                #only sample noise below, used for initial testing
                #numpy.random.random(10000).reshape(100, 100),
                #resetzoom=False,
                #legend=random.choice(("img1", "img2")),
            )

    def stop(self):
        """Stop the update thread"""
        self.running = False
        self.join(2)


class _RoiStatsWidget(qt.QMainWindow):
    """
    Window used to associate ROIStatsWidget and UpdateModeWidget
    """

    def __init__(self, parent=None, plot=None, mode=None):
        assert plot is not None
        qt.QMainWindow.__init__(self, parent)
        self._roiStatsWindow = ROIStatsWidget(plot=plot)
        self.setCentralWidget(self._roiStatsWindow)

        # update mode docker
        self._updateModeControl = UpdateModeWidget(parent=self)
        self._docker = qt.QDockWidget(parent=self)
        self._docker.setWidget(self._updateModeControl)
        self.addDockWidget(qt.Qt.TopDockWidgetArea, self._docker)
        self.setWindowFlags(qt.Qt.Widget)

        # connect signal / slot
        self._updateModeControl.sigUpdateModeChanged.connect(
            self._roiStatsWindow._setUpdateMode
        )
        callback = functools.partial(
            self._roiStatsWindow._updateAllStats, is_request=True
        )
        self._updateModeControl.sigUpdateRequested.connect(callback)

        # expose API
        self.registerROI = self._roiStatsWindow.registerROI
        self.setStats = self._roiStatsWindow.setStats
        self.addItem = self._roiStatsWindow.addItem
        self.removeItem = self._roiStatsWindow.removeItem
        self.setUpdateMode = self._updateModeControl.setUpdateMode

        # setup
        self._updateModeControl.setUpdateMode("auto")


class _RoiStatsDisplayExWindow(qt.QMainWindow):
    """
    Simple window to group the different statistics actors
    """

    def __init__(self, parent=None, mode=None):
        qt.QMainWindow.__init__(self, parent)
        self.plot = Plot2D()
        self.setCentralWidget(self.plot)

        # 1D roi management
        self._curveRoiWidget = self.plot.getCurvesRoiDockWidget().widget()
        # hide last columns which are of no use now
        for index in (5, 6, 7, 8):
            self._curveRoiWidget.roiTable.setColumnHidden(index, True)

        # 2D - 3D roi manager
        self._regionManager = RegionOfInterestManager(parent=self.plot)

        # Create the table widget displaying
        self._roiTable = RegionOfInterestTableWidget()
        self._roiTable.setRegionOfInterestManager(self._regionManager)

        # Create a toolbar containing buttons for all ROI 'drawing' modes
        self._roiToolbar = qt.QToolBar()  # The layout to store the buttons
        self._roiToolbar.setIconSize(qt.QSize(16, 16))

        for roiClass in self._regionManager.getSupportedRoiClasses():
        # Create a tool button and associate it with the QAction of each mode
            self._roiToolbar.addAction(self._regionManager.getInteractionModeAction(roiClass))

        modeSelectorAction = RoiModeSelectorAction()
        modeSelectorAction.setRoiManager(self._regionManager)

        # Create the table widget displaying
        self._roiTable = RegionOfInterestTableWidget()
        self._roiTable.setRegionOfInterestManager(self._regionManager)

        # tabWidget for displaying the rois
        self._roisTabWidget = qt.QTabWidget(parent=self)
        if hasattr(self._roisTabWidget, "setTabBarAutoHide"):
            self._roisTabWidget.setTabBarAutoHide(True)

        # widget for displaying stats results and update mode
        self._statsWidget = _RoiStatsWidget(parent=self, plot=self.plot)

        # create Dock widgets
        self._roisTabWidgetDockWidget = qt.QDockWidget(parent=self)
        self._roisTabWidgetDockWidget.setWidget(self._roisTabWidget)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._roisTabWidgetDockWidget)

        # create Dock widgets
        self._roiStatsWindowDockWidget = qt.QDockWidget(parent=self)
        self._roiStatsWindowDockWidget.setWidget(self._statsWidget)
        # move the docker contain in the parent widget
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._statsWidget._docker)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._roiStatsWindowDockWidget)

        # expose API
        self.setUpdateMode = self._statsWidget.setUpdateMode

        # Create a container widget for the 2D ROI tab
        self._2DRoiContainer = qt.QWidget()
        self._2DRoiContainer.setLayout(qt.QVBoxLayout())

        # Add the toolbar and the table widget to the container
        self._2DRoiContainer.layout().addWidget(self._roiToolbar)
        self._2DRoiContainer.layout().addWidget(self._roiTable)

        # Connect ROI creation signal to register ROIs automatically
        self._regionManager.sigRoiAdded.connect(self._registerRoi)

    def _registerRoi(self, roi):
        #Register a newly created ROI with the stats widget.
        self._statsWidget.registerROI(roi)

    def setRois(self, rois1D=None, rois2D=None):
        rois2D = rois2D or ()

        for roi2D in rois2D:
            self._regionManager.addRoi(roi2D)
            self._statsWidget.registerROI(roi2D)

        self._roisTabWidget.addTab(self._2DRoiContainer, "2D roi(s)")
        #self._roisTabWidget.addTab(self._curveRoiWidget, "1D roi(s)")

    def setStats(self, stats):
        self._statsWidget.setStats(stats=stats)

    def addItem(self, item, roi):
        self._statsWidget.addItem(roi=roi, plotItem=item)


# define stats to display
STATS = [
    ("mean", numpy.mean),
    ("std", numpy.std),
    ("min", numpy.min),
    ("max", numpy.max),
]

def example_image(mode):
    """set up the roi stats example for images"""
    app = qt.QApplication([])

    window = _RoiStatsDisplayExWindow()
    # setup the stats display and updating
    roiStatsDisplayExWindow = _RoiStatsDisplayExWindow()
    roiStatsDisplayExWindow.setStats(STATS)
    roiStatsDisplayExWindow.setUpdateMode("auto")
    # Create the thread that calls submitToQtMainThread
    updateThread = UpdateThread(window.plot)
    updateThread.start()  # Start updating the plot

    window.setRois(window)

    # define some image and curve
    window.plot.addImage(numpy.arange(10000).reshape(100, 100), legend="img1")
    window.plot.addImage(
        numpy.random.random(10000).reshape(100, 100), legend="img2", origin=(0, 100)
    )
    window.setStats(STATS)

    # add some couple (plotItem, roi) to be displayed by default
    img1_item = window.plot.getImage("img1")
    img2_item = window.plot.getImage("img2")

    window.setUpdateMode(mode)

    window.show()
    app.exec()
    updateThread.stop()  # Stop updating the plot

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--items",
        dest="items",
        default="curves+images",
        help="items type(s), can be curve, image, curves+images",
    )
    parser.add_argument(
        "--mode", dest="mode", default="auto", help="valid modes are `auto` or `manual`"
    )
    options = parser.parse_args(argv[1:])

    items = options.items.lower()
    if items == "curves+images":  
        example_image(mode=options.mode)
    else:
        raise ValueError("invalid entry for item type")

if __name__ == "__main__":
    main(sys.argv)
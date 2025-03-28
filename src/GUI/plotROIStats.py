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
    """Thread updating the image of a :class:`~silx.gui.plot.Plot2D`

    :param plot2d: The Plot2D to update."""

    def __init__(self, window):
        self.window = window
        self.plot2d = window.plot
        self.running = False
        super(plotUpdateThread, self).__init__()
        self.camera = CameraInit(720, 1280, 10000)

    def start(self):
        """Start the update thread"""
        self.running = True
        super(plotUpdateThread, self).start()

    def run(self):
        """Method implementing thread loop that updates the plot"""
        while self.running:
            time.sleep(0.05)
            frame = self.camera.capture_frame()
            if frame is not None:
                concurrent.submitToQtMainThread(self.plot2d.addImage, frame, legend="opencv_capture")
                #concurrent.submitToQtMainThread(self.window.updateAllStats(), is_request=True)

            # Run plot update asynchronously not needed
            #concurrent.submitToQtMainThread(
                #only sample noise below, used for initial testing
                #numpy.random.random(10000).reshape(100, 100),
                #resetzoom=False,
                #legend=random.choice(("img1", "img2")),
            #)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

'''class _RoiStatsWidget():
    """
    Window used to associate ROI manager, ROIStatsWidget and UpdateModeWidget
    """

    def __init__(self, parent=None, plot=None, mode=None):
        assert plot is not None
        qt.QMainWindow.__init__(self, parent)
        self._roiStatsWindow = ROIStatsWidget(plot=plot)
        self.setCentralWidget(self._roiStatsWindow)

        # remove update mode docker but keep the possibility to change the update mode
        #self._updateModeControl
        #self._updateModeControl = UpdateModeWidget(parent=self)
        #self._docker = qt.QDockWidget(parent=self)
        #self._docker.setWidget(self._updateModeControl)
        #self.addDockWidget(qt.Qt.TopDockWidgetArea, self._docker)
        #self.setWindowFlags(qt.Qt.Widget)

        # connect signal / slot
        #self._updateModeControl.sigUpdateModeChanged.connect(
        #    self._roiStatsWindow._setUpdateMode
        #)
        #callback = functools.partial(
        #    self._roiStatsWindow._updateAllStats, is_request=True
        #)
        #self._updateModeControl.sigUpdateRequested.connect(callback)

        # expose API
        self.registerROI = self._roiStatsWindow.registerROI
        self.setStats = self._roiStatsWindow.setStats
        self.addItem = self._roiStatsWindow.addItem
        self.removeItem = self._roiStatsWindow.removeItem
        #no need to set update mode, done automatically 
        #self.setUpdateMode = self._updateModeControl.setUpdateMode
        self.updateAllStats = self._roiStatsWindow._updateAllStats
        self.setUpdateMode = self._roiStatsWindow._setUpdateMode'''

class _RoiStatsDisplayExWindow(qt.QMainWindow):
    """
    Simple window to group the different statistics actors
    """

    def __init__(self, parent=None, mode=None):
        qt.QMainWindow.__init__(self, parent)
        self.plot = Plot2D(parent=self, backend="gl")
        self.setCentralWidget(self.plot)

        # widget for displaying stats results and update mode
        self._statsWidget = roiStatsWindow(parent=self, plot=self.plot)

        # 1D roi management
        self._curveRoiWidget = self.plot.getCurvesRoiDockWidget().widget()
        # hide last columns which are of no use now
        #for index in (5, 6, 7, 8):
        #    self._curveRoiWidget.roiTable.setColumnHidden(index, True)
    
        # 2D - 3D roi manager
        self._regionManagerWidget = roiManagerWidget(parent=self, plot=self.plot)

        '''# Create the table widget displaying
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
        '''
        
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

        '''
        # uncover the API of updatemode and control over the update of all ROI stats
        self.setUpdateMode = self._statsWidget.setUpdateMode
        self.updateAllStats = self._statsWidget.updateAllStats '''

        '''# Create a container widget for the 2D ROI tab
        self._2DRoiContainer = qt.QWidget()
        self._2DRoiContainer.setLayout(qt.QVBoxLayout())

        # Add the toolbar and the table widget to the container
        self._2DRoiContainer.layout().addWidget(self._roiToolbar)
        self._2DRoiContainer.layout().addWidget(self._roiTable)'''

        # Connect ROI signal to register ROI automatically
        self._regionManagerWidget.roiManager.sigRoiAdded.connect(self._statsWidget.registerRoi)
        self._regionManagerWidget.roiManager.sigRoiAboutToBeRemoved.connect(self._statsWidget.unregisterRoi)

        self._roisTabWidget.addTab(self._regionManagerWidget, "2D roi(s)")
        self._roisTabWidget.addTab(self._curveRoiWidget, "1D roi(s)")
    
    '''
    def _registerRoi(self, roi):
        #Register a newly created ROI with the stats widget.
        self._statsWidget.registerROI(roi)

    def _unregisterRoi(self, roi):
        print("unregistering roi")
        #Unregister a ROI with the stats widget.
        #self._statsWidget._roiStatsWindow._statsROITable.unregisterROI(roi)
        #self._statsWidget.unregisterROI(roi)

    def setStats(self, stats):
        self._statsWidget.setStats(stats=stats)

        self.roiUpdateTimer = qt.QTimer(self)
        self.roiUpdateTimer.timeout.connect(lambda: self._statsWidget.updateAllStats(is_request=True))
        self.roiUpdateTimer.start(50)

    def addItem(self, item, roi):
        self._statsWidget.addItem(roi=roi, plotItem=item)
    '''

def example_image(mode):
    """set up the roi stats example for images"""
    app = qt.QApplication([])

    window = _RoiStatsDisplayExWindow()
    # setup the stats display and updating
    #roiStatsDisplayExWindow.setUpdateMode("auto")
    # Create the thread that calls submitToQtMainThread
    updateThread = plotUpdateThread(window)
    updateThread.start()  # Start updating the plot
    # Create the thread that updates the stats

    #roiThread = roiUpdateThread(window)
    #roiThread.start()  # Start updating the stats
    #window.setUpdateMode(mode)
    window.show()
    window.plot.setKeepDataAspectRatio(True)
    window.plot.setYAxisInverted(True)
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
        "--mode", dest="mode", default="manual", help="valid modes are `auto` or `manual`"
    )
    options = parser.parse_args(argv[1:])

    items = options.items.lower()
    if items == "curves+images":  
        example_image(mode=options.mode)
    else:
        raise ValueError("invalid entry for item type")

#if __name__ == "__main__":
#    main(sys.argv)
from silx.gui import qt
from silx.gui.plot import Plot2D
from silx.gui.plot.StackView import StackView
import argparse
import time
from camera.opencv_capture import CameraInit
from gui.roiwidget import roiManagerWidget
from gui.statswindow import roiStatsWindow
from gui.about_menu import AboutWindow
from gui.camera_menu import CameraMenuWindow
import gui.file_menu as file_menu
from gui.file_menu import H5Playback


class plotUpdateThread(qt.QThread):
    """Thread updating the stack in the stack view.

    :param plot2d: The StackView to update."""

    def __init__(self, window):
        self.window = window
        self.plot = window.plot
        self.plot2d = self.plot.getPlotWidget()
        self.running = False
        super(plotUpdateThread, self).__init__()

    def start(self):
        """Start the update thread"""
        self.running = True
        super(plotUpdateThread, self).start()

    def run(self):
        """Method implementing thread loop that updates the plot"""
        while self.running:
            if self.window.camera is not None:
                if self.window.camera.cap.isOpened():
                    self.window.camera.capture_frame()
                    time.sleep((self.window.camera.getFPS())/1000)
            if self.window.syncButton is not None and self.window.syncButton.isChecked():
                self.window._sync_camera()
            #_framenum = self.plot2d.getFrameNumber()
            #self.plot2d.setFrameNumber(_framenum)
            #if frame is not None:
            #    concurrent.submitToQtMainThread(self.plot2d, frame, legend="opencv_capture")

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

class _RoiStatsDisplayExWindow(qt.QMainWindow):
    """
    Simple window to group the different statistics actors
    """

    """Signal to emit when the data is resized"""
    dataResized = qt.Signal(object, object)

    def __init__(self, parent=None, mode=None):
        qt.QMainWindow.__init__(self, parent)
        self.plot = StackView(parent=self, backend="gl")
        self.setCentralWidget(self.plot)
        self.setWindowTitle("RHEED Analysis")
        self.plot.setColormap("green")
        self.plot.setKeepDataAspectRatio(True)
        self.plot.setYAxisInverted(True)
        # remove unnecessary plane selection widget
        self.plot._StackView__planeSelection.setVisible(False)
        self.plot._StackView__planeSelection.setEnabled(False)
        #self.plot._StackView__dimensionsLabels.setVisible(False)
        self.plot._StackView__dimensionsLabels.clear
        # change the plane widget label to a slider label for consistency
        self.plot._browser_label.setText("Slider (Frames):")
        self.plot.layout().spacing = 5

        # create a none camera object placeholder
        self.camera = None

        # create a none sync button placeholder
        self.syncButton = None

        # create a menu bar
        self.menu = qt.QMenuBar(self)
        self.menu.setNativeMenuBar(False)

        # add file menu for video/dataset upload (h5py for now only)
        file_action = qt.QAction("Video/Dataset Upload", self)
        file_action.triggered.connect(self._file_menu)
        self.menu.addAction(file_action)

        # add camera setup and launch
        camera_action = qt.QAction("Camera Setup and Launch", self)
        camera_action.triggered.connect(self._camera_menu)
        self.menu.addAction(camera_action)

        # add about window
        about_action = qt.QAction("About", self)
        about_action.triggered.connect(self._about_menu)
        self.menu.addAction(about_action)

        # add menu to the window
        self.setMenuBar(self.menu)

        # hidden plot2D for stats
        self._hiddenPlot2D = Plot2D()  # not added to layout
        self._hiddenPlot2D.hide()

        # widget for displaying stats results and update mode
        self._statsWidget = roiStatsWindow(parent=self, plot=self._hiddenPlot2D, stackview=self.plot)
        self.plot.sigFrameChanged.connect(self._update_hidden_plot)
        self.plot.sigFrameChanged.connect(self._statsWidget.updateTimeseriesAsync)

        # 1D roi management
        self._curveRoiWidget = self.plot.getPlotWidget().getCurvesRoiDockWidget()

        # 2D - 3D roi manager
        self._regionManagerWidget = roiManagerWidget(parent=self, plot=self.plot.getPlotWidget())
        
        # tabWidget for displaying the rois
        self._roisTabWidget = qt.QTabWidget(parent=self)

        # create Dock widgets
        self._roisTabWidgetDockWidget = qt.QDockWidget(parent=self)
        self._roisTabWidgetDockWidget.setWidget(self._roisTabWidget)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._roisTabWidgetDockWidget)

        # create Dock widgets
        self._roiStatsWindowDockWidget = qt.QDockWidget(parent=self)
        self._roiStatsWindowDockWidget.setWidget(self._statsWidget)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._roiStatsWindowDockWidget)

        # Connect ROI signal to register ROI automatically
        self._regionManagerWidget.roiManager.sigRoiAdded.connect(self._onRoiAdded)
        self._regionManagerWidget.roiManager.sigRoiAboutToBeRemoved.connect(self._statsWidget.unregisterRoi)

        self._roisTabWidget.addTab(self._regionManagerWidget, "2D roi(s)")
        self._roisTabWidget.addTab(self._curveRoiWidget, "1D roi(s)")

    def _file_menu(self):
        file_path = file_menu.open_h5_dataset_path()
        if file_path is not None:
            try:
                self.plot.setStack(H5Playback(file_path).image_dataset)
                self.plot.setFrameNumber(0)
            except Exception as e:
                print(f"Failed to load HDF5 dataset: {e}")
        
    def _camera_menu(self):
        self.cmw = CameraMenuWindow()
        self.cmw.show()
        self.cmw.buttonClicked.connect(self._camera_init)

    def _camera_init(self):
        self.camera = CameraInit(100)

        # create an icon button to sync the stackview and its FPS speed with the camera
        self.syncButton = qt.QPushButton("Sync", self)
        self.syncButton.setIcon(self.style().standardIcon(qt.QStyle.SP_ArrowRight))
        self.syncButton.setLayoutDirection(qt.Qt.RightToLeft)
        self.syncButton.setIconSize(qt.QSize(20, 20))
        self.syncButton.setToolTip("Sync the stackview with the camera")
        self.syncButton.setCheckable(True)
        self.syncButton.clicked.connect(self._sync_camera)
        self.syncButton.toggled.connect(self._sync_camera)
        # add the sync button to the slider browser layout
        self.plot._browser.mainLayout.addWidget(self.syncButton)
        self.plot._browser.setFrameRate(int(self.camera.getFPS()))
        self.plot._browser.setContentsMargins(0, 0, 15, 0)

        # populate the stackview with the camera dataset
        self.plot.setStack(self.camera.image_dataset)
        self.plot.setFrameNumber(0)

        # connect the resize callback to the camera
        self.camera.on_resize = lambda new_dataset: self.dataResized.emit(self.plot, new_dataset)

        # connect the resize signal to the plot
        self.dataResized.connect(self.update_dataset)
        
        self.timer = qt.QTimer(self)
        self.timer.timeout.connect(self._camera_loop)
        self.timer.start(int(self.camera.getFPS()/1000))


    def _sync_camera(self):
        self.plot.setFrameNumber(self.camera.getCurrentFrame())

    def _camera_loop(self):
        if self.camera is not None and self.camera.cap.isOpened():
            self.camera.capture_frame()
            if self.syncButton is not None and self.syncButton.isChecked():
                self._sync_camera()
            
    def _about_menu(self):
        aw = AboutWindow(self)
        aw.show()

    def _onRoiAdded(self, roi):
        self._statsWidget.registerRoi(roi)
        image = self._hiddenPlot2D.addImage(self.plot._stack[self.plot.getFrameNumber()])
        if image is not None:
            print(image)
            self._statsWidget.addItem(roi=roi, item=image)
            self._statsWidget.statsWidget._updateAllStats()

    def _update_hidden_plot(self, index):
        try:
            frame = self.plot._stack[self.plot.getFrameNumber()]
            if frame is None or frame.size == 0:
                return
            self._hiddenPlot2D.addImage(frame)
            self._statsWidget.statsWidget._updateAllStats()
        except Exception as e:
            print(f"Failed to update hidden plot: {e}")

    def update_dataset(self, plot, dataset):
        """Update the plot with the new dataset"""
        framenum = plot.getFrameNumber()
        plot.setStack(dataset)
        plot.setFrameNumber(framenum)

def example_image(mode):
    app = qt.QApplication([])
    app.quitOnLastWindowClosed()
    window = _RoiStatsDisplayExWindow()
    #t = plotUpdateThread(window)
    #t.start()
    window.show()
    app.exec()

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
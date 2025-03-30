from silx.gui import qt
from silx.gui.plot.ROIStatsWidget import ROIStatsWidget
from silx.gui.plot.StatsWidget import _ScalarFieldViewWrapper
import numpy
from silx.gui.plot import Plot1D
from silx.gui.plot.StackView import StackView

class roiStatsWindow(qt.QWidget):
    """Window that embeds the stats widget and button for launching time series of the ROIs."""

    STATS = [
    ("mean", numpy.mean),
    ]

    def __init__(self, parent=None, plot=None, stackview=None):
        """
        Create a window that embeds the stats widget and button for showing _timeseries of the ROIs.
        """
        assert plot is not None
        qt.QMainWindow.__init__(self, parent)
        self._plot2d = plot
        self._stackview = stackview
        layout = qt.QVBoxLayout(self)
        self.statsWidget = ROIStatsWidget(plot=self._plot2d)
        
        self._timeseries = qt.QWidget()
        self._timeseries.setLayout(qt.QVBoxLayout())
        self._timeseries.setWindowTitle("ROI Time Series")
        self._timeseries.plot = Plot1D()
        self._timeseries.layout().addWidget(self._timeseries.plot)
        self._timeseries.plot.setGraphXLabel("Frame number")
        self._timeseries.plot.setGraphYLabel("Intensity")
        self._timeseries.plot.setGraphTitle("ROI Time Series")
        self._timeseries.plot.setKeepDataAspectRatio(False)
        self._timeseries.plot.setActiveCurveHandling(False)
        self._timeseries.hide()

        self._meanarray = {[roi.getName()]: numpy.array([]) for roi in self.statsWidget._rois}

        ''' Main layout for the custom widget
        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        '''
        
        # Create a horizontal layout for the time series button
        btnLayout = qt.QHBoxLayout()
        btnLayout.setAlignment(qt.Qt.AlignmentFlag.AlignVCenter)
        timeseriesbutton = qt.QPushButton("Show Timeseries Plot", self)
        btnLayout.addStretch(2)
        btnLayout.addWidget(timeseriesbutton)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(self.statsWidget)
        layout.addLayout(btnLayout)

        self.statsWidget._setUpdateMode("manual")
        self.setStats(self.STATS)
        timeseriesbutton.clicked.connect(self.showTimeseries)
    
    def showTimeseries(self):
            self.updateTimeseriesAsync()
            self._timeseries.show()
            self._stackview.sigStackChanged.connect(self._dataset_size_changed)

    def _dataset_size_changed(self):
        """Update the x-axis limits of the time series plot when the dataset size changes."""
        #(data, info) = self._stackview.getStack(copy=True, returnNumpyArray=True)
        #print(data.size)
        #self._timeseries.plot.setGraphXLimits(0, data.size)

    def _getMeanForROI(self, roi):
        """Return the current computed mean stat for the given ROI.
        This reads the value from the internal _statsROITable.
        """
        table = self.statsWidget._statsROITable
        meanColumn = None
        # Find the column index for the 'mean' stat.
        for col in range(table.columnCount()):
            header = table.horizontalHeaderItem(col)
            if header and header.data(qt.Qt.UserRole) == 'mean':
                meanColumn = col
                break

        if meanColumn is None:
            print("Mean column not found")
            return None

        # Now locate the row corresponding to the ROI by matching its name.
        meanValue = None
        for row in range(table.rowCount()):
            roiItem = table.item(row, 2)  # Column 2 is used for ROI name.
            if roiItem and roiItem.text() == roi.getName():
                meanItem = table.item(row, meanColumn)
                if meanItem:
                    try:
                        meanValue = float(meanItem.text())
                    except ValueError:
                        print("Could not convert mean value to float")
                        meanValue = None
                break

        return meanValue


    def setStats(self, stats):
        self.statsWidget.setStats(stats=stats)

        self.roiUpdateTimer = qt.QTimer(self)
        self.roiUpdateTimer.timeout.connect(lambda: self.statsWidget._updateAllStats(is_request=True))
        self.roiUpdateTimer.start(50)

    def addItem(self, item, roi):
        self.statsWidget.addItem(roi=roi, plotItem=item)

    def removeItem(self, item):
        self.statsWidget.removeItem(item)

    def registerRoi(self, roi):
        #Register a newly created ROI with the stats widget.
        self.statsWidget.registerROI(roi)

    def unregisterRoi(self, roi):
        print("unregistering roi")
        #Unregister a ROI in the stats widget.
        self._statsWidget._roiStatsWindow._statsROITable.unregisterROI(roi)
        self._statsWidget.unregisterROI(roi)
        #self._statsWidget

    def updateTimeseriesAsync(self):
        framenum = self._stackview.getFrameNumber()
        self.worker = TimeseriesWorker(
            rois=self.statsWidget._rois,
            meanarray=self._meanarray,
            getMeanFunc=self._getMeanForROI,
            frameNumber=framenum
        )
        self.worker.updated.connect(self._plotTimeseries)
        self.worker.start()

    def _plotTimeseries(self, data):
        self._timeseries.plot.clear()
        for name, (x, y, color) in data.items():
            self.c = self._timeseries.plot.addCurve(x, y, legend=name)
            self.c.setColor(color)

class TimeseriesWorker(qt.QThread):
    updated = qt.Signal(dict)  # signal to send processed data back to GUI

    def __init__(self, rois, meanarray, getMeanFunc, frameNumber):
        super().__init__()
        self.rois = rois
        self.meanarray = meanarray
        self.getMean = getMeanFunc
        self.framenum = frameNumber

    def run(self):
        result = {}
        for roi in self.rois:
            name = roi.getName()
            if name not in self.meanarray:
                self.meanarray[name] = numpy.array([])

            new_value = self.getMean(roi)
            if new_value is not None:
                self.meanarray[name] = numpy.append(self.meanarray[name], new_value)

                if self.framenum > 500:
                    x = numpy.arange(self.framenum - 500)
                    y = self.meanarray[name][self.framenum - 500:]
                else:
                    x = numpy.arange(self.framenum)
                    y = self.meanarray[name][:self.framenum]

                if x.size != y.size:
                    y = numpy.resize(y, x.size)

                result[name] = (x, y, roi.getColor())

        self.updated.emit(result)  # send data back to GUI thread

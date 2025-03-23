from silx.gui import qt
from silx.gui.plot.ROIStatsWidget import ROIStatsWidget
import numpy
from silx.gui.plot import Plot1D

class roiStatsWindow(qt.QMainWindow):

    STATS = [
    ("mean", numpy.mean),
    ]

    def __init__(self, parent=None, plot=None):
        """
        Create a window that embeds the stats widget and button for showing timeseries of the ROIs.
        """
        assert plot is not None
        qt.QMainWindow.__init__(self, parent)
        self.statsWidget = ROIStatsWidget(plot=plot)
        self.setCentralWidget(self.statsWidget)

        ''' Main layout for the custom widget
        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        '''
        
        # Create a horizontal layout for the save/load buttons
        btnLayout = qt.QHBoxLayout()
        #self.timeseriesbutton = qt.QPushButton("Show Timeseries Plot", self)
        btnLayout.addStretch(1)
        #btnLayout.addWidget(self.timeseriesbutton)

        self.statsWidget._setUpdateMode("manual")
        self.setStats(self.STATS)
        #self.timeseriesbutton.clicked.connect(self.showTimeseries)
    
    def showTimeseries(self):
        '''show the time series of the stats for all ROIs in a silx 1D plot, with automatic update, this will be a widget inside the main window'''
        self.timeseries = qt.QWidget()
        self.timeseries.setWindowTitle("ROI Time Series")
        self.timeseries.setLayout(qt.QVBoxLayout())
        self.timeseries.plot = Plot1D()
        self.timeseries.layout().addWidget(self.timeseries.plot)
        self.timeseries.plot.setGraphXLabel("Frame number")
        self.timeseries.plot.setGraphYLabel("Value")
        self.timeseries.plot.setGraphTitle("ROI Time Series")
        self.timeseries.plot.setKeepDataAspectRatio(True)
        self.timeseries.plot.setActiveCurveHandling(False)

        for roi in self.statsWidget._rois:
            stat = self._getMeanForROI(roi)
            if stat is not None:
                # x is dynamically updated depending on the number of frames
                x = numpy.arange(len(stat))
                y = numpy.array(stat)
                self.c = self.timeseries.plot.addCurve(x, y, legend=roi.getName())
                self.c.setSymbolVisible(False)
                self.c.setColor(roi.getColor())
        self.timeseries.show()

        '''
        for roi in self.statsWidget._rois:
            stats = self.statsWidget.getStats(roi)
            if stats is not None:
                x = numpy.arange(len(stats))
                y = numpy.array(stats)
                self.c = self.timeseries.plot.addCurve(x, y, legend=roi.getName())
                self.c.setSymbolVisible(False)
                self.c.setColor(roi.getColor())
        self.timeseries.show()
        '''

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
        #self._statsWidget._roiStatsWindow._statsROITable.unregisterROI(roi)
        #self._statsWidget.unregisterROI(roi)
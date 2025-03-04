from silx.gui import qt
from silx.gui.plot.tools.roi import RegionOfInterestManager, RegionOfInterestTableWidget, RoiModeSelectorAction
from silx.io import dictdump
import gui.roidictionary as rdict

class roiManagerWidget(qt.QWidget):
    def __init__(self, parent=None, plot=None):
        """
        Create a composite widget that embeds the 2D ROI manager and table,
        and adds Save/Load buttons.
        """
        super().__init__(parent)
        self.plot = plot

        # Main layout for the custom widget
        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Create a horizontal layout for the save/load buttons
        btnLayout = qt.QHBoxLayout()
        self.clearButton = qt.QPushButton("Clear All", self)
        self.saveButton = qt.QPushButton("Load", self)
        self.loadButton = qt.QPushButton("Save", self)
        btnLayout.addStretch(1)
        btnLayout.addWidget(self.clearButton)
        btnLayout.addWidget(self.saveButton)
        btnLayout.addWidget(self.loadButton)
        
        # Create the silx 2D ROI manager and table
        self.roiManager = RegionOfInterestManager(parent=plot)
        self._roiTable = RegionOfInterestTableWidget()
        self._roiTable.setRegionOfInterestManager(self.roiManager)

        # Create a toolbar containing buttons for all ROI 'drawing' modes
        self._roiToolbar = qt.QToolBar()
        self._roiToolbar.setIconSize(qt.QSize(16, 16))

        for roiClass in self.roiManager.getSupportedRoiClasses():
        # Create a tool button and associate it with the QAction of each mode
            self._roiToolbar.addAction(self.roiManager.getInteractionModeAction(roiClass))

        modeSelectorAction = RoiModeSelectorAction()
        modeSelectorAction.setRoiManager(self.roiManager)
        
        # Add the ROI table widget to the layout
        layout.addWidget(self._roiToolbar)
        layout.addWidget(self._roiTable)
        layout.addLayout(btnLayout)
        
        # Connect the button signals to the saving/loading methods and clear method
        self.loadButton.clicked.connect(self.loadROIs)
        self.saveButton.clicked.connect(self.saveROIs)
        self.clearButton.clicked.connect(self.clearROIs)
    
    # File dialog to save to file
    def saveROIs(self):
        # Use a file dialog to let the user choose a file name
        dialog = qt.QFileDialog(self)
        dialog.setAcceptMode(qt.QFileDialog.AcceptSave)
        dialog.setNameFilters(["INI File (*.ini)", "JSON File (*.json)"])
        if dialog.exec():
            filename = dialog.selectedFiles()[0]
            # Automatically add extension if missing (based on the filter)
            selectedFilter = dialog.selectedNameFilter()
            extension = ".ini" if "INI" in selectedFilter else ".json"
            if not filename.endswith(extension):
                filename += extension
            self._save(filename)
    
    # Save ROIs to a file
    def _save(self, filename):
        # Collect ROI data similar to the curvesROI widget's save method
        '''roilist = []
        roidict = {}
        for roi in self.roiManager.getRois():
            roilist.append(roi.getRoi())
            roidict[roi.getName()] = rdict.save_rois_to_file(roi)
        datadict = {"ROI": {"roilist": roilist, "roidict": roidict}}
        dictdump.dump(datadict, filename)'''
        # Save the ROI data to a file
        rois = self.roiManager.getRois()
        rdict.save_rois_to_file(rois, filename)
    
    # File dialog to load from file
    def loadROIs(self):
        dialog = qt.QFileDialog(self)
        dialog.setAcceptMode(qt.QFileDialog.AcceptOpen)
        dialog.setNameFilters(["INI File (*.ini)", "JSON File (*.json)"])
        if dialog.exec():
            filename = dialog.selectedFiles()[0]
            self._load(filename)
    
    # Load ROIs from a file
    def _load(self, filename):
        '''datadict = dictdump.load(filename)
        rois = []
        # Recreate ROI objects from the loaded dictionary
        for roiDict in datadict["ROI"]["roidict"].values():
            # Remove keys that might not be needed
            roiDict.pop("rawcounts", None)
            roiDict.pop("netcounts", None)
            # Use the ROI class’s _fromDict method
            from silx.gui.plot.tools.roi import ROI  # Adjust the import if needed
            roi = rdict.roi_from_dict(roiDict)
            rois.append(roi)
        self.roiTable.setRois(rois)'''
        # Load the ROI data from a file
        rois = rdict.load_rois_from_file(filename)
        for each in rois:
            self.roiManager.addRoi(each)

    # Clear all ROIs from the plot
    def clearROIs(self):
        self.roiManager.clear()
        self._roiTable.clear()
import silx.io
from silx.gui import qt
import h5py

class H5Playback:
    def __init__(self, file_path):
        self.h5_file = h5py.File(file_path, "r")
        # Try to find a 3D dataset
        self.image_dataset = None
        for name in self.h5_file.keys():
            d = self.h5_file[name]
            if d.ndim == 3:
                self.image_dataset = d
                break

        if self.image_dataset is None:
            raise ValueError("No 3D dataset found in file.")

        self.frame_index = 0
        self.dataset_size = self.image_dataset.shape[0]
        self.on_resize = None  # for compatibility

    def capture_frame(self):
        frame = self.image_dataset[self.frame_index]
        return frame

def open_h5_dataset_path():
    dialog = qt.QFileDialog()
    dialog.setFileMode(qt.QFileDialog.ExistingFile)
    dialog.setNameFilter("H5 Datasets (*.h5)")
    dialog.setViewMode(qt.QFileDialog.Detail)

    if dialog.exec_():
        selected_files = dialog.selectedFiles()
        if selected_files:
            return selected_files[0]
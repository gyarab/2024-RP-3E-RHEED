import silx.io
from silx.gui import qt

def open_h5_dataset():
    dialog = qt.QFileDialog()
    dialog.setFileMode(qt.QFileDialog.ExistingFile)
    dialog.setNameFilter("H5 Datasets (*.h5)")
    dialog.setViewMode(qt.QFileDialog.Detail)

    if dialog.exec_():
        selected_files = dialog.selectedFiles()
        if selected_files:
            file_path = selected_files[0]
            try:
                with silx.io.open(file_path) as h5_file:
                    dataset_names = h5_file.keys()
                    for dataset_name in dataset_names:
                        dataset = h5_file[dataset_name]
                        if dataset.ndim == 3:
                            # Process the 3D dataset
                            print(f"Processing dataset: {dataset_name}")
                        else:
                            print(f"Skipping dataset: {dataset_name} (not 3D)")
            except Exception as e:
                print(f"Error opening file: {str(e)}")
        else:
            print("No file selected")
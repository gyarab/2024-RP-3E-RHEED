import silx.gui.qt as qt

class AboutWindow(qt.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        
        layout = qt.QVBoxLayout()
        
        # App name and version
        app_name_label = qt.QLabel("RHEED Analysis App")
        app_name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(app_name_label)
        
        version_label = qt.QLabel("Version 1.0")
        layout.addWidget(version_label)
        
        # Description
        description_label = qt.QLabel("This app is designed for real-time RHEED analysis for MBE and other epitaxy growth methods.")
        layout.addWidget(description_label)
        
        # Links
        links_label = qt.QLabel("Useful Links:")
        layout.addWidget(links_label)
        
        link1_label = qt.QLabel('<a href="https://example.com">Link 1</a>')
        link1_label.setOpenExternalLinks(True)
        layout.addWidget(link1_label)
        
        link2_label = qt.QLabel('<a href="https://example.com">Link 2</a>')
        link2_label.setOpenExternalLinks(True)
        layout.addWidget(link2_label)
        
        # Contacts
        contacts_label = qt.QLabel("Contacts:")
        layout.addWidget(contacts_label)
        
        contact1_label = qt.QLabel("John Doe - john.doe@example.com")
        layout.addWidget(contact1_label)
        
        contact2_label = qt.QLabel("Jane Smith - jane.smith@example.com")
        layout.addWidget(contact2_label)
        
        self.setLayout(layout)
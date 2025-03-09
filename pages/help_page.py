import os
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt

def resource_path(relative_path):
    """UI 파일 경로를 반환하는 함수"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

ui_file = resource_path("../ui/help_page.ui")
form_class = uic.loadUiType(ui_file)[0]

class HelpPage(QDialog, form_class):
    def __init__(self, parent_geometry, main_window):
        super().__init__()
        self.setupUi(self)
        self.setGeometry(parent_geometry)
        self.main_window = main_window
        self.to_mainButton.clicked.connect(self.to_main)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def to_main(self):
        self.main_window.last_geometry = self.geometry()
        self.hide()
        self.main_window.setGeometry(self.geometry())
        self.main_window.show()

    def closeEvent(self, event):
        self.main_window.close()
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from .information_page import InformationPage
from .semester_gpa_page import SemesterGpaPage
from .overall_gpa_page import OverallGpaPage
from .credits_page import CreditsPage
from .help_page import HelpPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_path = os.path.join(os.path.dirname(__file__), "../ui/main_window.ui")
        uic.loadUi(ui_path, self)

        self.last_geometry = self.geometry()

        self.to_firstButton.clicked.connect(lambda: self.change_page("information", InformationPage))
        self.to_secondButton.clicked.connect(lambda: self.change_page("semester_gpa", SemesterGpaPage))
        self.to_thirdButton.clicked.connect(lambda: self.change_page("overall_gpa", OverallGpaPage))
        self.to_fourthButton.clicked.connect(lambda: self.change_page("credits", CreditsPage))
        self.to_fifthButton.clicked.connect(lambda: self.change_page("help", HelpPage))
        self.githubButton.clicked.connect(self.open_github)

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.pages = {}

    def change_page(self, page_name, page_class):
        self.last_geometry = self.geometry()
        self.hide()

        if page_name in self.pages:
            self.pages[page_name].deleteLater()

        new_page = page_class(self.last_geometry, self)
        self.pages[page_name] = new_page
        new_page.show()

    def show_error(self, message):
        QMessageBox.warning(self, "오류", message)

    def open_github(self):
        url = "https://github.com/sternenlicht/cau_gpa"
        if not QDesktopServices.openUrl(QUrl(url)):
            self.show_error("사이트에 연결할 수 없습니다.")

    def delete_pages(self):
        for page in self.pages.values():
            page.deleteLater()
        self.pages.clear()

    def closeEvent(self, event):
        self.delete_pages()
        QApplication.quit()
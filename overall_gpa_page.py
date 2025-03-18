import os
import math
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QPlainTextEdit
from PyQt5.QtCore import Qt
from .semester_gpa_page import SemesterGpaPage

def resource_path(relative_path):
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

ui_file = resource_path("../ui/overall_gpa_page.ui")
form_class = uic.loadUiType(ui_file)[0]

class OverallGpaPage(QDialog, form_class):
    def __init__(self, parent_geometry, main_window):
        super().__init__()
        self.setupUi(self)
        self.setGeometry(parent_geometry)
        self.main_window = main_window
        self.is_converted = False

        self.to_mainButton.clicked.connect(self.to_main)
        self.resetButton.clicked.connect(self.reset_user_inputs)
        self.copyButtonA.clicked.connect(self.format_copy_current)
        self.copyButtonB.clicked.connect(self.format_copy_if)
        self.calculateButton.clicked.connect(self.calculate_target_gpa)
        self.gpaConvertButton.clicked.connect(self.convert_gpa)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setup_user_input_listeners()
        self.current_gpa_values()

    @staticmethod
    def show_error(parent, message):
        QMessageBox.warning(parent, "오류", message)
    
    @staticmethod
    def show_message(parent, message):
        QMessageBox.information(parent, "알림", message)
    
    @staticmethod
    def copy_to_clipboard(parent, text):
        QApplication.clipboard().setText(text)
        OverallGpaPage.show_message(parent, "복사되었습니다.")
    
    @staticmethod
    def floor_decimal(value, decimal_places=2):
        factor = 10 ** decimal_places
        return math.floor(value * factor) / factor
    
    def get_semester_page(self):
        return SemesterGpaPage(self.geometry(), self.main_window)

    def current_gpa_values(self):
        semester_page = self.get_semester_page()
        col5_numerator, col5_denominator = semester_page.calculate_column5()
        col6_numerator, col6_denominator = semester_page.calculate_column6()
        gpa_raw = self.floor_decimal(col5_numerator / col5_denominator) if col5_denominator != 0 else 0
        gpa_adjusted = self.floor_decimal(col6_numerator / col6_denominator) if col6_denominator != 0 else 0
        self.textBrowser1.setText(f"{gpa_raw:.2f}")
        self.textBrowser2.setText(f"{gpa_adjusted:.2f}")

    def calculate_gpa(self):
        semester_page = self.get_semester_page()
        weights = [4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1]
        user_inputs = []
        
        for i in range(1, 9):
            plain_text_edit = self.findChild(QPlainTextEdit, f"plainTextEdit{i}")
            try:
                value = float(plain_text_edit.toPlainText().strip()) if plain_text_edit.toPlainText().strip() else 0
                user_inputs.append(value)
            except ValueError:
                plain_text_edit.clear()
                user_inputs.append(0)

        X = sum(user_inputs[i] * weights[i] for i in range(8))
        Y = sum(user_inputs)
        A, B = semester_page.calculate_column5()
        A2, B2 = semester_page.calculate_column6()

        gpa1 = self.floor_decimal((X + A) / (Y + B)) if (Y + B) != 0 else 0
        gpa2 = self.floor_decimal((X + A2) / (Y + B2)) if (Y + B2) != 0 else 0

        if self.is_converted:
            gpa1 = self.floor_decimal(float(self.convert(gpa1)))
            gpa2 = self.floor_decimal(float(self.convert(gpa2)))

            self.textBrowser5.setText(f"{gpa1:.1f}")
            self.textBrowser6.setText(f"{gpa2:.1f}")
        
        else:
            self.textBrowser5.setText(f"{gpa1:.2f}")
            self.textBrowser6.setText(f"{gpa1:.2f}")

    def setup_user_input_listeners(self):
        for i in range(1, 9):
            plain_text_edit = self.findChild(QPlainTextEdit, f"plainTextEdit{i}")
            if plain_text_edit:
                plain_text_edit.textChanged.connect(self.calculate_gpa)
        self.calculate_gpa()
    
    def reset_user_inputs(self):
        for i in range(1, 9):
            plain_text_edit = self.findChild(QPlainTextEdit, f"plainTextEdit{i}")
            if plain_text_edit:
                plain_text_edit.setPlainText("")
        self.calculate_gpa()

    def format_copy_current(self):
        tb1 = self.textBrowser1.toPlainText()
        tb2 = self.textBrowser2.toPlainText()
        copy_text = f"누적GPA(열람)\t{tb1}\n누적GPA(반영)\t{tb2}"
        self.copy_to_clipboard(self, copy_text)

    def format_copy_if(self):
        tb5 = self.textBrowser5.toPlainText()
        tb6 = self.textBrowser6.toPlainText()
        pt_values = [self.findChild(QPlainTextEdit, f"plainTextEdit{i}").toPlainText() for i in range(1, 9)]
        pt_values = [v if v else "0" for v in pt_values]
        copy_text = f"IF누적GPA(열람)\t{tb5}\t\tA+\tA\tB+\tB\tC+\tC\tD+\tD\n"
        copy_text += f"IF누적GPA(반영)\t{tb6}\t\t" + "\t".join(pt_values)
        self.copy_to_clipboard(self, copy_text)

    def calculate_target_gpa(self):
        mode = self.comboBox.currentText()
        semester_page = self.get_semester_page()
        if mode == "열람":
            A, B = semester_page.calculate_column5()
        else:
            A, B = semester_page.calculate_column6()
        X = self.plainTextEdit9.toPlainText()
        Y = self.plainTextEdit10.toPlainText()

        if not X or not Y:
            self.show_error(self, "값을 입력하세요.")
            return

        try:
            X = float(X)
            Y = float(Y)
            if X < 0 or X > 4.5 or Y <= 0:
                raise ValueError
        except ValueError:
            self.show_error(self, "올바른 숫자를 입력하세요.")
            return

        if A is None or B is None:
            self.show_error(self, "GPA 데이터가 부족합니다.")
            return

        result = self.floor_decimal(((B + Y) * X - A) / Y)
        self.textBrowser9.setPlainText(f"{result:.2f}")

    def convert(self, value):
        try:
            value = float(value)
            converted_value = (value - 55) / 10 if value >= 55 else 55 + 10 * value
            
            if value >= 55:
                if converted_value == 0:
                    return "0"
                elif converted_value == 4.5:
                    return "4.5"
                else:
                    return f"{max(0, min(4.5, converted_value)):.2f}"
            else:
                converted_value = min(100, converted_value)
                if converted_value == 55:
                    return "55"
                elif converted_value == 100:
                    return "100"
                else:
                    return f"{converted_value:.1f}"
        except ValueError:
            return ""
            
    def convert_gpa(self): 
        for browser in [self.textBrowser1, self.textBrowser2, self.textBrowser5, self.textBrowser6]:
            browser.setPlainText(self.convert(browser.toPlainText()))

        self.is_converted = not self.is_converted

    def to_main(self):
        self.main_window.last_geometry = self.geometry()
        self.hide()
        self.main_window.setGeometry(self.geometry())
        self.main_window.show()

    def closeEvent(self, event):
        self.main_window.close()
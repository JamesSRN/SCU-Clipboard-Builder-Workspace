import sys

from PySide6.QtWidgets import QApplication

from SCU_CBoards import ClinicApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClinicApp()
    window.show()
    sys.exit(app.exec())

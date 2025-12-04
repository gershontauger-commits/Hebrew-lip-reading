import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQt5 Test Window')
        self.setGeometry(200, 200, 400, 200)
        label = QLabel('If you see this window, PyQt5 works!', self)
        label.setGeometry(50, 80, 300, 40)

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

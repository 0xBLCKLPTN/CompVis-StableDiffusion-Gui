from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *
import time
import sys
import logging
import os
import subprocess
import random

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setFixedWidth(512)
        self.widget.setReadOnly(True)
        

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.setBaseSize(1000, 1000)
        self.setWindowTitle("Stable Diffusion GUI")
        self.out_dir = os.path.join(os.getcwd(), "outputs/txt2img-samples")
        self.seed = random.randint(1,2147483647)
        self.ddim_steps = 50
        self.plms = False
        self.laion = False
        self.height = 512
        self.width = 512
        self.start_command = 'python scripts/txt2img.py --prompt'
        self._setMainUi()
        
    
    def _init_layouts(self):
        self.widget = QWidget()    
        self.left_panel = QVBoxLayout()
        self.right_panel = QVBoxLayout()
        self.tree_settings = QHBoxLayout()
        self.layer_hor = QHBoxLayout()
        self.formGroupBox = QGroupBox("Settings")
        self.layout = QFormLayout()
    
    def _set_image(self, image: str = "rickroll.jpg"):
        self.pixmap = QPixmap(image)
        self.label.setPixmap(self.pixmap)

    def _init_settings(self):
        self.prompt = QLineEdit(self)
        self.seed_line = QLineEdit(self)
        self.ddim_line = QLineEdit(self)
        self.height_line = QLineEdit(self)
        self.width_line = QLineEdit(self)
        self.plms_bool = QCheckBox("Enable plms", self)
        self.laion_bool = QCheckBox("Enable laion",self)

        self.start_button = QtWidgets.QPushButton(self)
        self.start_button.setText("Start!")
        self.select_dir_button = QtWidgets.QPushButton(self)
        self.select_dir_button.setText("Select Output Directory")
        self.out_log = QLabel(self.out_dir)
        self.out_log.setFixedWidth(120)

        self.layout.addRow(QLabel("Prompt:"), self.prompt)
        self.layout.addRow(QLabel("Seed:"), self.seed_line)
        self.layout.addRow(QLabel("Ddim Steps:"), self.ddim_line)
        self.layout.addRow(QLabel("Height:"), self.height_line)
        self.layout.addRow(QLabel("Width:"), self.width_line)
        self.layout.addRow(self.plms_bool,self.laion_bool)
        self.layout.addRow(QLabel("Current Out Dir:"), self.out_log)
        self.layout.addRow(self.select_dir_button)
        self.layout.addRow(self.start_button)

        self._init_button_slots()

    def _init_button_slots(self):
        self.start_button.clicked.connect(self.start)
        self.select_dir_button.clicked.connect(self.sel_dir)
        self.laion_bool.stateChanged.connect(self.laion_func)
        self.plms_bool.stateChanged.connect(self.plms_func)

    def _init_log(self):
        self.logTextBox = QTextEditLogger(self)
        self.logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self.logTextBox)
        logging.getLogger().setLevel(logging.DEBUG)
    
    def _init_left_panel(self):
        self.label = QLabel(self)
        self._set_image()
        self._init_log()

        self.left_panel.addWidget(self.label)
        self.left_panel.addWidget(self.logTextBox.widget)

    def _init_right_panel(self):
        self._init_settings()
        self.formGroupBox.setLayout(self.layout)
        self.right_panel.addWidget(self.formGroupBox)

    def _init_layer_hor(self):
        self.layer_hor.addLayout(self.left_panel)
        self.layer_hor.addLayout(self.right_panel)

    def _setMainUi(self):
        self._init_layouts()
        self._init_left_panel()
        self._init_right_panel()
        self._init_layer_hor()

        self.widget.setLayout(self.layer_hor)
        self.setCentralWidget(self.widget)

    def start(self):
        generated_string = self.start_command + f' "{str(self.prompt.text())}" '
        if self.plms:
            generated_string += "--plms "
        if self.laion:
            generated_string += "--laion400m "
        
        if self.seed_line.text() != "":
            generated_string += "--seed " + str(self.seed_line.text()) + " "

        if self.seed_line.text() == "":
            generated_string += "--seed " + str(self.seed) + " "
        
        if self.height_line.text() == "":
            generated_string += f"--H {str(self.height)} "
        if self.width_line.text() == "":
            generated_string += f"--W {str(self.width)} "

        if self.height_line.text() != "":
            generated_string += f"--H {self.height_line.text()} "
        if self.width_line.text() != "":
            generated_string += f"--W {self.width_line.text()} "

        if self.ddim_line.text() != "":
            generated_string += f"--ddim_steps {str(self.ddim_line.text())} "
        if self.ddim_line.text() == "":
            generated_string += f"--ddim_steps {str(self.ddim_steps)} "

        if self.out_dir != "outputs/samples":
            generated_string += f"--outdir {self.out_dir} "

        logging.debug(generated_string)

        generated_string += "--skip_grid --n_samples 1"
        process = subprocess.call(generated_string)
        last_image = self.out_dir + "/samples/" + os.listdir(self.out_dir + "/samples")[-1]
        self._set_image(last_image)

    def sel_dir(self):
        self.out_dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.out_log.setText(self.out_dir)

    def laion_func(self, state):
        if state == QtCore.Qt.Checked:
            self.laion = True
        else:
            self.laion = False
    
    def plms_func(self, state):
        if state == QtCore.Qt.Checked:
            self.plms = True
        else:
            self.plms = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showNormal()

    app.exec_()

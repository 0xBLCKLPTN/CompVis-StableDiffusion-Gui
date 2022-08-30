from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *
import sys
import logging
import os
import random
import glob
import json

# Log window
class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setFixedWidth(512)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
        self.widget.moveCursor(QtGui.QTextCursor.End)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Default variables
        self.prompt="a photograph of an astronaut riding a horse"
        self.setBaseSize(1000, 1000)
        self.setWindowTitle("Stable Diffusion GUI")
        self.out_dir = os.path.join(os.getcwd(), "outputs")
        self.seed = random.randint(1, 2147483647)
        self.ddim_steps = 50
        self.plms = True
        self.laion = False
        self.height = 512
        self.width = 640
        self.last_image = "rickroll.jpg"
        self.start_command = 'python3 scripts/txt2img.py --prompt'
        self._setMainUi() # setting up ui
        self.default_setting_path = "settings.json"
        if os.path.exists(self.default_setting_path):
            self.import_settings(self.default_setting_path)

    def _init_layouts(self):
        # Initialize all layouts
        self.widget = QWidget()
        self.left_panel = QVBoxLayout()
        self.right_panel = QVBoxLayout()
        self.tree_settings = QHBoxLayout()
        self.layer_hor = QHBoxLayout()
        self.formGroupBox = QGroupBox("Settings")
        self.layout = QFormLayout()

    def _set_image(self, image: str = "rickroll.jpg"):
        # Set default/generated image
        self.pixmap = QPixmap(image)
        self.label.setPixmap(self.pixmap)

    def make_divisible_by_64(self):
        # round down to nearest divisible by 64.  This is for convenience-- 0 is still possible, 64 etc.
        self.height_line.setText(str(int(self.height_line.text()) - int(self.height_line.text()) % 64))
        self.width_line.setText(str(int(self.width_line.text()) - int(self.width_line.text()) % 64))

    def _init_settings(self):
        # Initializing all elements
        intreg = QRegExp("\\d+")
        self.prompt_line = QPlainTextEdit(self)
        self.seed_line = QLineEdit(self)
        self.seed_line.setValidator(QRegExpValidator(intreg))
        self.ddim_line = QLineEdit(self)
        self.ddim_line.setValidator(QRegExpValidator(intreg))
        self.height_line = QLineEdit(self)
        self.height_line.setValidator(QRegExpValidator(intreg))
        self.height_line.editingFinished.connect(self.make_divisible_by_64)
        self.width_line = QLineEdit(self)
        self.width_line.setValidator(QRegExpValidator(intreg))
        self.width_line.editingFinished.connect(self.make_divisible_by_64)

        self.plms_bool = QCheckBox("Enable plms", self)
        self.laion_bool = QCheckBox("Enable laion", self)

        self.new_seed_button = QtWidgets.QPushButton(self)
        self.new_seed_button.setText("Randomize Seed")

        self.start_button = QtWidgets.QPushButton(self)
        self.start_button.setText("Start!")

        self.save_settings_button = QtWidgets.QPushButton(self)
        self.save_settings_button.setText("Save settings")

        self.import_settings_button = QtWidgets.QPushButton(self)
        self.import_settings_button.setText("Import settings")

        self.select_dir_button = QtWidgets.QPushButton(self)
        self.select_dir_button.setText("Select \"outputs\" Directory")
        
        self.clipboard_button = QtWidgets.QPushButton(self)
        self.clipboard_button.setText("Copy Image to clipboard")

        self.out_log = QLabel(self.out_dir)
        self.out_log.setFixedWidth(500)
        # Adds all elements to right layout
        self.layout.addRow(QLabel("Prompt:"), self.prompt_line)
        self.layout.addRow(QLabel("Seed:"), self.seed_line)
        self.layout.addRow(QLabel("Ddim Steps:"), self.ddim_line)
        self.layout.addRow(QLabel("Height:"), self.height_line)
        self.layout.addRow(QLabel("Width:"), self.width_line)
        self.layout.addRow(self.plms_bool, self.laion_bool)
        self.layout.addRow(QLabel("Current \"outputs\" Directory:"))
        self.layout.addRow(self.out_log)
        self.layout.addRow(self.select_dir_button)
        self.layout.addRow(self.new_seed_button)
        self.layout.addRow(self.save_settings_button, self.import_settings_button)
        self.layout.addRow(self.clipboard_button)
        self.layout.addRow(self.start_button)
        self._init_button_slots()
        self.update_form()

    def update_form(self):
        self.prompt_line.setPlainText(self.prompt)
        self.seed_line.setText(str(self.seed))
        self.ddim_line.setText(str(self.ddim_steps))
        self.height_line.setText(str(self.height))
        self.width_line.setText(str(self.width))
        self.plms_bool.setCheckState(2 if self.plms is True else 0)
        self.laion_bool.setCheckState(2 if self.laion is True else 0)
        self.out_log.setText(self.out_dir)

    def _init_button_slots(self):
        # Initialize buttons and checkboxs
        self.start_button.clicked.connect(self.start)
        self.select_dir_button.clicked.connect(self.sel_dir)
        self.laion_bool.stateChanged.connect(self.laion_func)
        self.plms_bool.stateChanged.connect(self.plms_func)
        self.new_seed_button.clicked.connect(self.new_seed)
        self.save_settings_button.clicked.connect(self.save_settings)
        self.import_settings_button.clicked.connect(self.import_settings)
        self.clipboard_button.clicked.connect(self.to_clipboard)

    def _init_log(self):
        # Log window
        self.logTextBox = QTextEditLogger(self)
        self.logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self.logTextBox)
        logging.getLogger().setLevel(logging.DEBUG)

    def _init_left_panel(self):
        # Image and debug window
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

    def log_subprocess_output(self, pipe):
        for line in iter(pipe.readline, b''): # b'\n'-separated lines
            logging.info('got line from subprocess: %r', line)

    def _startImGenProcess(self, generated_command: str):
        self.process = QtCore.QProcess(self)
        self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.on_readyReadStandardOutput)
        self.process.finished.connect(self.process_done)
        self.process.start(generated_command)

    def process_done(self):
        # look for the new image
        # setting up generated image.
        last_images = glob.glob(os.path.join(self.out_dir, 'samples/*'))
        self.last_image = max(last_images, key=os.path.getctime)
        self._set_image(self.last_image)

    @QtCore.pyqtSlot()
    def on_readyReadStandardOutput(self):
        text = self.process.readAllStandardOutput().data().decode()
        logging.info(text)

    def start(self):
        # generating command via variables
        generated_string = self.start_command + f' "{str(self.prompt_line.toPlainText())}" '
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

        if os.path.exists(os.path.join(self.out_dir, "txt2img-samples")):
           self.out_dir = os.path.join(self.out_dir, "txt2img-samples")

        generated_string += f"--outdir {self.out_dir} "
        generated_string += "--skip_grid --n_samples 1 --n_iter 1"

        logging.debug(generated_string)  # output generated_string to debug window

        
        self._startImGenProcess(generated_string)  # Starting image generator

    def sel_dir(self):
        tmp = self.out_dir
        self.out_dir = str(QFileDialog.getExistingDirectory(self, "Select \"outputs\" Directory"))
        if not os.path.isdir(self.out_dir):
            self.out_dir = tmp
        self.out_log.setText(self.out_dir)

    def laion_func(self, state):
        if state == QtCore.Qt.Checked:
            self.laion = True
        else:
            self.laion = False

    def to_clipboard(self):
        if self.last_image != "":
            QApplication.clipboard().setImage(QImage(self.last_image))

    def import_settings(self):
        tmp = self.out_dir
        response = QFileDialog.getOpenFileNames(
            parent=self,
            caption='Select a data file',
            directory=os.getcwd(),
            filter="Json File (*.json)",
            initialFilter='Json File (*.json)'
        )
        print(response[0])
        with open(response[0][0]) as json_file:
            data = json.load(json_file)
        
            # Print the type of data variable
            print("Type:", type(data))
            self.seed_line.setText(str(data["seed"]))
            self.ddim_line.setText(str(data["ddim_steps"]))
            if data["laion_enabled"] == True:
                self.laion = True
                self.laion_bool.setChecked(True)
            if data["laion_enabled"] == False:
                self.laion = False
                self.laion_bool.setChecked(False)
            
            if data["plms_enabled"] == True:
                self.plms = True
                self.plms_bool.setChecked(True)
            if data["plms_enabled"] == False:
                self.plms = False
                self.plms_bool.setChecked(False)
            
            self.height_line.setText(str(data["height"]))
            self.width_line.setText(str(data["width"]))

    def save_settings(self):
        res: dict = {"seed": self.seed,
                     "plms_enabled": self.plms,
                     "ddim_steps": self.ddim_steps,
                     "laion_enabled": self.laion,
                     "height": self.height,
                     "width": self.width,
                    }

        with open(self.default_setting_path, "w") as outfile:
            json.dump(res, outfile)
        logging.info("Settings saved!")
        print(res)

    def plms_func(self, state):
        if state == QtCore.Qt.Checked:
            self.plms = True
        else:
            self.plms = False

    def new_seed(self):
        self.seed = random.randint(1, 2147483647)
        self.seed_line.setText(str(self.seed))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showNormal()

    app.exec_()

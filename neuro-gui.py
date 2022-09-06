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
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
        self.widget.moveCursor(QTextCursor.End)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Default variables
        ## image settings
        self.image_type = "txt2img"
        self.start_command = "python3 scripts/" + self.image_type + ".py --prompt"

        self.prompt = "a photograph of an astronaut riding a horse"
        self.strength = .7
        self.init_image_path = ""
        self.setBaseSize(1000, 1000)
        self.setWindowTitle("Stable Diffusion GUI")
        self.out_dir = os.path.join(os.getcwd(), "outputs")
        self.seed = random.randint(1, 2147483647)
        self.ddim_steps = 50
        self.plms = True
        self.laion = False
        self.random_seed = True
        self.height = 512
        self.width = 512
        self.image_count = 1
        self.last_image = "rickroll.jpg"
        self._setMainUi()  # setting up ui
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
        try:
            self.height_line.setText(str(int(self.height_line.text()) - int(self.height_line.text()) % 64))
            self.width_line.setText(str(int(self.width_line.text()) - int(self.width_line.text()) % 64))

            if int(self.height_line.text()) < 256:
                self.height_line.setText("256")
            if int(self.width_line.text()) < 256:
                self.width_line.setText("256")
            self.height = int(self.height_line.text())
            self.width = int(self.width_line.text())
        except:
            logging.debug("Error formatting input!")

    def _init_settings(self):
        # Initializing all elements
        self.image_type_combobox = QComboBox(self)
        self.image_type_combobox.addItem("txt2img")
        self.image_type_combobox.addItem("img2img")
        intreg = QRegExp("\\d+")
        floatreg = QRegExp("[-+]?[0-9]*\\.?[0-9]+")
        self.prompt_line = QPlainTextEdit(self)
        self.seed_line = QLineEdit(self)
        self.seed_line.setValidator(QRegExpValidator(intreg))
        self.ddim_line = QLineEdit(self)
        self.ddim_line.setValidator(QRegExpValidator(intreg))
        self.height_line = QLineEdit(self)
        self.height_line.setValidator(QRegExpValidator(intreg))
        self.width_line = QLineEdit(self)
        self.width_line.setValidator(QRegExpValidator(intreg))
        self.image_count_line = QLineEdit(self)
        self.image_count_line.setValidator(QRegExpValidator(intreg))
        self.strength_line = QLineEdit(self)
        self.strength_line.setValidator(QRegExpValidator(floatreg))

        self.plms_bool = QCheckBox("Enable plms", self)
        self.laion_bool = QCheckBox("Enable laion", self)
        self.random_seed_bool = QCheckBox("Random seed every time", self)

        self.select_init_image_button = QPushButton(self)
        self.select_init_image_button.setText("Select Init Image…")

        self.init_image_path_line = QLabel(self.init_image_path)

        self.new_seed_button = QPushButton(self)
        self.new_seed_button.setText("Randomize Seed")

        self.start_button = QPushButton(self)
        self.start_button.setText("Start!")
        self.start_button.setStyleSheet("background-color: lightgreen")

        self.save_settings_button = QPushButton(self)
        self.save_settings_button.setText("Save Settings")

        self.import_settings_button = QPushButton(self)
        self.import_settings_button.setText("Import Settings…")

        self.select_dir_button = QPushButton(self)
        self.select_dir_button.setText("Select \"outputs\" Folder…")

        self.clipboard_button = QPushButton(self)
        self.clipboard_button.setText("Copy Image to Clipboard")

        self.out_log = QLabel(self.out_dir)
        self.out_log.setMinimumWidth(500)
        # Adds all elements to right layout
        self.layout.addRow(QLabel("Type:"), self.image_type_combobox)
        self.layout.addRow(QLabel("Prompt:"), self.prompt_line)
        self.layout.addRow(QLabel("Seed:"), self.seed_line)
        self.layout.addRow(QLabel("Ddim Steps:"), self.ddim_line)
        self.layout.addRow(QLabel("Height:"), self.height_line)
        self.layout.addRow(QLabel("Width:"), self.width_line)
        self.layout.addRow(QLabel("Image Count:"), self.image_count_line)
        self.layout.addRow(QLabel("Strength:"), self.strength_line)
        self.layout.addRow(QLabel("Path to Init Image:"))
        self.layout.addRow(self.init_image_path_line)
        self.layout.addRow(self.select_init_image_button)
        self.layout.addRow(self.plms_bool, self.laion_bool)
        self.layout.addRow(self.random_seed_bool)
        self.layout.addRow(QLabel("Current \"outputs\" Folder:"))
        self.layout.addRow(self.out_log)
        self.layout.addRow(self.select_dir_button)
        self.layout.addRow(self.save_settings_button, self.import_settings_button)
        self.layout.addRow(self.new_seed_button)
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
        self.image_count_line.setText(str(self.image_count))
        self.strength_line.setText(str(self.strength))
        self.plms_bool.setChecked(self.plms)
        self.laion_bool.setChecked(self.laion)
        self.random_seed_bool.setChecked(self.random_seed)
        self.out_log.setText(self.out_dir)
        self.init_image_path_line.setText(self.init_image_path)
        for i in range(0, self.image_type_combobox.count()):
            if self.image_type_combobox.itemText(i) == self.image_type:
                self.image_type_combobox.setCurrentIndex(i)
                break

        if self.image_type == "img2img":
            self.plms_bool.setEnabled(False)
            self.height_line.setEnabled(False)
            self.width_line.setEnabled(False)
            self.strength_line.setEnabled(True)
            self.init_image_path_line.setEnabled(True)
            self.select_init_image_button.setEnabled(True)
            if not os.path.isfile(self.init_image_path):
                self.select_init_image_button.setStyleSheet("background-color: red")
                self.start_button.setEnabled(False)
            else:
                self.select_init_image_button.setStyleSheet("background-color: none")
                self.start_button.setEnabled(True)

        if self.image_type == "txt2img":
            self.plms_bool.setEnabled(True)
            self.height_line.setEnabled(True)
            self.width_line.setEnabled(True)
            self.strength_line.setEnabled(False)
            self.init_image_path_line.setEnabled(False)
            self.select_init_image_button.setEnabled(False)

    def _init_button_slots(self):
        # Initialize buttons and checkboxs
        self.start_button.clicked.connect(self.start)
        self.select_dir_button.clicked.connect(self.sel_dir)
        self.laion_bool.stateChanged.connect(self.laion_func)
        self.plms_bool.stateChanged.connect(self.plms_func)
        self.random_seed_bool.stateChanged.connect(self.random_seed_func)
        self.prompt_line.textChanged.connect(self.prompt_func)
        self.ddim_line.editingFinished.connect(self.ddim_func)
        self.image_count_line.editingFinished.connect(self.count_func)

        self.new_seed_button.clicked.connect(self.new_seed)
        self.save_settings_button.clicked.connect(self.save_settings)
        self.import_settings_button.clicked.connect(self.find_import_settings)
        self.clipboard_button.clicked.connect(self.to_clipboard)
        self.image_type_combobox.activated[str].connect(self.image_type_func)
        self.select_init_image_button.clicked.connect(self.sel_init_image)

        self.width_line.editingFinished.connect(self.make_divisible_by_64)
        self.height_line.editingFinished.connect(self.make_divisible_by_64)

    def _init_log(self):
        # Log window
        self.logTextBox = QTextEditLogger(self)
        self.logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self.logTextBox)
        logging.getLogger().setLevel(logging.DEBUG)

    def _init_left_panel(self):
        # Image and debug window
        self.label = QLabel(self)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.label)
        self._set_image()
        self._init_log()

        self.left_qsplitter = QSplitter(Qt.Orientation.Vertical)
        self.left_qsplitter.addWidget(self.scroll_area)
        self.left_qsplitter.addWidget(self.logTextBox.widget)
        self.left_panel.addWidget(self.left_qsplitter)

    def _init_right_panel(self):
        self._init_settings()
        self.formGroupBox.setLayout(self.layout)
        self.right_panel.addWidget(self.formGroupBox)

    def _init_layer_hor(self):
        self.splitter = QSplitter(self)
        self.left_widget = QWidget(self)
        self.left_widget.setLayout(self.left_panel)
        self.right_widget = QWidget(self)
        self.right_widget.setLayout(self.right_panel)
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        self.layer_hor.addWidget(self.splitter)

    def _setMainUi(self):
        self._init_layouts()
        self._init_left_panel()
        self._init_right_panel()
        self._init_layer_hor()

        self.widget.setLayout(self.layer_hor)
        self.setCentralWidget(self.widget)

    def log_subprocess_output(self, pipe):
        for line in iter(pipe.readline, b''):  # b'\n'-separated lines
            logging.info('got line from subprocess: %r', line)

    def _startImGenProcess(self, generated_command: str):
        self.start_button.setEnabled(False)
        try:
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyReadStandardOutput.connect(self.on_readyReadStandardOutput)
            self.process.finished.connect(self.process_done)
            self.process.start(generated_command)
        except:
            logging.debug(f"Error doing:\n {generated_command}!")
            self.start_button.setEnabled(True)

    def process_done(self):
        # look for the new image
        # setting up generated image.
        if int(self.image_count_line.text()) == 1:
            last_images = glob.glob(os.path.join(self.out_dir, 'samples/*'))
        else:
            last_images = glob.glob(os.path.join(self.out_dir, '*'))
        self.last_image = max(last_images, key=os.path.getctime)
        self._set_image(self.last_image)
        self.start_button.setEnabled(True)

    pyqtSlot()

    def on_readyReadStandardOutput(self):
        text = self.process.readAllStandardOutput().data().decode()
        logging.info(text)

    def start(self):
        if self.random_seed:
            self.new_seed()
        # generating command via variables
        self.start_command = "python3 scripts/" + self.image_type + ".py --prompt"
        generated_string = self.start_command + f' "{str(self.prompt_line.toPlainText())}" '

        if self.laion:
            generated_string += "--laion400m "

        if self.seed_line.text() != "":
            generated_string += "--seed " + str(self.seed_line.text()) + " "

        if self.image_count_line.text() != "" and self.image_count_line.text() != "1":
            generated_string += f"--n_iter {self.image_count_line.text()} "
            generated_string += f"--n_rows {round(int(self.image_count_line.text()) / 3) + 1} "
        else:
            generated_string += f"--n_iter 1 --skip_grid "

        if self.ddim_line.text() != "":
            generated_string += f"--ddim_steps {str(self.ddim_line.text())} "
        if self.ddim_line.text() == "":
            generated_string += f"--ddim_steps {str(self.ddim_steps)} "

        if self.image_type == "txt2img":
            if os.path.exists(os.path.join(self.out_dir, "txt2img-samples")):
                self.out_dir = os.path.join(self.out_dir, "txt2img-samples")
            if self.height_line.text() != "":
                generated_string += f"--H {self.height_line.text()} "
            if self.width_line.text() != "":
                generated_string += f"--W {self.width_line.text()} "

        if self.image_type == "img2img":
            if os.path.exists(os.path.join(self.out_dir, "img2img-samples")):
                self.out_dir = os.path.join(self.out_dir, "img2img-samples")
            self.plms = False  # not supported on img2img
            generated_string += f"--init-img \"{str(self.init_image_path)}\" --strength {(str(self.strength_line.text()))} "

        if self.plms:
            generated_string += "--plms "

        generated_string += f"--outdir {self.out_dir} "
        generated_string += "--n_samples 1"

        logging.debug(generated_string)  # output generated_string to debug window

        self._startImGenProcess(generated_string)  # Starting image generator

    def sel_dir(self):
        tmp = self.out_dir
        self.out_dir = str(QFileDialog.getExistingDirectory(self, "Select \"outputs\" Directory"))
        if not os.path.isdir(self.out_dir):
            self.out_dir = tmp
        self.out_log.setText(self.out_dir)

    def sel_init_image(self):
        tmp = self.init_image_path
        self.init_image_path, _ = QFileDialog.getOpenFileName(self, "Select an Image", ".",
                                                              "Images (*.png *.jpg *.jpeg *.gif)")
        if not os.path.isfile(self.init_image_path):
            self.init_image_path = tmp
        self.init_image_path_line.setText(str(self.init_image_path))
        self.update_form()

    def laion_func(self, state):
        self.laion = state == Qt.Checked
        self.update_form()

    def prompt_func(self):
        self.prompt = self.prompt_line.toPlainText()

    def ddim_func(self):
        self.ddim_steps = int(self.ddim_line.text())

    def count_func(self):
        self.image_count = int(self.image_count_line.text())

    def random_seed_func(self, state):
        self.random_seed = state == Qt.Checked
        self.update_form()

    def image_type_func(self, text):
        self.image_type = self.image_type_combobox.currentText()
        self.update_form()

    def strength_func(self, strength):
        self.strength = int(self.strength_line.text())
        self.update_form()

    def to_clipboard(self):
        if self.last_image != "":
            QApplication.clipboard().setImage(QImage(self.last_image))

    def find_import_settings(self):
        response = QFileDialog.getOpenFileNames(
            parent=self,
            caption='Select a data file',
            directory=os.getcwd(),
            filter="Json File (*.json)",
            initialFilter='Json File (*.json)'
        )
        if not response[0]:
            return
        self.import_settings(response[0][0])

    def import_settings(self, filename):
        print("Importing settings from ", filename)
        try:
            with open(filename) as json_file:
                data = json.load(json_file)

                # Print the type of data variable
                print("Type:", type(data))
                self.seed = int(data["seed"])
                self.ddim_steps = int(data["ddim_steps"])
                self.laion = data["laion_enabled"] is True
                self.plms = data["plms_enabled"] is True
                self.random_seed = data["random_seed_enabled"] is True
                self.height = int(data["height"])
                self.width = int(data["width"])
                self.image_count = int(data["image_count"])
                self.prompt = str(data["prompt"])
                self.out_dir = str(data["outputs_dir"])
                self.strength = float(data["strength"])
                self.init_image_path = str(data["init_image_path"])
                self.image_type = str(data["image_type"])
                self.update_form()
        except:
            message = 'Error reading settings file. Probably old. Delete it and try again'
            logging.debug(message)
            err = QErrorMessage(self)
            err.showMessage(message)

    def save_settings(self):
        res: dict = {"seed": self.seed_line.text(),
                     "plms_enabled": self.plms,
                     "ddim_steps": int(self.ddim_line.text()),
                     "laion_enabled": self.laion,
                     "height": int(self.height_line.text()),
                     "width": int(self.width_line.text()),
                     "image_count": int(self.image_count_line.text()),
                     "prompt": self.prompt_line.toPlainText(),
                     "outputs_dir": self.out_log.text(),
                     "random_seed_enabled": self.random_seed,
                     "strength": float(self.strength_line.text()),
                     "init_image_path": str(self.init_image_path),
                     "image_type": str(self.image_type)
                     }

        with open(self.default_setting_path, "w") as outfile:
            json.dump(res, outfile)
        logging.info("Settings saved!")
        print(res)

    def plms_func(self, state):
        self.plms = state == Qt.Checked

    def new_seed(self):
        self.seed = random.randint(-2147483648, 2147483647)
        self.seed_line.setText(str(self.seed))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showNormal()

    app.exec_()

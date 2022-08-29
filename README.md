# About
This program is an add-on to the [image generator](https://github.com/CompVis/stable-diffusion) using PyQt5. You can copy generate an image to the clipboard, export and import neural network settings. 

![alt text](https://github.com/blcklptn/CompVis-StableDiffusion-Gui/blob/main/screenshot_update.png)




## Install:
```sh
# Install requirements:
pip install pyqt5

# Move files
mv neuro-gui.py stable-diffusion/gui.py
```

## Create .exe:
```sh
# Create Executable file for windows:
cd stable-diffusion
pip install pyinstaller
pyinstaller --onefile gui.py

mv dist/gui ..
```

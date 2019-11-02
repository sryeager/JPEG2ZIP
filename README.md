# JPEG2ZIP
## ==> ABOUT:
This program will take in images (JPG, JPEG, JFIF, JIF, JPE, JFI), read the GPS metadata for each image and output the ZIP code where each image was taken. There is a UI associated with the program for ease of use. No command line necessary once installed or running. Do note that due to the nature of the lookup calls for the zip codes, it takes a bit of time to run the more images you select. My tests showed that 106MB worth of images took 18 seconds to finish and the application showed as not responding for part of it. If it shows it is not responding while running, just be patient as it is still running in the background.

## ==> REQUIREMENTS:
* Python 3.8.0 (latest version)
* Pyinstaller
* tkinter (included with python, no need to install. Mac users read NOTE below)
* **NOTE**: If you are using macOS 10.6 or later, the Apple supplied version of tkinter in Python has serious bugs and it is recommended to install the Python version provided by Python.org. For more information, visit https://www.python.org/download/mac/tcltk/

## ==> INSTALLATION:
1. Download this python file from Github
2. Ensure Python 3.8.0 is installed.
	
	a. To check your python version type 'python --version' in the command line.
	
	b. Python can be downloaded from https://www.python.org/downloads/
3. Install Pillow and geopy - Type 'pip install Pillow geopy'. Do note that this program will attempt to install these dependencies itself if they are not present.
4. Run the program. 'python jpeg2zip.py'

## ==> HOW TO USE:
Once you run the application, you can open a file or files by clicking *'File'*, then *'Open File(s)'* on the top menu.
Select as many images as you like (the more you select the longer it will take to process).
All successfully loaded images will populate a list showing the file paths to each file as a seperate item.
You can select as many images as you wish using control/command or shift buttons to select more than one file at a time or by clicking *'Select All'* in the *'Edit'* menu button.
With your images selected, click *'Action'* -> *'Get ZIP Codes'* in the menu and the program will give you the zip code for all the files you selected, showing 'Error' if it was unable to find one.
Enjoy!

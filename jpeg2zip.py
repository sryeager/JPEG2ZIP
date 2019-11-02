from tkinter import Frame, Tk, BOTH, Text, scrolledtext, Listbox, EXTENDED, DISABLED, NORMAL, Menu, END, filedialog, messagebox
import os
import time
try:
	from PIL import Image
	from PIL.ExifTags import TAGS, GPSTAGS
	from geopy.geocoders import Nominatim
except:
	print('Required dependencies not found. Attempting to install them now.')
	time.sleep(2)
	os.system('python -m pip install Pillow geopy')
# Re import in case they were not initially installed.
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
	

class ImageZip(Frame):

	def __init__(self, parent):
	
		# Bind Frame to self and begin UI
		Frame.__init__(self, parent)   

		self.parent = parent
		
		self.onGetZipResults = {}
		self.imagetypes = [("Image file","*.jpg"),
		("Image file","*.jpeg"),
		("Image file","*.jfif"),
		("Image file","*.jpe"),
		("Image file","*.jfi"),
		("Image file","*.jif")]
		
		self.initUI()

	def initUI(self):

		# Creating UI elements and action calls
		self.parent.title("JPEG 2 Zip Code")
		self.pack(fill=BOTH, expand=True)
		
		# Menu
		menubar = Menu(self.parent)

		fileMenu = Menu(menubar, tearoff=False)
		fileMenu.add_command(label="Open File(s)", command=self.onOpenFile)
		fileMenu.add_command(label="Exit", command=self.parent.quit)
		menubar.add_cascade(label="File", menu=fileMenu)
		
		self.editMenu = Menu(menubar, tearoff=False)
		self.editMenu.add_command(label="Select All", command=self.onSelectAll)
		self.editMenu.add_command(label="Deselect All", command=self.onDeselectAll)
		menubar.add_cascade(label="Edit", menu=self.editMenu)
		
		self.actionMenu = Menu(menubar, tearoff=False)
		self.actionMenu.add_command(label="Get ZIP Codes", command=self.onGetZIP)
		menubar.add_cascade(label="Action", menu=self.actionMenu)
		
		self.parent.config(menu=menubar)
		self.menuItemAccess(False) # Disable unneeded menu items until files loaded

		# Listbox which will hold opened file names and allow selection
		self.listboxFiles = Listbox(self.parent, selectmode=EXTENDED)
		self.listboxFiles.pack(fill=BOTH, expand=True)

	def onDeselectAll(self):
		self.listboxFiles.select_clear(0, END)

	def onSelectAll(self):
		self.listboxFiles.select_set(0, END)
		
	# Takes in boolean, TRUE = allow access, FALSE = disable access
	def menuItemAccess(self, viewable):
		if viewable == True:
			self.editMenu.entryconfig(0, state=NORMAL)
			self.editMenu.entryconfig(1, state=NORMAL)
			self.actionMenu.entryconfig(0, state=NORMAL)
		if viewable == False:
			self.editMenu.entryconfig(0, state=DISABLED)
			self.editMenu.entryconfig(1, state=DISABLED)
			self.actionMenu.entryconfig(0, state=DISABLED)

	def badImageDialog(self, badimagefiles):
	
		# Takes in a list of files and produces a warning dialog
		fileerrors = ""
		
		for file in badimagefiles:
			fileerrors += str(file) + '\n'
		messagebox.showwarning("Error Loading All Images", 
			"Not all images were found to be valid. The following files will not be loaded...\n" + fileerrors)

	def onGetZIP(self):
		
		# Produces GPS, then ZIP codes for all selected files in the UI.
		geolocator = Nominatim(user_agent="JPEG2ZIP")
		selectedfiles = self.listboxFiles.curselection()
		for item in selectedfiles:
			currentFile = self.listboxFiles.get(item)
			currentGPS = getEXIF().load(currentFile)
			print(currentGPS)
			try: 
				temp = geolocator.reverse(currentGPS)
				currentZIP = temp.raw['address']['postcode']
			
			except: # If ZIP code not found or coords are (0.0, 0.0)
				currentZIP = "Error"
			
			# Unused right now but still saved.
			# Adds {index: FileName, GPS Coords, ZIP code} to dictionary
			self.onGetZipResults.update({item: (currentFile, getEXIF().load(currentFile), currentZIP)})
			
			#Update UI
			self.listboxFiles.delete(item)
			self.listboxFiles.insert(item, currentFile + '    ' + currentZIP)
			
		#print(self.onGetZipResults)

	def onOpenFile(self):
		
		# TODO: Grab and display thumbnails with file name.
		
		fl = filedialog.askopenfilenames(filetypes = self.imagetypes)

		# Image validity check and update UI with file names
		print('Opening...')
		badimagefiles = []
		if fl != '':
			for file in fl:
				if (self.isValidJPEG(file) == True): # is valid
					print('\t' + file)
					self.listboxFiles.insert(END, file)
					
				if (self.isValidJPEG(file) == False): # is invalid
					badimagefiles.append(file)
					
		if len(badimagefiles) > 0: # push bad images to dialog box
			self.badImageDialog(badimagefiles)
			
		# Enable Menu items
		self.menuItemAccess(True)

	def isValidJPEG(self, imageFile):
	
		# TODO: use library to check validity of image. No need to reinvent the wheel.
		try:
			data = open(imageFile,'rb').read(11) #read first 11 bytes
			
			# All JPEG image files start off with SOI '0xff 0xd8'.
			# This is slightly unnecessary. See TODO above.
			if data[:2] != b'\xff\xd8': #Bad SOI
				return False
			return True
			
		except:
			print("Image Validation Error: Unable to open image " + imageFile) # sanity check (print to console)
			return False

class getEXIF():

	def __init__(self):
	
		self.exifdata = []
		
	def load(self, filelocation):
	
		# TODO: scan and extract GPS data completely manually to speed up runtime.
		# 
		# 0x8769 tag defines start of EXIF directory
		# 0x8825 is tag for GPS IFD
		#
		# Reading EXIF metadata are contained in IFD. In an IFD there are tags.
		# Each tag contain...
		# ID		Bytes 0-1		The type of tag it is.
		# Type		Bytes 2-3		1=BYTE, 2=ASCI, 3=SHORT, 4=LONG, 
		#							5=RATIONAL, 7=UNDEFINED (can take on any value), 
		#							9=SLONG,10=SRATIONAL.
		# Count		Bytes 4-7		Number of values (not no. of bytes).
		# Value		Bytes 8-11		If it can fit in 4 bytes then it is recorded there
		#							otherwise it gives offset to the starting location
		#							for the value.
		#
		# ############################################################################
		#
		# For more information on this visit....
		# https://web.archive.org/web/20170418081331/http://itbrigadeinc.com/post/2012/03/06/Anatomy-of-a-JPG-image.aspx
		# https://www.codeproject.com/Articles/47486/Understanding-and-Reading-Exif-Data
		# 
		
		image = Image.open(filelocation)

		try:
			gpsraw = image._getexif()[0x8825]
			#print('Raw GPS data: ' + str(gpsraw))
			gpsdata = self.parseGPS(gpsraw)
			#print('GPS coordinates: ' + str(gpsdata))
		except:
			print("EXIF Error: GPS data not found or corrupted for " + filelocation)
			return (0.0, 0.0)
		
		return gpsdata
		
	def parseGPS(self, data):
		# Example data recieved
		# {1: 'N', 2: ((35, 1), (3, 1), (25, 1)), 3: 'W', 4: ((92, 1), (26, 1), (59, 1))}
		#	1: = GPSLatitudeRef
		#	2: = GPSLatitude
		#	3: = GPSLongitudeRef
		#	4: = GPSLongitude
		#	5: = GPSTimeStamp
		
		#print('Parsing GPS Data')
		latRef = data.get(1)
		lat = data.get(2)
		lonRef = data.get(3)
		lon = data.get(4)
		
		#print('Converting GPS to Decimal format.')
		latitude = self.convertToDec(lat, latRef)
		longitude = self.convertToDec(lon, lonRef)
		
		return (latitude, longitude)

	def convertToDec(self, num, dir):
		try:
			#print('Starting to convert GPS to coordinate')
			deg = num[0][0] / num[0][1]
			min = num[1][0] / num[1][1] / 60.0
			sec = num[2][0] / num[2][1] / 3600.0
			
		except:
			print("Raw GPS coordinate data incomplete/corrupted/invalid.")
			return 0.0
		
		# Covering my bases for error checking. Could and should be done better.
		if dir in ['S', 'W', 's', 'w']:
			if dir not in ['N', 'E', 'n', 'e']:
				deg = -deg
				min = -min
				sec = -sec
			
		
		return round(deg + min + sec, 6)

# Runtime code starts here.
def main():
	root = Tk()
	program = ImageZip(root)
	root.geometry('500x200')
	root.mainloop()


if __name__ == '__main__':
	main()
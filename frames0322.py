from luma.core.interface.serial import spi
import luma.oled.device 
from luma.oled.device import ssd1351
from PIL import Image, ImageDraw
import time

framesize = (128,128)
actWindowSize = (128,104)
Serial = spi(device = 0, port = 0)
device = ssd1351(Serial,128,128,0,'diff_to_previous',0,0,True)
#ObjectImage = ["Sources", (SizeX,SizeY),(LocationX,LocationY)]
Logo = ["LOGO.png",(128,128),(0,0)]
Power = ["PowerFinal.png", (12,12), (114,6)]
Wifi = ["WifiIcon.png", (14,14), (97,5)]
Battery = ["BatteryIcon.png", (20,20), (2,2)]
FramesLogo = ["FramesLogo.png", (70,27), (30,90)]
Bluetooth = ["BluetoothIcon.png", (16,16) , (82,4)]
DevBar = [Power, Wifi, Battery, Bluetooth]
SplashScrn = [Logo, FramesLogo]

RunOnce = 1
#Draw Init Canvas
Canvas = Image.new("RGB", framesize, (255,255,255))


def DrawSplashScreen(Canvas):
	#Draw Image 'Canvas'
	for imageObject in SplashScrn:
		#create temp image and open the file 
		tmpimg = Image.open(imageObject[0])
		#resize image
		tmpimg = tmpimg.resize(imageObject[1])
		#convert image to RGBA if it wasnt already
		tmpimg = tmpimg.convert("RGBA")
		#paste the image on the splash with mask of the image
		Canvas.paste(tmpimg, imageObject[2], tmpimg)

def DrawDevBar(Canvas):
	draw = ImageDraw.Draw(Canvas)
	draw.rectangle((0,22,128,24),(0,0,0))
	del draw
	for imageObject in DevBar:
		tmpimg = Image.open(imageObject[0])
		tmpimg = tmpimg.resize(imageObject[1])
		tmpimg = tmpimg.convert("RGBA")
		Canvas.paste(tmpimg, imageObject[2], tmpimg)


def CheckBatt(Canvas):
	#Code for checking battery percentage
	BattX = 0
	BattMaxX = 17
	fillColor = "green"
	BattPercentage = 100
	#Just for testing because the code for checking bat percent and the calculation is not there
	BattX =15
	BattPercentage = (int)((BattX/BattMaxX) * 100)
	if(BattX < 5):
		fillColor = "red"
	elif(BattX <= 10):
		fillColor = "orange"
	else:
		fillColor = "green"

	draw = ImageDraw.Draw(Canvas)
	draw.rectangle((4,8,BattX,15), fill = fillColor)
	draw.text((24,8),str(BattPercentage) +"%",fill = "black")
	del draw


def Run():
	DrawSplashScreen(Canvas)
	DrawDevBar(Canvas)
	CheckBatt(Canvas)
	device.display(Canvas)


def Persist():
	#Dont really have to do anything here
	x = 1
Run()
while(True):
	Persist()

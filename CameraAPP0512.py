from luma.core.interface.serial import spi
from luma.core.virtual import viewport
import luma.oled.device
from luma.oled.device import ssd1351
from PIL import Image, ImageDraw
import time
import RPi.GPIO as GPIO
from datetime import datetime
import io
import sys
import time
import threading
import picamera

#TrackBall
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
Trackball = [5,6,13,19]
SW = 26
GPIO.setup(Trackball, GPIO.IN)
GPIO.setup(SW, GPIO.IN)
Trackballindex = 1
TOPINDEX = 0
Array = []

framesize = (128,128)
PicWindowSize = (128,98)
ToolBarLine = (0,98,128,100)
Serial = spi(device = 0, port = 0)
device = ssd1351(Serial,128,128,1,'diff_to_previous',0,0,True)

#Icons
BlankImage = ("framesResources/BlankImageIcon.jpg", PicWindowSize ,(0,0))
Exit = ("framesResources/ExitIcon.jpg", (24,24), (5,103) ,(4,102,29,127))
TakePic = ("framesResources/TakePicIcon.jpg", (24,24) , (54,103), (53,102,78,127))
Filler = ("framesResources/CELogo01.jpg", (1,1),(0,0),(0,0,0,0))

#Trackball arrays
CameraAppSel = [Exit, TakePic]

#Resource Draws
CameraApp = [Exit, BlankImage, TakePic]

#Screen Context
Context = "Camera"
ScreenContext = CameraApp
ScreenSelectContext = CameraAppSel
#Button Context
ButtonSel = False
BContext = Filler

#Click
ClickState = True
#Context Sensitive Menus


RunOnce = 1
def Persist():
	x = 1

#Draw Init Canvas
Canvas = Image.new("RGB", framesize, (255,255,255))

def DrawScreen(Canvas, Screen):
	global TOPINDEX
	global Array
	Array = CameraAppSel
	TOPINDEX = len(CameraAppSel)
	draw = ImageDraw.Draw(Canvas)
        #Draw Image 'Canvas'

	for imageObject in Screen:
                #create temp image and open the file
		tmpimg = Image.open(imageObject[0])
                #resize image
		tmpimg = tmpimg.resize(imageObject[1])
                #convert image to RGBA if it wasnt already
		tmpimg = tmpimg.convert("RGBA")
                #paste the image on the splash with mask of the image
		Canvas.paste(tmpimg, imageObject[2], tmpimg)
	draw.rectangle(ToolBarLine, fill = "black")
	x = 1
	device.display(Canvas)

def takePic(Canvas):
	stream = io.BytesIO()
	with picamera.PiCamera() as camera:
		time.sleep(2)
		camera.capture(stream, format='jpeg')
	stream.seek(0)
	img = Image.open(stream)
	#Create Image Destination
	destination = "FramesPics/" + datetime.today().isoformat()
	img.save(destination, "JPEG")
	img = img.resize(PicWindowSize)
	img = img.convert("RGBA")
	Canvas.paste(img, (0,0), img)
	device.display(Canvas)

def upCallback(channel):
	global Trackballindex
	global Canvas
	global Array
	global TOPINDEX
	global BContext
	CurIndex = 0
	PrevIndex = 0
	Trackballindex += 1
	if(Trackballindex > TOPINDEX):
		Trackballindex = 0
		CurIndex = Trackballindex
		PrevIndex = TOPINDEX
	else:
		CurIndex = Trackballindex
		PrevIndex = Trackballindex - 1

		CurImage = Array[CurIndex]
		BContext = CurImage
		PrevImage = Array[PrevIndex]
		SelectionBox(Canvas, PrevImage, CurImage)
	print("up call back fired")

def downCallback(channel):
	global Trackballindex
	global Canvas
	global Array
	global TOPINDEX
	global BContext
	CurIndex = 0
	PrevIndex = 0
	Trackballindex -=1
	if(Trackballindex < 0):
		Trackballindex = TOPINDEX - 1
		CurIndex = Trackballindex
		PrevIndex = 0
	else:
		CurIndex = Trackballindex
		PrevIndex = Trackballindex + 1

	CurImage = Array[CurIndex]
	BContext = CurImage
	PrevImage = Array[PrevIndex]
	SelectionBox(Canvas, PrevImage, CurImage)
	print("Down Call Back Fired")

def clickCallback(channel):
	global BContext
	print("Click call back fired")
	checkButton(BContext)

def SelectionBox(Canvas, PrevImage, CurImage):
	draw = ImageDraw.Draw(Canvas)
	#Erase the Selection Box around the old image
	draw.rectangle(PrevImage[3], fill = "white")
	#Repaste the old image
	tmpPrev = Image.open(PrevImage[0])
	tmpPrev = tmpPrev.resize(PrevImage[1])
	tmpPrev = tmpPrev.convert("RGBA")
	tmpPrev.putalpha(255)
	Canvas.paste(tmpPrev, PrevImage[2], tmpPrev)
	#Draw Box Around New Image
	draw.rectangle(CurImage[3], fill = "purple")
	#Paste new Image on top of selection box
	tmpCur = Image.open(CurImage[0])
	tmpCur = tmpCur.resize(CurImage[1])
	tmpCur = tmpCur.convert("RGBA")	
	tmpCur.putalpha(255)
	Canvas.paste(tmpCur, CurImage[2], tmpCur)
	device.display(Canvas)

def DisableClick():
	GPIO.remove_event_detect(SW)
	global ClickState
	ClickState = False

def EnableClick():
	GPIO.add_event_detect(SW, GPIO.RISING)
	GPIO.add_event_callback(SW, clickCallback)
	global ClickState
	ClickState = True

def checkButton(BContext):
	global ScreenSelectContext
	global ScreenContext
	global Context
	global Trackballindex
	if(BContext == TakePic):
		takePic(Canvas)
	if(BContext == Exit):
		exit()
	Trackballindex = 0

def Setup():
	DrawScreen(Canvas, CameraApp)
	device.display(Canvas)
	global Trackball
	GPIO.add_event_detect(Trackball[0],GPIO.FALLING)
	GPIO.add_event_detect(Trackball[1],GPIO.FALLING)
	GPIO.add_event_detect(Trackball[2],GPIO.FALLING)
	GPIO.add_event_detect(Trackball[3],GPIO.FALLING)
	GPIO.add_event_detect(SW,GPIO.RISING)
	GPIO.add_event_callback(SW, clickCallback)
	GPIO.add_event_callback(Trackball[0], upCallback)
	GPIO.add_event_callback(Trackball[2], downCallback)


Setup()
if __name__ == '__main__':
	try:
		while(True):
			Persist()
	except KeyboardInterrupt:
		device.hide()
		GPIO.cleanup()


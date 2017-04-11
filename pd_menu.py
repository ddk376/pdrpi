#!/usr/bin/python
# Import necessary modules
import Adafruit_CharLCD as LCD
from time import sleep
import subprocess
import os

# Initialize variable
base_path = '/media/pi'
pd_files  = None
pos       = 0
media     = None
opened_pd = None

# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()

# Set Background Color to green
lcd.set_color(0.0, 1.0, 0.0)

# Create special char better description
lcd.create_char(1, [8, 12, 10, 9, 10, 12, 8, 0]) # right arrow
lcd.create_char(2, [2, 6, 10, 18, 10, 6, 2, 0])  # left arrow
lcd.create_char(3, [0, 1, 3, 22, 28, 8, 0, 0])   # Check mark

# Functions to clean up control flow
def message(msg, time = 1.0):
    """wrapper for lcd.message() """
    lcd.clear()
    if len(msg) > 16: msg = msg[0:16] + "\n" + msg[16:]
    lcd.message(msg)
    sleep(time)

def clear(exiting = False):
    """clears display and sets background color to no color """
    lcd.clear()
    lcd.set_color(0,0,0)
    if exiting: exit()

def get_files():
    """  Returns a list of '.pd' files and directories """
    return [ file for file in os.listdir('.') if file[0] != '.' and ((file[-3:]) == '.pd' or os.path.isdir(file))]

def display(file):
    """ Display the puredata file or a directory. If a directory is displayed a right arrow is also displayed """
    lcd.clear()
    display = file
    if len(file) > 16: display = file[0:16] + "\n" + file[16:] 
    if os.path.isdir(pd_files[pos]):
        display += " \x01"
    lcd.message(display)

def open_puredata_file(file):
   """ Closes current puredata file and opens puredata file given in the argument"""
   global opened_pd
   if opened_pd is not None: close_puredata_file()
   message("Opening " + file, 2.0)
   #opened_pd = subprocess.Popen("exec /usr/bin/pd -noadc -alsa " + file, shell=True)
   os.system('/usr/bin/pd -noadc -alsa ' + file)
   message(str(opened_pd), 2.0)
   display(file)

def close_puredata_file():
   """ Closes puredata file """
   opened_pd.kill()
                                                                     
def chdir(dir):
    """ Changes directory """
    global pd_files, pos
    os.chdir(dir)
    pd_files = get_files()
    pos = 0
    lcd.clear()
    if len(pd_files) == 0: lcd.message("\x02 No files")
    else: display(pd_files[pos])

def exit_program():
    """ Exits the program with confirmation"""
    message('Exit program?\nYes \x03 No')
    ans = True
    while True:
       if lcd.is_pressed(LCD.RIGHT):
           ans = False
           message('Exit program?\nYes   No \x03')
       elif lcd.is_pressed(LCD.LEFT):
           ans = True
           message('Exit program?\nYes \x03  No')
       elif lcd.is_pressed(LCD.SELECT):
           if ans: clear(True)
           chdir('.')
           break

# Select USB drive
message('Locating USB\ndrives...', 1.0)
medias = os.listdir(base_path)
medias.remove('SETTINGS')                      # We do not want this to show up as part of available medias to choose from

# Exit if no USB is present. Sets media to USB if only one USB is present and informs user to select a USB if multiple USB are present
if len(medias) > 1:
    message('Please select\nUSB...', 1.0)
    pos = 0
    while True:
        if lcd.is_pressed(LCD.UP):
            if pos > 0:
                pos -= 1
                message(medias[pos])
        elif lcd.is_pressed(LCD.DOWN):
            if pos < len(medias) - 1:
                pos += 1
                message(medias[pos])
        elif lcd.is_pressed(LCD.LEFT): exit_program()
        elif lcd.is_pressed(LCD.RIGHT) or lcd.is_pressed(LCD.SELECT):
            media = medias[pos]
            break
        else: pass
elif len(medias) == 1:
    media = medias[0]
    message("Entering \n" + media, 1.0)
else:
    message('No USB Found...')
    message('Exiting...')
    clear(True)

lcd.clear()

# Gets all the files to choose from
path = base_path + '/' + media
chdir(path)

# Navigates through the usb drive using the LCD buttons
while True:
    if lcd.is_pressed(LCD.LEFT):
        sleep(0.5)
        if os.getcwd() == base_path+ '/'+ media: pass
        else: chdir('..')  # path of one level up from current directory
    elif lcd.is_pressed(LCD.UP):
        if pos != 0:
            pos -= 1
            display(pd_files[pos])
    elif lcd.is_pressed(LCD.DOWN):
        if pos != len(pd_files) - 1:
            pos += 1
            display(pd_files[pos])
    elif lcd.is_pressed(LCD.RIGHT) or lcd.is_pressed(LCD.SELECT):
        if os.path.isdir(pd_files[pos]):
	    chdir(pd_files[pos])
            sleep(2.0)
        else: open_puredata_file(pd_files[pos])
    else: pass   

clear(True)


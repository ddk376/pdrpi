#!/usr/bin/python
# Import necessary modules
import Adafruit_CharLCD as LCD
from time import sleep
from subprocess import call
import os

# Initialize variable
base_path = '/media/pi'
pd_files  = None
pos       = 0
media     = None

# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()

# Create arrow char for folder
lcd.create_char(1, [8, 12, 10, 9, 10, 12, 8,  0]) # right arrow
lcd.create_char(2, [0, 1, 3, 22, 28, 8, 0, 0])    # Check mark

# Select USB drive
lcd.clear()
lcd.message('Locating USB\ndrives...')
sleep(1.0)
medias = os.listdir(base_path)
medias.remove('SETTINGS')                      # We do not want this to show up as part of available medias to choose from

# Exit if no USB is present. Sets media to USB if only one USB is present and informs user to select a USB if multiple USB are present
if len(medias) > 1:
    lcd.clear()
    lcd.message('Please select\nUSB...')
    sleep(1.0)
    break
elif len(medias) == 1:
    media = medias[0]
else:
    lcd.clear()
    lcd.message('No USB Found...')
    sleep(2.0)
    lcd.clear()
    lcd.message('Exiting...')
    sleep(1.0)
    lcd.set_color(0,0,0)
    exit()

# Functions to clean up control flow
def get_files(pwd):
    """  Returns a list of '.pd' files and directories """
    return [ file for file in os.listdir(pwd) if file[0] != '.' and (file[-3:) == '.pd' or os.path.isdir(file)]

def display(file):
    """ Display the puredata file or a directory. If a directory is displayed a right arrow is also displayed """
    file_or_dir = pwd + '/' + pd_files[pos]
    if os.path.isdir(file_or_dir):
        file_or_dir += " \x01"
    lcd.message(file_or_dir)

def open_puredata_file(file):
   """ Opens puredata file"""
   lcd.clear()
   lcd.message("Opening " + file)
   sleep(2.0)
   call("puredata", "-nogui", pwd + '/' + file )
   display(file)

def chdir(path):
    """ Changes directory """
    global pwd, pd_files, pos
    os.chdir(path)
    pwd = path
    pd_files = get_files(pwd)
    pos = 0
    lcd.clear()
    display(pd_files[pos]) 

def exit_program():
    """ Exits the program with confirmation"""
    lcd.clear()
    lcd.message('Exit program?\nYes \x02 No')
    ans = True
    while True:
       if lcd.is_pressed(LCD.RIGHT):
           ans = False
           lcd.clear()
           lcd.message('Exit program?\nYes   No \x02')
       elif lcd.is_pressed(LCD.LEFT):
           ans = True
           lcd.clear()
           lcd.message('Exit program?\nYes \x02 No')
       elif lcd.is_pressed(LCD.SELECT):
           if ans:
               lcd.clear()
               lcd.set_color(0,0,0)
               break
           else: pass

# Testing purposes
#lcd.clear()
#exit_program()

lcd.clear()

# Gets all the files to choose from
path = base_path
if media is not None: path += '/' + media
chdir(path)

# Navigates through the usb drive using the LCD inputs
while True:
    if lcd.is_pressed(LCD.LEFT):
        if os.getcwd() == base_path + media: exit_program()
        else: 
            path  = '/'.join(pwd.split('/')[:-1])
            chdir(path)
    elif lcd.is_pressed(LCD.RIGHT):
        if os.path.isdir(pwd + '/' + pd_files[pos]): chdir(pwd + '/' + pd_files[pos])
        else:                                        open_puredata(pd_files[pos])
    elif lcd.is_pressed(LCD.UP):
        if pos != 0:
            pos = pos -1
            display(pd_files[pos])
    elif lcd.is_pressed(LCD.DOWN):
         if pos != len(pd_files) - 1:
             pos = pos + 1
             display(pd_files[pos])
    else:
       if os.path.isdir(pwd + '/' + pd_files[pos] ): chdir(pwd + '/' + pd_files[pos])
       else:                                         open_puredata(pd_ls[pos])   

lcd.clear()
lcd.set_color(0,0,0)
exit()


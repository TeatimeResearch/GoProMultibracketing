# Automated still image bracketing for multi-GoPro rigs

This was a tool developed in a hurry for a specific use-case and is not meant to be a supported well formed utility.
I do not have constant access to GoPro rigs so this project is entirely unsupported.
That said, feel free to use this for whatever.

## Setup
- install python3
- install openv ( *pip install opencv-python* )
- install gopro api ( *pip install goprocam* or https://github.com/KonradIT/gopro-py-api )
- configure wifi on your gopros
- connect your computer to each at least once
- add gopro SSID names in the cameralist array
- turn on all gopros
- set writeMacs=True to get mac addresses
- run *python omnibracketing.py* and it'll take a bunch of pictures for testing (and get your camera macs)
- copy camera macs from cameraMacs.txt to cameraMacs array
- turn writeMacs=False and set any settings you want

## Usage
- just run with *python omnibracketing.py*

## Requirements
- Windows
  - only for the wifi network commands - you could easily port this to your environment
- Python 3
- OpenCV
  - only for image preview
- GoPro API
- GoPro cameras
  - tested with HERO4 black
  - for others see api call support and adjust accordingly; https://github.com/KonradIT/gopro-py-api

## Known issues
- slow
  - wifi connections are always slow :(
  - for a more permanent solution i would just rig a raspberry pi to hub everything physically
- sometimes wifi fails to connect
  - just connect manually and script should resume
  - also gopro firmware is garbage and occationally turns off wifi for no reason so check for that
- if anything goes wrong with the connection, the script will just print garbage on the screen forever
  - this has a lot to do with poor error management on gopro-api side
  - just ctrl+c out of execution or use taskmanager to kill the process and try again


# Automated still image bracketing for multi-GoPro rigs

This was a tool developed in a hurry for a specific use-case and is not meant to be a supported well formed utility.
I do not have constant access to GoPro rigs so this project is entirely unsupported.
That said, feel free to use this for whatever.

Requirements;
- Windows
  - only for the wifi network commands - you could easily port this to your environment
- Python 3
  - required by gopro api
- GoPro API
  - just install by: *pip install goprocam*
  - or get from project site https://github.com/KonradIT/gopro-py-api
- GoPro cameras
  - tested with HERO4 black
  - for others see api call support and adjust accordingly; https://github.com/KonradIT/gopro-py-api

Known issues:
- sometimes wifi fails to connect
  - just connect manually and script should resume
  - also gopro firmware is garbage and occationally turns off wifi for no reason so check for that
- if anything goes wrong with the connection, the script will just print garbage on the screen forever
  - this has a lot to do with poor error management on gopro-api side
  - just ctrl+c out of execution or use taskmanager to kill the process and try again


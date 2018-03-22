import os
import datetime
import time
from goprocam import GoProCamera
from goprocam import constants
from subprocess import check_output
import cv2

####### options

# do we even want to take photos? - disable if you just want to set settings
takePhotos = True
# take bracketing images ( configured below )
useBracketing = True
# show downloaded images ( might cause a few second delay as image is loaded )
preview = True

# set video settings
setVideoMode = False
videoDuration = 120

# delete camera contents after image download ( also stuff that was there earlier like videos! )
deleteAll = False
# enter standby after taking photos ( saves battery, leaves wifi on and can wake up the next time you need it )
powerOff = True
# write camera mac addresses into a file - only need to do
writeMacs = False

beepWhenDone = True

# what brackets to take
brackets = [
    (constants.Photo.EvComp.M2, "m2"),
    (constants.Photo.EvComp.Zero, "o"),
    (constants.Photo.EvComp.P2, "p2")
]

# wifi ssids of your cameras - connect to them at least once on this machine so you have their profile and passwords in the system
cameralist = []
cameralist.append("1")
cameralist.append("2")
cameralist.append("3")
cameralist.append("4")
cameralist.append("5")
cameralist.append("6")

# camera mac addresses - needed for wake-on-lan functionality
camsMacs = []
camsMacs.append("d4d91990b852")
camsMacs.append("d4d91990cabf")
camsMacs.append("d4d91990b159")
camsMacs.append("d4d91990ace9")
camsMacs.append("d4d91990c0d8")
camsMacs.append("d4d91990b6aa")

wifidevicename = "Wi-Fi"

######### init
startTime = int(datetime.datetime.now().timestamp())
cam = False
batteryStatus = []

# force refresh wifi - requires to run as admin
#check_output('netsh interface set interface name="'+wifidevicename+'" admin=disabled', shell=True)
#time.sleep(1)
#check_output('netsh interface set interface name="'+wifidevicename+'" admin=enabled', shell=True)
#time.sleep(1)


ssids = []
wlanstdout = check_output("netsh wlan show networks", shell=True)  # list networks
for line in wlanstdout.decode().splitlines():
    if ("SSID " in line):
        trash, ssid = line.split(":")
        ssid = ssid.strip()
        ssids.append(ssid)

okToGo = True
for cameraname in cameralist:
    if (cameraname not in ssids):
        print("camera " + cameraname + " not found!")
        okToGo = False

if (not okToGo):
    exit()

shotid = str(int(datetime.datetime.now().timestamp()))
os.makedirs(shotid)

if writeMacs:
    cameraMacs = open("cameraMacs.txt", "w")

######## start connecting stuff

for cameraname, cameraMac in zip(cameralist, camsMacs):
    print("connecting to camera " + cameraname)

    # wlan connection - very windows specific
    wlanstdout = check_output("netsh wlan connect " + cameraname, shell=True)  # connect wifi
    connected = False
    while (not connected):
        wlanstdout = check_output("netsh interface show interface", shell=True)  # check if connected
        for line in wlanstdout.decode().splitlines():
            if (wifidevicename in line and "Connected" in line):
                # print("yup")
                connected = True
                break
            else:
                # print("nope")
                connected = False

    print("connected")
    time.sleep(1)

    if (cameraMac == ""):
        cam = GoProCamera.GoPro(constants.gpcontrol)
    else:
        print("wake up " + cameraMac)
        cam = GoProCamera.GoPro(constants.gpcontrol, mac_address=cameraMac)

    #cam.power_on()

    if (takePhotos):
        cam.gpControlSet(constants.Setup.BEEP, constants.Setup.Beep.OFF)

        cam.mode(constants.Mode.PhotoMode, constants.Mode.SubMode.Photo.Single)
        cam.gpControlSet(constants.Photo.ISO_LIMIT, constants.Photo.IsoLimit.ISO100)
        cam.gpControlSet(constants.Photo.ISO_MIN, constants.Photo.IsoLimit.ISO100)
        if (useBracketing):
            cam.gpControlSet(constants.Photo.PROTUNE_PHOTO, constants.Photo.ProTune.ON)
            for bracket in brackets:
                print("Bracket: " + bracket[1])
                #cam.mode(constants.Mode.PhotoMode,constants.Mode.SubMode.Photo.Single) # nightmode useful?
                cam.gpControlSet(constants.Photo.EVCOMP, str(bracket[0]))
                time.sleep(2)
                filename = cam.take_photo(0)
                #print(filename)
                path, file = filename.split("/")[-2:]
                #print(path,file)
                targetfile = shotid + "\hdr_cam" + cameraname + "_ev" + bracket[1] + ".jpg"
                cam.downloadMedia(path, file, custom_filename=targetfile)
                # cam.downloadLastMedia(cam.take_photo(0),custom_filename=targetfile)
                if (preview):
                    img = cv2.imread(targetfile)
                    img = cv2.resize(img, (800, 600), interpolation=cv2.INTER_NEAREST)
                    cv2.imshow("Image", img)
                    cv2.waitKey(1)
        else:
            #cam.gpControlSet(constants.Photo.PROTUNE_PHOTO, constants.Photo.ProTune.OFF)
            cam.gpControlSet(constants.Photo.PROTUNE_PHOTO, constants.Photo.ProTune.ON)
            cam.gpControlSet(constants.Photo.EVCOMP, str(constants.Photo.EvComp.Zero))
            time.sleep(1)
            filename = cam.take_photo(0)
            path, file = filename.split("/")[-2:]
            targetfile = shotid + "\cam" + cameraname + ".jpg"
            cam.downloadMedia(path, file, custom_filename=targetfile)
            if (preview):
                img = cv2.imread(targetfile)
                img = cv2.resize(img, (800, 600), interpolation=cv2.INTER_NEAREST)
                cv2.imshow("Image", img)
                cv2.waitKey(1)

    if (setVideoMode):
        # todo? video was not important for us
        cam.mode(constants.Mode.VideoMode, constants.Mode.SubMode.Video.Video)
        cam.gpControlSet(constants.Video.PROTUNE_VIDEO, constants.Video.ProTune.ON)
        cam.gpControlSet(constants.Video.EVCOMP, constants.Video.EvComp.Zero)
        cam.gpControlSet(constants.Video.ISO_LIMIT, constants.Video.IsoLimit.ISO100)
        cam.gpControlSet(constants.Video.ISO_MODE, constants.Video.IsoMode.Max)
        #constants.Video.ProTune.ON
        print("starting video for " + str(videoDuration))
        #cam.video_settings(constants.Video. asdfasdf)
        #cam.shoot_video(videoDuration)

    if (deleteAll):
        cam.delete("all")

    if writeMacs:
        cameraMacs.write(cam.infoCamera(constants.Camera.MacAddress) + "\n")

    #cam.gpControlSet(constants.Setup.BEEP,constants.Setup.Beep.SemiLoud)

    batteryStatus.append(
        cam.parse_value("battery", cam.getStatus(constants.Status.Status, constants.Status.STATUS.BatteryLevel)))

    if (beepWhenDone and cameraname==cameralist[len(cameralist)-1]):
        cam.locate(constants.Locate.Start)
        time.sleep(1)
        cam.locate(constants.Locate.Stop)

    if powerOff:
        cam.power_off()

if writeMacs:
    cameraMacs.close()

endTime = int(datetime.datetime.now().timestamp())
print("done.. took " + str(endTime - startTime) + " seconds...")

for camera, battStatus in zip(cameralist, batteryStatus):
    print(camera + " battery status: " + str(battStatus))

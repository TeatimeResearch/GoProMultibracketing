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
startVideo = False
videoDuration = 0

downloadVideos = False

# delete camera contents after image download ( also stuff that was there earlier like videos! )
deleteAll = False
# enter standby after taking photos ( saves battery, leaves wifi on and can wake up the next time you need it )
powerOff = True

# write camera mac addresses into a file - only need to do once
writeMacs = False

beepWhenDone = True

# what brackets to take
brackets = [
    (constants.Photo.EvComp.P2, "p2"), # bright
    (constants.Photo.EvComp.Zero, "o"),
    (constants.Photo.EvComp.M2, "m2"), # dark
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

powerOff=powerOff and not startVideo # do not turn off if we're starting video!

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
if (takePhotos):
    os.makedirs(shotid)

if writeMacs:
    cameraMacs = open("cameraMacs.txt", "w")

######## start connecting stuff

for cameraname, cameraMac in zip(cameralist, camsMacs):
    print("connecting to camera " + cameraname)

    # wlan connection - very windows specific
    # you can use 'netsh wlan connect ssid="ssidname" key="yourpassword"' but safer to first connect manually
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
        cam.gpControlSet(constants.Photo.RESOLUTION, constants.Photo.Resolution.R12W)

        if (useBracketing):
            cam.gpControlSet(constants.Photo.PROTUNE_PHOTO, constants.Photo.ProTune.ON)

            for bracket in brackets:
                print("Bracket: " + bracket[1])
                #cam.mode(constants.Mode.PhotoMode,constants.Mode.SubMode.Photo.Single) # nightmode useful?
                cam.gpControlSet(constants.Photo.EVCOMP, str(bracket[0]))
                # todo: this is unreliable for some damn reason - find a way to check if setting actually has been applied?
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
                    cv2.waitKey(100)

            cam.gpControlSet(constants.Photo.EVCOMP, str(brackets[0][0])) # reset because it's so damn unreliable
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
                cv2.waitKey(100)

    if (startVideo):
        cam.shutter(constants.stop) # stop in case still recording

        cam.mode(constants.Mode.VideoMode, constants.Mode.SubMode.Video.Video)
        cam.gpControlSet(constants.Video.PROTUNE_VIDEO, constants.Video.ProTune.ON)
        cam.gpControlSet(constants.Video.EVCOMP, constants.Video.EvComp.Zero)
        cam.gpControlSet(constants.Video.ISO_LIMIT, constants.Video.IsoLimit.ISO400)
        cam.gpControlSet(constants.Video.ISO_MODE, constants.Video.IsoMode.Max)
        #cam.gpControlSet(constants.Video.VIDEO_EIS, constants.Video.VideoEIS.ON) #what even is this
        #todo: video exposure???
        #cam.gpControlSet("73","1") #exposure from nodejs project - doesn't seem to work
        #cam.gpControlSet("73","23")
        cam.gpControlSet(constants.Video.RESOLUTION, constants.Video.Resolution.R4k)

        print("starting video for " + str(videoDuration))
        time.sleep(1)
        #cam.video_settings(constants.Video. asdfasdf)
        cam.shoot_video(videoDuration)
        #cam.shutter(constants.start)

    if downloadVideos:
        cam.shutter(constants.stop) # stop in case still recording
        time.sleep(1)

        mediaList=cam.listMedia(True,True)
        for file in mediaList:
            if file[1].endswith('MP4'):
                print(file[0]+'/'+file[1]+'   '+str(int(int(file[2])/1024/1024))+'M')
                cam.downloadMedia(file[0],file[1])
                os.rename(file[1],"cam" + cameraname +"_"+file[1])

    if deleteAll:
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
        cam.shutter(constants.stop)
        time.sleep(1)
        cam.power_off()

if writeMacs:
    cameraMacs.close()

endTime = int(datetime.datetime.now().timestamp())
print("done.. took " + str(endTime - startTime) + " seconds...")

for camera, battStatus in zip(cameralist, batteryStatus):
    print(camera + " battery status: " + str(battStatus))

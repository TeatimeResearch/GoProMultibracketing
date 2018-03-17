import os
import datetime
import time
import urllib.request
from goprocam import GoProCamera
from goprocam import constants
from subprocess import check_output
import cv2

####### options

takePhotos=True
useBracketing=True
preview=False
deleteAll=True
powerOff=True
writeMacs=False

brackets=[
    (constants.Photo.EvComp.M2,"m2"),
    (constants.Photo.EvComp.Zero,"o"),
    (constants.Photo.EvComp.P2,"p2")
]

cameralist=[]
cameralist.append("1")
cameralist.append("2")
cameralist.append("3")
cameralist.append("4")
cameralist.append("5")
cameralist.append("6")

camsMacs=[]
camsMacs.append("d4d91990b852")
camsMacs.append("d4d91990cabf")
camsMacs.append("d4d91990b159")
camsMacs.append("d4d91990ace9")
camsMacs.append("d4d91990c0d8")
camsMacs.append("d4d91990b6aa")

wifidevicename="Wi-Fi"

######### init
startTime=int(datetime.datetime.now().timestamp())
shotid=str(int(datetime.datetime.now().timestamp()))
os.makedirs(shotid)
cam = False

# force refresh wifi
#check_output('netsh interface set interface name="'+wifidevicename+'" admin=disabled', shell=True)
#time.sleep(1)
#check_output('netsh interface set interface name="'+wifidevicename+'" admin=enabled', shell=True)
#time.sleep(1)
#check_output('netsh wlan disconnect', shell=True)
#time.sleep(1)


ssids=[]
wlanstdout = check_output("netsh wlan show networks", shell=True) # list networks
for line in wlanstdout.decode().splitlines():
    if ("SSID " in line):
        trash, ssid=line.split(":")
        ssid=ssid.strip()
        ssids.append(ssid)

okToGo=True
for cameraname in cameralist:
    if (cameraname not in ssids):
        print("camera "+cameraname+" not found!")
        okToGo=False

if (not okToGo):
    exit()

batteryStatus=[]

if writeMacs:
    cameraMacs=open("cameraMacs.txt","w")

######## start connecting stuff

for cameraname, cameraMac in zip(cameralist, camsMacs):
    print("connecting to camera "+cameraname)
    wlanstdout=check_output("netsh wlan connect "+cameraname,shell=True) # connect wifi

    connected=False
    while (not connected):
        wlanstdout=check_output("netsh interface show interface", shell=True) # check if connected
        for line in wlanstdout.decode().splitlines():
            if (wifidevicename in line and "Connected" in line):
                #print("yup")
                connected=True
                break
            else:
                #print("nope")
                connected=False

    print("connected")
    time.sleep(1)

    if (cameraMac==""):
        cam = GoProCamera.GoPro(constants.gpcontrol)
    else:
        print("wake up "+cameraMac)
        cam = GoProCamera.GoPro(constants.gpcontrol, mac_address=cameraMac)

    #cam.power_on()

    if (takePhotos):
        cam.gpControlSet(constants.Setup.BEEP,constants.Setup.Beep.OFF)

        #break

        cam.mode(constants.Mode.PhotoMode,constants.Mode.SubMode.Photo.Single)
        cam.gpControlSet(constants.Photo.ISO_LIMIT,constants.Photo.IsoLimit.ISO100)
        cam.gpControlSet(constants.Photo.ISO_MIN,constants.Photo.IsoLimit.ISO100)
        if (useBracketing):
            cam.gpControlSet(constants.Photo.PROTUNE_PHOTO, constants.Photo.ProTune.ON)
            for bracket in brackets:
                print("Bracket: "+bracket[1])
                #cam.mode(constants.Mode.PhotoMode,constants.Mode.SubMode.Photo.Single) # nightmode useful?
                cam.gpControlSet(constants.Photo.EVCOMP,str(bracket[0]))
                time.sleep(2)
                filename=cam.take_photo(0)
                #print(filename)
                path,file=filename.split("/")[-2:]
                #print(path,file)
                targetfile = shotid+"\hdr_cam"+cameraname+"_ev"+bracket[1]+".jpg"
                cam.downloadMedia(path,file,custom_filename=targetfile)
                #cam.downloadLastMedia(cam.take_photo(0),custom_filename=targetfile)
                if (preview):
                    img=cv2.imread(targetfile)
                    img=cv2.resize(img,(800,600),interpolation=cv2.INTER_NEAREST)
                    cv2.imshow("Image",img)
                    cv2.waitKey(1)
        else:
            cam.gpControlSet(constants.Photo.PROTUNE_PHOTO, constants.Photo.ProTune.OFF)
            time.sleep(1)
            filename = cam.take_photo(0)
            path, file = filename.split("/")[-2:]
            targetfile=shotid + "\cam" + cameraname +".jpg"
            cam.downloadMedia(path, file, custom_filename=targetfile)
            if (preview):
                img = cv2.imread(targetfile)
                img = cv2.resize(img, (800, 600), interpolation=cv2.INTER_NEAREST)
                cv2.imshow("Image", img)
                cv2.waitKey(1)

    if (deleteAll):
        cam.delete("all")

    if writeMacs:
        cameraMacs.write(cam.infoCamera(constants.Camera.MacAddress)+"\n")

    #cam.gpControlSet(constants.Setup.BEEP,constants.Setup.Beep.SemiLoud)

    batteryStatus.append(cam.parse_value("battery", cam.getStatus(constants.Status.Status, constants.Status.STATUS.BatteryLevel)))

    if powerOff:
        cam.power_off()

if writeMacs:
    cameraMacs.close()

endTime=int(datetime.datetime.now().timestamp())
print("done.. took "+str(endTime-startTime)+" seconds...")

for camera,battStatus in zip(cameralist,batteryStatus):
    print(camera+" battery status: "+str(battStatus))


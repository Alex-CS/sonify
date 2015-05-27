import XboxController
from time import strftime
import time

start = int(round(time.time() * 1000))
#global f
#f = open('output.txt','w')

def controller_event(controlId, value):
    current = int(round(time.time() * 1000))
    elapsed = current - start
    t = "Time:"+str(elapsed)+";\n"
    
    #defaults
    wButtons = "wButtons:[];\n"
    bLeftTrigger = "bLeftTrigger:0;\n"
    bRightTrigger = "bRightTrigger:0;\n"
    sThumbLX = "sThumbLX:0;\n"
    sThumbLY = "sThumbLY:0;\n"
    sThumbRX = "sThumbRX:0;\n"
    sThumbRY = "sThumbRY:0;"

    #joysticks
    if controlId == 0:
        sThumbLX = "sThumbLX:"+str(value)+";\n"
    elif controlId == 1:
        sThumbLY = "sThumbLY:"+str(value)+";\n"
    elif controlId == 2:
        sThumbRX = "sThumbRX:"+str(value)+";\n"
    elif controlId == 3:
        sThumbRY = "sThumbRY:"+str(value)+";"
    elif controlId == 4:
        val = int(round(value*255,0))
        bRightTrigger = "bRightTrigger:"+str(val)+";\n"
    elif controlId == 5:
        val = int(round(value*255,0))
        bLeftTrigger = "bLeftTrigger:"+str(val)+";\n"
    
    #dpad
    elif controlId == 17:
        if value == (0,1):
            wButtons = "wButtons:[0x0001,];\n"
        elif value == (1,0):
            wButtons = "wButtons:[0x0008,];\n"
        elif value == (0,-1):
            wButtons = "wButtons:[0x0002,];\n"
        elif value == (-1,0):
            wButtons = "wButtons:[0x0004,];\n"
        else:
            pass
    
    #y,b,a,x
    elif controlId == 9:
        wButtons = "wButtons:[0x8000,];\n"
    elif controlId == 7:
        wButtons = "wButtons:[0x2000,];\n"
    elif controlId == 6:
        wButtons = "wButtons:[0x1000,];\n"
    elif controlId == 8:
        wButtons = "wButtons:[0x4000,];\n"

    #lb,rb
    elif controlId == 10:
        wButtons = "wButtons:[0x0100,];\n"
    elif controlId == 11:
        wButtons = "wButtons:[0x0200,];\n"

    #start,back
    elif controlId == 12:
        wButtons = "wButtons:[0x0020,];\n"
    elif controlId == 13:
        wButtons = "wButtons:[0x0010,];\n"

    #left thumb, right thumb  
    elif controlId == 15:
        wButtons = "wButtons:[0x0040,];\n"
    elif controlId == 16:
        wButtons = "wButtons:[0x0080,];\n"

    else:
        pass
    
    print t, wButtons, bLeftTrigger, bRightTrigger, sThumbLX, sThumbLY, sThumbRX, sThumbRY
    print "$;"
    #print "Control id = {}, Value = {}".format(controlId, value)

xboxCont = XboxController.XboxController(
    controllerCallBack = controller_event,
    joystickNo = 0,
    deadzone = 0.1,
    scale = 1,
    invertYAxis = False)

# dont use ctrl+c to stop, XboxController thread has to be stopped manually.
# enter 's' to start listening, 'q' to stop
while True:
    key = raw_input("")
    if key == "s":
        xboxCont.start()
    elif key == "q":
        xboxCont.stop()
        #f.close()
        break
        


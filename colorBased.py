import numpy as np 
import cv2
# import pyfirmata
import cvzone


gambar= cv2.imread("test.jpg")
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# port = "COM3" 
# board = pyfirmata.Arduino(port)
# servo_pinX = board.get_pin('d:5:s') #pin 9 Arduino
# servo_pinY = board.get_pin('d:6:s') #pin 10 Arduino
# servoPos = [90, 90] # initial servo position

def stackImages(scale,imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver

lowerKorban = (10,  100,  20)
upperKorban = (25, 255, 255)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    blurred = cv2.GaussianBlur(img, (11,11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lowerKorban, upperKorban)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None

    if len(contours) > 0:
        # area = cv2.contourArea(contours)
        c = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(c)
        ((x,y), (width, height), rotation) = rect
        x = f"x {np.round(x)}, y: {np.round(y)}, width: {np.round(width)}, height: {np.round(height)}, rotation: {np.round(rotation)}"
        
        box = cv2.boxPoints(rect)
        box = np.int64(box)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        jarak = 9000/height
        
        cv2.circle(img, center, 5, (255, 0, 255), -1)
        cv2.drawContours(img, [box], 0, (255, 0 , 0), 3)
        cv2.drawContours(img, contours, -1, (0, 255, 0), 3)
        cv2.putText(img, x, (25, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

        cvzone.putTextRect(img, "Kuning", (center[0]-10,center[1]-10), scale=2)
        # cvzone.putTextRect(img, f'{int(jarak)} cm', (center[0]-100,center[1]-100), scale=2)
        #get the coordinate
        # fx, fy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
        # pos = [fx, fy]
        # # convert coordinat to servo degree
        # servoX = np.interp(fx, [0, 1280], [0, 180])
        # servoY = np.interp(fy, [0, 720], [0, 180])

        # if servoX < 0:
        #     servoX = 0
        # elif servoX > 180:
        #     servoX = 18086686
        # if servoY < 0:
        #     servoY = 0
        # elif servoY > 180:
        #     servoY = 180

    # servoPos[0] = servoX
    # servoPos[1] = servoY
    # servo_pinX.write(servoPos[0])
    # servo_pinY.write(servoPos[1])
        # board.digital[pin_L].write(L)


    imgStack = stackImages(0.8,([img,blurred],[hsv,mask]))
    cv2.imshow("tess", img)
    if cv2.waitKey(1) & 0xFF == 27:
       break
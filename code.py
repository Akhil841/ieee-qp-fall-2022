from time import sleep
from machine import pin
from machine import PWM
# from gpiozero import Robot
import cv2
import numpy as np
import math
import os

class cvpwm:
    a = 1
    b = 0.9
    c = 0.8
    d = 0.7
    e = 0.6
    f = 0.5
    g = 0.4

    # left servo
    pwm = PWM(Pin(0))

    # right servo
    pwm2 = PWM(Pin(5))

    pwm.freq(50)
    pwm2.freq(50)


    def forward():
        for pos in range(1000, 5000, 50):
            pwm.duty_u16(pos)
            pwm2.duty_u16(5000 - pos)
            sleep(0.01)
    
    def backward():
        for pos in range(5000, 1000, 50):
            pwm.duty_u16(pos)
            pwm2.duty_u16(5000 - pos)
            sleep(0.01)
    
    def leftu():
        for pos in range(1000, 10000, 50):
            pwm.duty_u16(pos)
            pwm2.duty_u16(pos)
            sleep(0.01)
    
    def rightu():
        for pos in range(1000, 10000, 50):
            pwm.duty_u16(10000 - pos)
            pwm2.duty_u16(10000 - pos)
            sleep(0.01)

    def stop():
        pwm.duty_u16(0)
        pwm2.duty_u16(0)



    testmode = 1  # to enable added features such as view and save on file


    # distance betweem two points
    def calc_dist(p1,p2):

        x1 = p1[0]

        y1 = p1[1]

        x2 = p2[0]

        y2 = p2[1]
        
        dist = np.sqrt((x2-x1)**2 + (y2-y1)**2)

        return dist

    # Yield successive n-sized chunks from l.
    def getChunks(l, n):
        a = []

        for i in range(0, len(l), n):   

            a.append(l[i:i + n])

        return a


    # Main method for continous running.
    # Assumes object is placed on right corner of table.
    def main():
        cap = cv2.VideoCapture(1)

        try:
            if not os.path.exists('data'):
                os.makedirs('data')

        except OSError:
            print('Error: Creating directory of data')

        StepSize = 5
        currentFrame = 0

        while True:

            _, frame = cap.read()

            # if testmode == 1:
            name = './data/frame' + str(currentFrame) + '.jpg'
            print ('Creating...' + name)
            
            img = frame.copy()

            blur = cv2.bilateralFilter(img, 9, 40, 40)

            edges = cv2.Canny(blur, 50, 100)

            img_h = img.shape[0] - 1

            img_w = img.shape[1] - 1

            EdgeArray = []

            for j in range(0, img_w, StepSize):

                pixel = (j,0)

                for i in range(img_h-5,0,-1):

                    if edges.item(i,j) == 255:

                        pixel = (j,i)

                        break

                EdgeArray.append(pixel)

            for x in range(len(EdgeArray)-1):

                cv2.line(img, EdgeArray[x], EdgeArray[x+1], (0, 255, 0), 1)

            for x in range(len(EdgeArray)):

                cv2.line(img, (x*StepSize, img_h), EdgeArray[x], (0, 255, 0), 1)

            chunks = getChunks(EdgeArray, int(len(EdgeArray)/3))  # 5

            max_dist = 0

            c = []

            for i in range(len(chunks)-1):        

                x_vals = []

                y_vals = []

                for (x,y) in chunks[i]:

                    x_vals.append(x)

                    y_vals.append(y)

                avg_x = int(np.average(x_vals))
                avg_y = int(np.average(y_vals))

                c.append([avg_y, avg_x])

                cv2.line(frame, (320, 480), (avg_x, avg_y), (255, 0, 0), 2)

            print(c)

            forwardEdge = c[1]
            print(forwardEdge)

            cv2.line(frame,(320,480),(forwardEdge[1],forwardEdge[0]),(0,255,0),3)   
            cv2.imwrite(name, frame)
            
            y = (min(c))
            print(y)
            
            # if we have taken a left turn
            lt = False
            if forwardEdge[0] > 250: #200 # >230 works better

                # take a left u-turn if have not already, otherwise take a right u-turn
                if y[1] < 310 and not lt:
                    leftu()
                    lt = True
                    direction = "left"
                    print(direction)

                else:
                    rightu()
                    lt = False
                    direction = "right "
                    print(direction)

            else:
                forward()
                direction = "forward "
                print(direction)
            
            if testmode == 1:
                F = open("./data/imagedetails.txt", 'a')
                F.write("\n\nNew Test \n")
                F.write ("frame"+str(currentFrame)+".jpg" +" | " + str(c[0]) + " | " + str(c[1]) + " | " +str(c[2])  + " | " + direction + "\n")
                currentFrame +=1

                cv2.imshow("frame", frame)

                cv2.imshow("Canny", edges)

                cv2.imshow("result", img)

            if testmode == 2:

                cv2.imshow("frame",frame)

                cv2.imshow("Canny",edges)

                cv2.imshow("result",img)
        
        cap.release()
        cv2.destroyAllWindows()
         

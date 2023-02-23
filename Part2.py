import cv2, time
import numpy as np

def draw_direction(img, lx, ly, nx, ny):
    # Calculate the direction of movement based on the previous position and the current position and draw an arrow

    dx = nx - lx
    dy = ny - ly
    if abs(dx) < 4 and abs(dy) < 4:
        dx = 0
        dy = 0
    else:
        r = (dx**2 + dy**2)**0.5
        dx = int(dx/r*40)
        dy = int(dy/r*40)
        # print(dx, dy)
    cv2.arrowedLine(img, (60, 100), (60+dx, 100+dy), (0, 255, 0), 2)
    
    



frameWidth = 640
frameHeight = 480
cap = cv2.VideoCapture(0) #0 corresponds to the notebook with its own camera
cap.set(3, frameWidth)  # In the set, the 3 here, the 4 and 10 below are things similar to the function number, and the value of the number has no practical meaning
cap.set(4, frameHeight)
cap.set(10, 5)        # set brightness
pulse_ms = 30

#lower = np.array([4, 180, 156])     # 4<=h<=32, suitable for orange ping pong balls
#upper = np.array([32, 255, 255])
# =============================================================================
lower = np.array([0, 150, 130])     # 4<=h<=32, suitable for orange ping pong balls
upper = np.array([40, 255, 255])
# 
# =============================================================================
srt = time.time()
rec = [[0]*3, [0]*3, [0]*3]
num = 0
state = 0

dictionary = {0:"Not detect", 1: "Late", 2: "Early", 3: "Perfect"}
timing_score = []
while True:
    _, img = cap.read()

    imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    imgMask = cv2.inRange(imgHsv, lower, upper)     # Get the image mask
    imgOutput = cv2.bitwise_and(img, img, mask=imgMask)
    contours, hierarchy = cv2.findContours(imgMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)   # 查找轮廓

    # CV_RETR_EXTERNAL, Only detect the outermost contour
    # CV_CHAIN_APPROX_NONE, Save all continuous contour points on the object boundary to the contours vector
    imgMask = cv2.cvtColor(imgMask, cv2.COLOR_GRAY2BGR)    
    # After the conversion, it can be spliced ​​with the original picture in the later stage, otherwise it will have different dimensions from the original picture

    # The following code finds the bounding box, and draws
    x, y, w, h = 0, 0, 0, 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # print(area)vg
        if area > 30:
         
            x, y, w, h = cv2.boundingRect(cnt)            
            rec[0] = rec[0][1:3] + [int(x+w/2)]
            rec[1] = rec[1][1:3] + [int(y+h/2)]
            rec[2] = rec[2][1:3] + [round(time.time()-srt,2)]
            print('D'+str(num), "    ", str(int(x+w/2)), str(int(y+h/2)), str(rec))
            
            num += 1
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.circle(img, (int(x+w/2), int(y+h/2)), 2, (0, 255, 0), 4)
            
# =============================================================================
#             x, y, w, h = cv2.boundingRect(cnt)
#             lastPos_x = targetPos_x
#             lastPos_y = targetPos_y
#             targetPos_x = int(x+w/2)
#             targetPos_y = int(y+h/2)
#             cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
#             cv2.circle(img, (targetPos_x, targetPos_y), 2, (0, 255, 0), 4)
# =============================================================================

            if rec[0][0]+3 < rec[0][1] and rec[0][1] > rec[0][2]+3 and rec[2][2] - rec[2][1] < 0.8:
                dx = float(rec[0][1] - rec[0][0])
                dy = -float(rec[1][1] - rec[1][0])
                #if dy*1.732 > dx:#(30, 90]
# =============================================================================
#                 if  0.414 < dy / dx < 1:
#                     state = 4
#                     print(4)
# =============================================================================
                #elif 0 < dy*1.732 <= dx:
                if -0.57 <= dy/dx <= 0.57:#
                    state = 3
                    print(dictionary[state])
                #elif -dy*1.732 <= dx: #[-30,0)
                elif  0.57 < dy / dx: 
                    state = 2
                    print(dictionary[state])
                #elif dx < -dy*1.732 and dx > -dy/1.732 :#(-60, -30)
                elif dy / dx < -0.57:
                    state = 1
                    print(dictionary[state])

    timing_score.append(state)        
    cv2.putText(img, dictionary[state], (250, 30),
                cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)
            
    cv2.putText(img, "({:0<2d}, {:0<2d})".format(rec[0][2], rec[1][2]), (20, 30),
                cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)
    
    draw_direction(img, rec[0][1], rec[1][1], rec[0][2], rec[1][2])
    

    cv2.imshow('Horizontal Stacking', img)     # Output images
    if cv2.waitKey(pulse_ms) & 0xFF == ord('q'):          # 'q' to quit
        print("Quit\n")
        break

cap.release()
cv2.destroyAllWindows()
print("Average Timing Score:", np.mean(timing_score))#print average timing scores
import requests, json
#requests.put('http://129.236.150.42:5001/update_t',headers={'content-type':'application/json'},data=json.dumps({'timing':np.mean(timing_score)}))
requests.put('http://129.236.150.159:5002/update_t',headers={'content-type':'application/json'},data=json.dumps({'timing':np.mean(timing_score)}))
#output average timing scores


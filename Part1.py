import time,os,requests,cv2
import mediapipe as mp
import numpy as np
import matplotlib.pyplot as plt



import pandas as pd 
def data_read(filename):
    CSV = pd.read_csv(filename, header=None)
    Array = CSV.values
    Angle = Array[:,1]
    return Angle



mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
cap = cv2.VideoCapture(0)
F_mode = "Shakehand_forehand"# default mode: Shakehand forehand

def extract_stat(Shoulder_test, Elbow):
    Shoulder, Elbow = np.array(Shoulder_test), np.array(Elbow)
    max_S, min_S = np.max(Shoulder), np.min(Shoulder) # Extract maximum and minimum of shoulder angles
    median_S, mean_S, std_S = np.median(Shoulder), np.mean(Shoulder), np.std(Shoulder) # Extract median, mean, and standard deviation of shoulder angles
    max_E, min_E = np.max(Elbow), np.min(Elbow) # Extract maximum and minimu of Elbow angles
    median_E, mean_E, std_E = np.median(Elbow), np.mean(Elbow), np.std(Elbow) # Extract median, mean, and standard deviation of elbow angles
    return max_S, min_S, median_S, mean_S, std_S, max_E, min_E, mean_E, median_E, std_E

def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)#measure the angle based on np.arctan2()
    
    if angle >180.0:
        angle = 360-angle
        
    return angle 

    
def analyze_consistency(max_S, min_S, max_E, min_E):
    COMP_S = np.abs(K_F_max_S - max_S) / K_F_max_S  # Compare the shoulder angle with Kun Wang's data
    COMP_E = np.abs(K_F_max_E - max_E) / K_F_max_E  # Compare the Elbow angle with Kun Wang's data
    state_S_max = "Normal Shoulder Angle"
    state_S_min = "Normal Shoulder Angle"
    state_E_max = "Normal Elbow Angle"
    state_E_min = "Normal Elbow Angle"
    
    if max_S > 1.3*K_F_max_S:
        state_S_max = "Largest Shoulder angle is too large"
    elif max_S < 0.7*K_F_max_S:#analyze consistency based on Kun Wang's data
        state_S_max = "Largest Shoulder angle is too small" 
    else:
         state_S_max = "Normal Shoulder Angle"
        


    if max_E > 1.3*K_F_max_E:#analyze consistency based on Kun Wang's data
        state_E_max = "Largest Elbow angle is too large"
    elif max_E < 0.7*K_F_max_E:
        state_E_max = "Largest Elbow angle is too small" 
    else:
         state_E_max = "Normal Elbow Angle"

    if COMP_S + COMP_E < 0.5:
         consistency = {'state':'Perfect', 'value': 3}
    elif 0.5 < COMP_S + COMP_E < 1:
        consistency = {'state':'Good', 'value': 2}
    else:
        consistency = {'state':'Need to Improve', 'value': 1}
        
    
    return COMP_S, COMP_E, consistency, state_S_max, state_S_min, state_E_max, state_E_min
    
def analyze_framework(mean_S, mean_E):
    COMP_S = np.abs(K_F_mean_S - mean_S) / K_F_mean_S 
    COMP_E = np.abs(K_F_mean_E - mean_E) / K_F_mean_E 
    state_S = "Normal Shoulder Angle"
    state_E = "Normal Elbow Angle"
    if mean_S > K_F_mean_S*1.3:#analyze framework based on Kun Wang's data
        state_S = "Average Shoulder angle is too large"
    elif mean_S < K_F_mean_S*0.7:
        state_S = "Average Shoulder angle is too small"
    else:
        state_S = "Normal Shoulder Angle"
    if mean_E > K_F_mean_E*1.3:#analyze framework based on Kun Wang's data
        state_E = "Average Elbow angle is too large"
    elif mean_E < K_F_mean_E*0.7:
        state_E = "Average Elbow angle is too small"
    else:
        state_E = "Normal Elbow Angle"
        
    if COMP_S + COMP_E < 0.5:#analyze framework based on Kun Wang's data
         framework = {'state':'Perfect', 'value': 3}
    elif 0.5 < COMP_S + COMP_E < 1:
        framework = {'state':'Good', 'value': 2}
    else:
        framework = {'state':'Need to Improve', 'value': 1}
        
    
    return COMP_S, COMP_E, framework, state_S, state_E



Shoulder = []
Elbow = []
con_score, frame_score = [], []        
## Setup mediapipe instance
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Ignoring empty camera frame.")
            continue
        else:
            image = cv2.resize(frame, (640,480))        
        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #pdb.set_trace()
        image.flags.writeable = False
      
        # Make detection
        results = pose.process(image)
        
         # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        #Coordinates for detection
        
        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark
    
        
            R_X_S, R_Y_S,  R_Z_S = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z
            R_X_E, R_Y_E, R_Z_E = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].z 
            R_X_W, R_Y_W, R_Z_W = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].z
            R_X_H, R_Y_H, R_Z_H = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].z
            
            
            R_shoulder = [R_X_S, R_Y_S, R_Z_S]
            R_elbow = [R_X_E, R_Y_E, R_Z_E]
            R_wrist = [R_X_W, R_Y_W, R_Z_W]
            R_hip = [R_X_H, R_Y_H, R_Z_H]
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].z]
            # Calculate angle
            R_angle = calculate_angle([R_shoulder[0],R_shoulder[1], R_shoulder[2]], [R_elbow[0], R_elbow[1], R_elbow[2]], [R_wrist[0], R_wrist[1], R_wrist[2]])
            R_angle2 = calculate_angle([R_hip[0], R_hip[1], R_hip[2]], [R_shoulder[0], R_shoulder[1], R_shoulder[2]], [R_elbow[0], R_elbow[1], R_elbow[2]])
            
            if len(Shoulder) == 25:
                Shoulder = Shoulder[1:24] + [R_angle2]
            else:
                Shoulder.append(R_angle2)
            
            if len(Elbow) == 25:
                Elbow = Elbow[1:24] + [R_angle]
            else:
                Elbow.append(R_angle)
            
            
    

                       
        except:
            cv2.putText(image, 'Please Show Your Body!', (320,240), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            pass




        # Render detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                 )               
        #cv2.putText(image, str(F_mode), (20, 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2) 
        con_info = "Ready for testing consistency"
        frame_info = "Ready for testing framework "
        cv2.putText(image, F_mode, (20, 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
        #cv2.putText(image, con_info, (20, 130), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)
        #cv2.putText(image, frame_info, (20, 230), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)
        cv2.putText(image, 'Elbow:'+str(int(R_angle)), 
                           tuple(np.multiply([R_elbow[0],R_elbow[1]], [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA
                                )
        cv2.putText(image, 'Shoulder:'+str(int(R_angle2)), 
                           tuple(np.multiply([R_shoulder[0],R_shoulder[1]], [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA
                                )
        cv2.imshow('Mediapipe Feed', image)
        
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):
            break#返回最终consistency和framework结果 np.mean(consistency), np.median(consistency), np.mean(framework), np.median(framework)
        elif key == ord('f'):
            F_mode = "Shakehand_forehand"
        elif key == ord('g'):
            F_mode = "Penhold_forehand"
        elif key == ord('b'):
            F_mode = "Shakehand_backhand"
        elif key == ord('n'):
            F_mode = "Penhold_backhand"#change modes
    
        time.sleep(0.2)
        if len(Shoulder) == 25 and len(Elbow) == 25:
            #import pdb;pdb.set_trace()
            if F_mode == "Shakehand_forehand":
            
   
                K_F_max_S, K_F_max_E, K_F_mean_S, K_F_mean_E = 33, 164, 28, 84
            elif F_mode == "Shakehand_backhand":
                K_F_max_S, K_F_max_E, K_F_mean_S, K_F_mean_E = 37, 158, 30, 86
            elif F_mode == "Penhold_forehand":
                #K_F_max_S, K_F_max_E, K_F_mean_S, K_F_mean_E = 32, 174, 22, 106
                K_F_max_S, K_F_max_E, K_F_mean_S, K_F_mean_E = 39, 174, 29, 106
            elif F_mode == "Penhold_backhand":
                #K_F_max_S, K_F_max_E, K_F_mean_S, K_F_mean_E = 32, 163, 22, 95
                K_F_max_S, K_F_max_E, K_F_mean_S, K_F_mean_E = 39, 163, 29, 95
                
            
            Y_F_max_S, Y_F_min_S, Y_F_median_S, Y_F_mean_S, Y_F_std_S, Y_F_max_E, Y_F_min_E, Y_F_mean_E, Y_F_median_E, Y_F_std_E = extract_stat(Shoulder, Elbow)
            
            #COMP_S_CON, COMP_E_CONS, consistency, state_S_con, state_E_con = analyze_consistency(Y_F_max_S, Y_F_min_S, Y_F_max_E, Y_F_min_E)
            COMP_S_CON, COMP_E_CON, consistency, state_S_max, state_S_min, state_E_max, state_E_min = analyze_consistency(Y_F_max_S, Y_F_min_S, Y_F_max_E, Y_F_min_E)
            #print("Shoulder Difference:", COMP_S_CON*100, "%"," ,", "Elbow Difference:", COMP_E_CON*100, "%",",", "Consistency is:", consistency)
            con_info = "Consistency:"+consistency['state']+","+state_S_max+","+state_E_max
            print(con_info)

            con_score.append(consistency['value'])# append scores to calculate the average
            #COMP_S_framework, COMP_E_framework, framework, state_S_frame, state_E_frame = analyze_framework(Y_F_median_S, Y_F_mean_S, Y_F_std_S, Y_F_median_E, Y_F_mean_E, Y_F_std_E)
            COMP_S_framework, COMP_E_framework, framework, state_S, state_E = analyze_framework(Y_F_mean_S, Y_F_mean_E)
            frame_info = "Framework:"+framework['state']+","+state_S+","+state_E 
            print(frame_info)# append scores to calculate the average
            frame_score.append(framework['value'])
    
    cap.release()
    cv2.destroyAllWindows()


print("Average Consistency:", np.mean(con_score),"Average Framework:", np.mean(frame_score))# Output average scores of consistency and framework
import requests, json
requests.put('http://129.236.150.159:5002/update_cf',headers={'content-type':'application/json'},data=json.dumps({'consistency':np.mean(con_score),'framework':np.mean(frame_score)}))
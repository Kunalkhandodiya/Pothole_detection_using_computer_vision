#importing necessary libraries
# import ComputerVision -Opencv
# import python timing  -time
# import Navigation     -Geocoder
# import python to user interact -OS
import cv2 as cv
import time
import geocoder
import os

#reading label name from obj.names file
'''class_name = []
with open(os.path.join("project_files",'obj.names'), 'r') as f:
    class_name = [cname.strip() for cname in f.readlines()]'''

#importing model weights and config file
#defining the model parameters

net1 = cv.dnn.readNet('yolov4_tiny.weights', 'yolov4_tiny.cfg')
net1.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
net1.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA_FP16)
model1 = cv.dnn_DetectionModel(net1)
model1.setInputParams(size=(640, 480), scale=1/255, swapRB=True)

#defining the video source (0 for camera or file name for video)
cap = cv.VideoCapture("test.mp4") 
width  = cap.get(3)
height = cap.get(4)
result = cv.VideoWriter('result.avi', 
                         cv.VideoWriter_fourcc(*'MJPG'),
                         10,(int(width),int(height)))

#defining parameters for result saving and get coordinates
#defining initial values for some parameters in the script
g = geocoder.ip('me')
result_path = "pothole_coordinates"
starting_time = time.time()
Conf_threshold = 0.5
NMS_threshold = 0.4
frame_counter = 0
i = 0
b = 0

#detection loop
while True:
    ret, frame = cap.read()
    frame_counter += 1
    if ret == False:
        break
#analysis the stream with detection model
    classes, scores, boxes = model1.detect(frame, Conf_threshold, NMS_threshold)
    for (classid, score, box) in zip(classes, scores, boxes):
        label = "pothole"
        x, y, w, h = box
        recarea = w*h
        area = width*height
#drawing detection boxes on frame for detected potholes and saving coordinates txt and photo
        if(len(scores)!=0 and scores[0]>=0.7):
            if((recarea/area)<=0.1 and box[1]<600):
#Detection Frame Size and Color
                cv.rectangle(frame, (x, y), (x + w, y + h), (10,255,255), 3)
# Detection Size Writing Text
                cv.putText(frame, "%" + str(round(scores[0]*100,2)) + " " + label, (box[0], box[1]-10),cv.FONT_HERSHEY_COMPLEX, 0.9, (255,0,0), 1)
                if(i==0):
                    cv.imwrite(os.path.join(result_path,'pothole'+str(i)+'.jpg'), frame)
                    with open(os.path.join(result_path,'pothole'+str(i)+'.txt'), 'w') as f:
                        f.write(str(g.latlng))
                        i=i+1
                if(i!=0):
                    if((time.time()-b)>=2):
                        cv.imwrite(os.path.join(result_path,'pothole'+str(i)+'.jpg'), frame)
                        with open(os.path.join(result_path,'pothole'+str(i)+'.txt'), 'w') as f:
                            f.write(str(g.latlng))
                            b = time.time()
                            i = i+1
#writing fps on frame
# fps is frame per Second
    endingTime = time.time() - starting_time
    fps = frame_counter/endingTime
    cv.putText(frame, f'FPS: {fps}', (20, 50),
# change Font Color and Size & Field
               cv.FONT_HERSHEY_COMPLEX, 0.7, (500, 255, 0), 2)

    #showing and saving result
    cv.imshow('Pothole Detection Version 1.1 by Kunal khandodiya ', frame)
    result.write(frame)
    key = cv.waitKey(1)
    if key == ord('q'):
        break
    
#end
cap.release()
result.release()
cv.destroyAllWindows()

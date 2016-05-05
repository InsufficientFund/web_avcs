import cv2
import numpy as np
from copy import deepcopy
import math
import os
from lbp_feature import lbp_feature
from neural_net import neural_net
from lda import LDA
from save_db import save_type, update_progress
from django.conf import settings
import threading

class AVCS:
    """docstring for ClassName"""
    def __init__(self):
        self.video = None
        self.fgMask = None
        self.sampleFrame = None
        #self.subtractor = cv2.BackgroundSubtractorMOG(history=150, nmixtures=20, backgroundRatio=0.7, noiseSigma=25)
        self.subtractor = cv2.BackgroundSubtractorMOG2(150, 200, False)
        self.lanes = []
        self.lanesImage = []
        self.laneContours = []
        self.lanePoints = []
        self.typeCar = {"small": 0, "medium": 0, "large": 0}
        self.totalLane = 0
        self.video_name = ''
        self.num_frame = 0
        self.timer = None
        self.total_frame = 0

    def __del__(self):
        pass

    def readVideo(self, path_name, file_name):
        self.video = cv2.VideoCapture(path_name)
        self.video_name = file_name
        self.total_frame = int(self.video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

    def addLane(self, upLeft, upRight, lowLeft, lowRight):
        self.lanes.append({"upLeft": upLeft, "upRight": upRight,
                           "lowLeft": lowLeft, "lowRight": lowRight,
                           "is_empty": True, "pts": []})
        point = np.array([[upLeft],
                          [upRight],
                          [lowRight],
                          [lowLeft]], np.int32)
        self.lanePoints.append(point)
        laneImage = np.zeros((480, 640), np.uint8)
        cv2.fillPoly(laneImage, [point], 255)
        self.lanesImage.append(laneImage)
        contour, hrc = cv2.findContours(laneImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.laneContours.append(contour)
        self.totalLane += 1

    def showPoint(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            print x, y

    def sampleImage(self):
        if self.video.isOpened():
            self.video.set(cv2.cv.CV_CAP_PROP_POS_MSEC, 0)
            ret, self.sampleFrame = self.video.read()
            if ret:
                return self.sampleFrame

    def writeClusters(self, data, members):
        dataF = open('data.csv', 'a')
        for cluster in range(3):
            for atr1, atr2 in data[members[cluster]]:
                dataF.write(str(atr1) + ", " + str(atr2) + ", " + str(cluster) + "\n")
        dataF.close()

    def getBackground(self, data, avg):
        cv2.accumulateWeighted(data, avg, 0.01)
        res = cv2.convertScaleAbs(avg)
        return res

    def get_num_frame(self):
        return self.total_frame

    def progress(self):
        self.timer = threading.Timer(5.0, self.progress)
        self.timer.start()
        #print 'frame' + str(self.num_frame)
        update_progress(self.video_name, self.num_frame, self.total_frame)

    def run(self, mode,  cntStatus = True, saveVid = False, showVid = True ):
        lbp = lbp_feature()
        # neural_network = neural_net(75, 3)
        # neural_network.create_struct(150)
        # neural_network.load_model(settings.STATICFILES_DIRS[0])
        lda = LDA(75, 3)
        #lda.create_struct(150)
        if mode == 'predict':
            lda.load_model(settings.STATICFILES_DIRS[0])
        self.video.set(cv2.cv.CV_CAP_PROP_POS_MSEC, 0)
        kernel = np.ones((10, 10), np.uint8)
        lanes = [[] for x in range(self.totalLane)]
        totalCars = [0] * self.totalLane
        num_car_detect = 0
        self.timer = threading.Timer(5.0, self.progress)
        self.timer.start()
        while self.video.isOpened():
            ret, frame = self.video.read()
            if not ret:
                break
            frameOrigin = deepcopy(frame)
            res = frame
            self.num_frame +=1
            for point in self.lanePoints:
                cv2.polylines(frame, [point], True, (0, 255, 0), 3)

            filteredFrame = cv2.GaussianBlur(frame, (5, 5), 0)
            if self.fgMask is None:
                self.fgMask = self.subtractor.apply(filteredFrame, -1)
                test = deepcopy(self.fgMask)
            self.fgMask = self.subtractor.apply(filteredFrame, self.fgMask, -1)
            self.fgMask = cv2.dilate(self.fgMask, kernel, iterations=1)
            self.fgMask = cv2.erode(self.fgMask, kernel, iterations=1)

            self.fgMask = cv2.morphologyEx(self.fgMask, cv2.MORPH_CLOSE, np.ones((30, 30), np.uint8))
            self.fgMask = cv2.morphologyEx(self.fgMask, cv2.MORPH_CLOSE, np.ones((30, 30), np.uint8))
            self.fgMask = cv2.morphologyEx(self.fgMask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
            tempMask = deepcopy(self.fgMask)
            carImg = cv2.bitwise_and(frameOrigin, frameOrigin, mask=self.fgMask)
# Section tracking and Detection
            contours, hrc = cv2.findContours(tempMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
            isIn = [False] * self.totalLane
            laneObj = [[] for x in range(self.totalLane)]

            outLane = [[] for x in range(self.totalLane)]
            for obj in contours:
                moment = cv2.moments(obj)
                if moment['m00'] == 0:
                    continue
                cx = int(moment['m10']/moment['m00'])
                cy = int(moment['m01']/moment['m00'])
                pX, pY, w, h = cv2.boundingRect(obj)

                isNotLane = True
                for numLane in range(len(self.laneContours)):
                    if cv2.pointPolygonTest(self.laneContours[numLane][0], (cx, cy), False) == 1:
                        car_object = {"centroid": (cx, cy+h/2), "origin": (pX, pY), "height": h, "width": w}
                        laneObj[numLane].append(car_object)
                        isNotLane = False
                        break
                if isNotLane:
                    for numLane in range(len(self.laneContours)):
                        lanePoint =  self.lanePoints[numLane]

                        if cx >= lanePoint[3][0][0] and cx <= lanePoint[2][0][0]\
                                and cy >= lanePoint[3][0][1]  and cy <= lanePoint[3][0][1]+50:
                            car_object = {"centroid": (cx, cy+h/2), "origin": (pX, pY), "height": h, "width": w}
                            outLane[numLane].append(car_object)

            for numLane in range(len(self.laneContours)):
                for i in outLane[numLane]:
                    diffRange = 50
                    foundedObj = None
                    for j in lanes[numLane]:
                        diff = math.fabs(j["point"][0][0] - i["centroid"][0]) + math.fabs(j["point"][0][1] - i["centroid"][1])
                        if diff < diffRange:
                            diffRange = diff
                            foundedObj = j
                    if foundedObj is not None:
                        totalCars[numLane] += 1
                        originX = i["origin"][0]
                        originY = i["origin"][1]
                        crop_img = frameOrigin[originY:originY + i["height"], originX:originX+i["width"]]
                        normal_image = cv2.resize(crop_img, (64, 64))
                        num_car_detect += 1
                        if mode == 'train':
                            directory = settings.STATICFILES_DIRS[0]+'main_app/media/train_image/'
                            if not os.path.exists(directory):
                                os.makedirs(directory)
                            cv2.imwrite(directory + 'car'+str(num_car_detect)+'.png', crop_img)
                        if mode == 'predict':
                            height, width, channels = crop_img.shape
                            size_data = [height/100.0, width/100.0, height * width/10000.0]
                            lbp.read_image(normal_image)
                            feature = lbp.extract_feature(size_data[0], size_data[1], size_data[2])
                            #answer = neural_network.predict(feature)
                            answer = int(lda.predict(feature))
                            save_type(self.video_name, answer, self.num_frame)
                            if answer == 2:
                                self.typeCar["small"] += 1
                            elif answer == 1:
                                self.typeCar["medium"] += 1
                            else:
                                self.typeCar["large"] += 1
                            print answer
                            file_name = self.video_name[:self.video_name.find('.avi')] + '.png'
                            path = settings.STATICFILES_DIRS[0]+'main_app/media/result_image/'+str(num_car_detect)+'-'+str(answer)+'-'+file_name
                            cv2.imwrite(path, crop_img)
                        lanes[numLane].remove(foundedObj)

                for i in lanes[numLane]:
                    i["stat"] = False
                for i in laneObj[numLane]:
                    diffRange = 50
                    foundedObj = None
                    for j in lanes[numLane]:
                        diff = math.fabs(j["point"][0][0] - i["centroid"][0]) + math.fabs(j["point"][0][1] - i["centroid"][1])

                        if diff < diffRange:
                            diffRange = diff
                            foundedObj = j
                    if foundedObj is not None:
                        foundedObj["point"].insert(0, i["centroid"])
                        foundedObj["stat"] = True
                    else:
                        lanes[numLane].append({ "point": [i["centroid"]], "stat": True })
                tempLane = []
                for i in lanes[numLane]:
                    if i["stat"]:
                        tempLane.append(i)
                        cv2.polylines(res, np.int32([i["point"]]), False, (0, 255, 255), 3)
                lanes[numLane] = tempLane

# Section Draw TrackLine
            for obj in contours:
                moment = cv2.moments(obj)
                if moment['m00'] == 0:
                    continue
                pX, pY, w, h = cv2.boundingRect(obj)
                cx = int(moment['m10']/moment['m00'])
                cy = int(moment['m01']/moment['m00'])+h/2
                cv2.circle(res, (cx, cy), 3, (0, 0, 255), 4)
                distance = []
                for numLane in range(len(self.laneContours)):
                    distance.append(cv2.pointPolygonTest(self.laneContours[numLane][0], (cx, cy), False))
                for numLane in range(len(self.laneContours)):
                    if distance[numLane] == 1:
                        isIn[numLane] = True
                        cv2.rectangle(res, (pX, pY), (pX+w, pY+h), (0, 255, 255), 2)
                        if self.lanes[numLane]["is_empty"]:
                            self.lanes[numLane]["is_empty"] = False
                            self.lanes[numLane]["pts"].append((cx, cy))
                        else:
                            self.lanes[numLane]["pts"].insert(0, (cx, cy))
                        break
                    else:
                        cv2.rectangle(res, (pX, pY), (pX+w, pY+h), (255, 255, 0), 2)
            for i in range(0, self.totalLane):
                if isIn[i]:
                    if showVid:
                        pass
                else:
                    self.lanes[numLane]["is_empty"] = True
                    self.lanes[numLane]["pts"] = []
            if cntStatus:
                cv2.putText(res, 'lane1: '+str(totalCars[0]), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(res, 'lane2: '+str(totalCars[1]), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (125, 0, 255), 2)
                cv2.putText(res, 'truck/bus: '+str(self.typeCar["large"]), (400, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(res, 'small car: '+str(self.typeCar["medium"]), (400, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(res, 'motorcycle: '+str(self.typeCar["small"]), (400, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            if showVid:
                resMask = cv2.bitwise_and(frame, frame, mask=~self.fgMask)
                cv2.imshow('frame', res)
                if cv2.waitKey(5) & 0xFF == ord('q'):
                    cv2.imwrite('tesf.png', frameOrigin)
                    cv2.imwrite('tesM.png', self.fgMask)
                    break
        self.timer.cancel()
        update_progress(self.video_name, self.num_frame, self.total_frame)
        print totalCars
        self.video.release()
        cv2.destroyAllWindows()
        print self.typeCar

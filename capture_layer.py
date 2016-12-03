import cv2
import numpy as np

from multiprocessing import Process, Value, Array

class CaptureLayer:
    def __init__(self):
        self.marker_shape = Array('d', [-1,-1,-1,-1])

    def run_capture(self):
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        cap = cv2.VideoCapture(0)

        while True:
            ret, img = cap.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape

            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            biggest_face = 0
            b_face = [0,0]

            for (x,y,w,h) in faces:
                #cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
                if w*h > biggest_face:
                    biggest_face = w*h
                    b_face = [float(x)/width, float(y)/height, float(w)/width, float(h)/height]
                    #b_face = [x,y,w,h]

            if biggest_face != 0:
                #cv2.rectangle(img, (b_face[0],b_face[1]), (b_face[0]+b_face[2],b_face[1]+b_face[3]), (0,255,0), 2)
                for i in xrange(len(self.marker_shape)):
                    self.marker_shape[i] = b_face[i]
            else:
                for i in xrange(len(self.marker_shape)):
                    self.marker_shape[i] = -1

            #cv2.imshow('img', img)
            #k = cv2.waitKey(10) & 0xff
            #if k == 27 or k == 32:
            #    break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    run_capture()
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
# PROCESSED_FRAME_RESOLUTION = (640, 360)
PROCESSED_FRAME_RESOLUTION = (640, 360)


if __name__ == '__main__':
    print('object detection')

    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    cv2.startWindowThread()

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out_video = cv2.VideoWriter('person.avi', fourcc, 2.0, PROCESSED_FRAME_RESOLUTION)
    try:

        video = cv2.VideoCapture(r'D:\MyData\Files\MyProjects\scripts\13 авг.avi')
        # video = cv2.VideoCapture(r'T:\Record\cam vet 2\1\20220812120000.h264')
        try:
            eof = False
            error_count = 0
            key = -1
            while video.isOpened() and not eof and key != 27:
                is_ok, frame = video.read()
                if is_ok:
                    error_count = 0

                else:
                    error_count += 1
                    if error_count >= 150:
                        eof = True
                        print('is eof')

                if is_ok:
                    frame = cv2.resize(frame, PROCESSED_FRAME_RESOLUTION)
                    boxes, weights = hog.detectMultiScale(frame, 0, (8, 8))

                    if len(weights) > 0:
                        print(f'boxes: {boxes}')
                        print(f'weights: {weights}')
                        max_weight = max(weights)
                        if len(boxes) > 0 and max_weight > 0.2:
                            for box, weight in zip(boxes, weights):
                                x1, y1, w, h = box
                                x2 = x1 + w
                                y2 = y1 + h
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 3)
                                cv2.putText(frame, '{0:.4f}'.format(weight), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))
                        cv2.rectangle(frame, (0, 0), (64, 128), (170, 170, 170), 2)
                    cv2.imshow('detection', frame)
                    out_video.write(frame)
                    # for i in range(500):
                    #     video.grab()

                key = cv2.waitKey(10)

        finally:
            video.release()

    finally:
        out_video.release()
        cv2.destroyAllWindows()

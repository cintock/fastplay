#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2

from object_detector import ObjectDetector

if __name__ == '__main__':
    print('object detection')
    detector = ObjectDetector()
    detector.set_output_filename('person.mp4')
    detector.begin_detection(1920, 1080)
    try:
        video = cv2.VideoCapture(r'T:\CamRecordAnalysis\202208221417_cam3.mkv')
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
                    detector.process_frame(frame)

                key = cv2.waitKey(1)

        finally:
            video.release()

    finally:
        detector.end_detection()
        cv2.destroyAllWindows()

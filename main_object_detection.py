#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

import cv2

from object_detector import ObjectDetector

KEY_ESC = 27
EOF_BAD_FRAME_COUNT = 150

if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('input_video_file')
    argument_parser.add_argument('output_video_file')
    args = argument_parser.parse_args()
    input_video_file = args.input_video_file
    output_video_file = args.output_video_file
    print(f'input video file: {input_video_file}')
    print(f'output video file: {output_video_file}')
    detector = ObjectDetector()
    detector.set_output_filename(output_video_file)
    # todo: определять размер кадра
    detector.begin_detection(1920, 1080)
    try:
        video = cv2.VideoCapture(input_video_file)
        try:
            eof = False
            error_count = 0
            key = -1
            while video.isOpened() and not eof and key != KEY_ESC:
                is_ok, frame = video.read()
                if is_ok:
                    error_count = 0

                else:
                    error_count += 1
                    if error_count >= EOF_BAD_FRAME_COUNT:
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

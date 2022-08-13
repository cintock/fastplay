#!/usr/bin/env python
# -*- coding: utf-8 -*-
import typing

import cv2
# PROCESSED_FRAME_RESOLUTION = (640, 360)
import numpy

from objects_saver import ObjectSaver

VIDEO_FRAME_RESOLUTION = (1920, 1080)
PROCESSED_FRAME_RESOLUTION = (768, 432)


def draw_object_zone(
        frame: numpy.ndarray,
        weight: typing.Optional[float],
        resize_coef: float,
        x1: int, y1: int,
        w: int, h: int,
        color: tuple = (255, 255, 0),
        small_rectangle: bool = False
):
    assert isinstance(frame, numpy.ndarray)
    assert isinstance(weight, float) or weight is None
    assert isinstance(resize_coef, float)
    assert isinstance(x1, int)
    assert isinstance(y1, int)
    assert isinstance(w, int)
    assert isinstance(h, int)
    if small_rectangle:
        x1 += round(w * 0.1)
        y1 += round(h * 0.07)
        w = round(w * 0.8)
        h = round(h * 0.8)
    x2 = x1 + w
    y2 = y1 + h
    cv2.rectangle(
        frame,
        (int(x1 * resize_coef), int(y1 * resize_coef)),
        (int(x2 * resize_coef), int(y2 * resize_coef)),
        color,
        3
    )

    if weight is not None:
        cv2.putText(
            frame,
            '{0:.4f}'.format(weight),
            (int(x1 * resize_coef), int(y1 * resize_coef)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 0)
        )


if __name__ == '__main__':
    print('object detection')

    resize_coef = float(VIDEO_FRAME_RESOLUTION[0]) / PROCESSED_FRAME_RESOLUTION[0]

    hog = cv2.HOGDescriptor((64,128), (16,16), (8,8), (8,8), 9)
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    cv2.startWindowThread()

    object_saver = ObjectSaver()
    object_saver.resize_coef = resize_coef

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_video = cv2.VideoWriter('person.mp4', fourcc, 2.0, VIDEO_FRAME_RESOLUTION)
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
                    frame = cv2.resize(frame, VIDEO_FRAME_RESOLUTION)
                    processed_frame = cv2.resize(frame, PROCESSED_FRAME_RESOLUTION)
                    boxes, weights = hog.detectMultiScale(processed_frame, 0, (8, 8))

                    if len(weights) > 0:
                        print(f'boxes: {boxes}')
                        print(f'weights: {weights}')
                        max_weight = max(weights)
                        if len(boxes) > 0 and max_weight > 0.7:
                            for box, weight in zip(boxes, weights):
                                x1, y1, w, h = box
                                draw_object_zone(
                                    frame, float(weight), float(resize_coef),
                                    int(x1), int(y1), int(w), int(h),
                                    small_rectangle=False
                                )
                                object_saver.save_object(
                                    frame, int(x1), int(y1), int(w), int(h), weight=weight)

                    draw_object_zone(frame, None, resize_coef, 0, 0, 64, 128, color=(0, 0, 0))
                    cv2.imshow('detection', frame)
                    out_video.write(frame)
                    # for i in range(500):
                    #     video.grab()

                key = cv2.waitKey(1)

        finally:
            video.release()

    finally:
        out_video.release()
        cv2.destroyAllWindows()

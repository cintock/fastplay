#!/usr/bin/env python
# -*- coding: utf-8 -*-
import typing

import cv2
import numpy

from objects_saver import ObjectSaver

VIDEO_FRAME_RESOLUTION_WIDTH = 1920
VIDEO_FRAME_RESOLUTION_HEIGHT = 1080


class ObjectDetector:
    # разрешение кадра, на котором определяются объекты
    # (размер картинки должен соответствовать размерам поисковых шаблонов)
    _PROCESSED_FRAME_RESOLUTION_WIDTH = 768
    _PROCESSED_FRAME_RESOLUTION_HEIGHT = 432

    _NUMPY_ARR_WIDTH_INDEX = 1
    _NUMPY_ARR_HEIGHT_INDEX = 0

    # todo: привести этот класс в порядок
    def __init__(self):
        self._hog: typing.Optional[cv2.HOGDescriptor] = None
        self._output_filename: typing.Optional[str] = None
        self._out_video: typing.Optional[cv2.VideoWriter] = None
        self._object_saver: typing.Optional[ObjectSaver] = None
        self._resize_coef: typing.Optional[float] = None
        self._video_frame_width: typing.Optional[int] = None
        self._video_frame_height: typing.Optional[int] = None

    def set_output_filename(self, name: str):
        assert isinstance(name, str)
        self._output_filename = name

    def begin_detection(self, frame_width: int, frame_height: int):
        assert isinstance(frame_width, int)
        assert isinstance(frame_height, int)

        if self._output_filename is None:
            raise Exception('Output filename is not defined')

        self._video_frame_width = frame_width
        self._video_frame_height = frame_height
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        self._out_video = cv2.VideoWriter(
            self._output_filename, fourcc, 2.0, (self._video_frame_width, self._video_frame_height))

        self._resize_coef = float(self._video_frame_width) / float(self._PROCESSED_FRAME_RESOLUTION_WIDTH)

        # соотношение сторон должно соответствовать
        if round(float(self._video_frame_height) / float(self._PROCESSED_FRAME_RESOLUTION_HEIGHT), 4) != \
                round(self._resize_coef, 4):
            raise Exception('Соотношение сторон изображения должно соответствовать')

        self._hog = cv2.HOGDescriptor((64, 128), (16, 16), (8, 8), (8, 8), 9)
        self._hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        self._object_saver = ObjectSaver()
        self._object_saver.resize_coef = 1.0

    def process_frame(self, frame: numpy.ndarray):
        if (
            frame.shape[self._NUMPY_ARR_WIDTH_INDEX] != self._video_frame_width or
            frame.shape[self._NUMPY_ARR_HEIGHT_INDEX] != self._video_frame_height
        ):
            raise Exception('Размер обрабатываемого кадра не соответствует')

        processed_frame = cv2.resize(
            frame,
            (self._PROCESSED_FRAME_RESOLUTION_WIDTH, self._PROCESSED_FRAME_RESOLUTION_HEIGHT)
        )
        boxes, weights = self._hog.detectMultiScale(processed_frame, 0, (8, 8))

        if len(weights) > 0:
            for box, weight in zip(boxes, weights):
                if weight > 0.7:
                    x1, y1, w, h = self._resized_box_to_normal(box)

                    self._object_saver.save_object(
                        frame, int(x1), int(y1), int(w), int(h), weight=weight)

                    self._draw_object_zone(
                        frame, float(weight), float(1.0),
                        int(x1), int(y1), int(w), int(h),
                        small_rectangle=False
                    )

                    self._draw_object_zone(frame, None, self._resize_coef, 0, 0, 64, 128, color=(0, 0, 0))
                    cv2.imshow('detection', frame)
                    self._out_video.write(frame)

    def end_detection(self):
        self._out_video.release()

    def _resized_box_to_normal(self, box: typing.Iterable[typing.Union[int, float]]) -> numpy.ndarray:
        return numpy.array(box) * self._resize_coef

    def _draw_object_zone(
            self,
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

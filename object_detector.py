#!/usr/bin/env python
# -*- coding: utf-8 -*-
import typing

import cv2
import numpy

from objects_saver import ObjectSaver


class ObjectDetector:
    # разрешение кадра, на котором определяются объекты
    # (размер картинки должен соответствовать размерам поисковых шаблонов)
    _PROCESSED_FRAME_RESOLUTION_WIDTH = 768
    _PROCESSED_FRAME_RESOLUTION_HEIGHT = 432

    # какую часть выходного кадра будет занимать изображение
    _IMAGE_COEF_FULL_FRAME = 0.9

    _NUMPY_ARR_WIDTH_INDEX = 1
    _NUMPY_ARR_HEIGHT_INDEX = 0

    # todo: привести этот класс в порядок
    def __init__(self):
        self._left_shift_width: typing.Optional[int] = None
        self._top_panel_height: typing.Optional[int] = None
        self._hog: typing.Optional[cv2.HOGDescriptor] = None
        self._output_filename: typing.Optional[str] = None
        self._out_video: typing.Optional[cv2.VideoWriter] = None
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

        self._hog = cv2.HOGDescriptor()
        self._hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def process_frame(self, input_frame: numpy.ndarray):
        if (
            input_frame.shape[self._NUMPY_ARR_WIDTH_INDEX] != self._video_frame_width or
            input_frame.shape[self._NUMPY_ARR_HEIGHT_INDEX] != self._video_frame_height
        ):
            raise Exception('Размер обрабатываемого кадра не соответствует')

        processed_frame = cv2.resize(
            input_frame,
            (self._PROCESSED_FRAME_RESOLUTION_WIDTH, self._PROCESSED_FRAME_RESOLUTION_HEIGHT)
        )

        boxes, weights = self._hog.detectMultiScale(
            processed_frame,
            hitThreshold=0,
            winStride=(8, 8)
        )

        output_frame_image_height = round(self._video_frame_height * self._IMAGE_COEF_FULL_FRAME)
        output_frame_image_width = round(self._video_frame_width * self._IMAGE_COEF_FULL_FRAME)
        left_right_side_width = self._video_frame_width - output_frame_image_width

        self._top_panel_height: int = self._video_frame_height - output_frame_image_height
        self._left_shift_width: int = round(float(left_right_side_width) / 2.0)

        output_frame = numpy.zeros(shape=input_frame.shape, dtype=input_frame.dtype)
        output_frame_image = cv2.resize(
            input_frame,
            (output_frame_image_width, output_frame_image_height),
        )

        # поместим на результирующий кадр уменьшенное изображение
        output_frame[
            # верхняя панель занимает место сверху, поэтому отступаем от нее
            self._top_panel_height:self._video_frame_height,

            # левая область и правая область обрамляют изображение посередине
            self._left_shift_width:self._video_frame_width - self._left_shift_width
        ] = output_frame_image

        # если обнаружены объекты
        if len(boxes) > 0:
            for box, weight in zip(boxes, weights):
                if weight > 0.7:
                    x1_det = box[0]
                    y1_det = box[1]
                    width_det = box[2]
                    height_det = box[3]
                    x2_det = x1_det + width_det
                    y2_det = y1_det + height_det

                    x1, y1 = self._coord_processed_image_to_image(x1_det, y1_det)
                    x2, y2 = self._coord_processed_image_to_image(x2_det, y2_det)

                    x1, y1 = self._coord_image_to_full_frame(x1, y1)
                    x2, y2 = self._coord_image_to_full_frame(x2, y2)

                    self._draw_object_zone(
                        output_frame, float(weight),
                        x1, y1, x2, y2
                    )

            example_box_x2, example_box_y2 = self._coord_processed_image_to_image(self._hog.winSize[0], self._hog.winSize[1])
            example_box_x2, example_box_y2 = self._coord_image_to_full_frame(example_box_x2, example_box_y2)
            width, height = example_box_x2, example_box_y2
            self._draw_rectangle(output_frame, 0, 0, width, height, color=(0, 0, 0))
            cv2.imshow('detection', output_frame)
            self._out_video.write(output_frame)

    def end_detection(self):
        self._out_video.release()

    def _coord_processed_image_to_image(self, x: int, y: int) -> typing.Tuple[int, int]:
        """
        Переход от координат обрабатываемого изображения к координатам исходного изображения
        :param x: значение x
        :param y: значение y
        :return: (x, y)
        """
        x_image_frame = round(x * self._resize_coef)
        y_image_frame = round(y * self._resize_coef)
        return x_image_frame, y_image_frame

    def _coord_image_to_full_frame(self, x: int, y: int) -> typing.Tuple[int, int]:
        """
        Переход от координат исходного изображения к координатам выходного кадра
        :param x: значение x
        :param y: значение y
        :return: (x, y)
        """
        x_full = round((x * self._IMAGE_COEF_FULL_FRAME) + self._top_panel_height)
        y_full = round((y * self._IMAGE_COEF_FULL_FRAME) + self._left_shift_width)
        return x_full, y_full

    def _draw_rectangle(
        self,
        frame: numpy.ndarray,
        x1: int,
        y1: int,
        width: int,
        height: int,
        color: tuple = (255, 255, 0),
    ):
        assert isinstance(x1, int)
        assert isinstance(y1, int)
        assert isinstance(width, int)
        assert isinstance(height, int)
        x2 = x1 + width
        y2 = y1 + height
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            3
        )

    def _draw_object_zone(
            self,
            frame: numpy.ndarray,
            weight: typing.Optional[float],
            x1: typing.Union[int, float], y1: typing.Union[int, float],
            x2: typing.Union[int, float], y2: typing.Union[int, float],
            color: tuple = (255, 255, 0)
    ):
        assert isinstance(frame, numpy.ndarray)
        assert isinstance(weight, float) or weight is None
        assert x1 <= x2
        assert y1 <= y2

        w = x2 - x1
        h = y2 - y1
        self._draw_rectangle(frame, x1, y1, w, h, color)

        if weight is not None:
            text = '{0:.2f}'.format(weight)
            text_x1 = int(x1)
            text_y1 = int(y1 - 10)

            (width, height), _ = cv2.getTextSize(
                text,
                cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1,
                thickness=2
            )
            text_x2 = text_x1 + width
            text_y2 = text_y1 - height

            cv2.rectangle(
                frame,
                (text_x1 - 7, text_y1 + 4),
                (text_x2 + 7, text_y2 - 4),
                color=(0, 0, 0),
                thickness=-1
            )

            cv2.putText(
                frame,
                text,
                (text_x1, text_y1),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1,
                color=(0, 0, 255),
                thickness=2
            )
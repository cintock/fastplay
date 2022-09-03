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

    # какая минимальная оценка похожести нужна, чтобы учитывать объект
    _DETECTION_THRESHOLD = 0.7

    # какую часть выходного кадра будет занимать изображение
    _IMAGE_COEF_FULL_FRAME = 0.9

    _NUMPY_ARR_WIDTH_INDEX = 1
    _NUMPY_ARR_HEIGHT_INDEX = 0

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

        # признак, что найден объект (объекты) с достаточным весом
        object_detected = False

        # если получены данные распознавания
        if len(boxes) > 0:
            for box, weight in zip(boxes, weights):
                if weight > self._DETECTION_THRESHOLD:
                    x1_det = int(box[0])
                    y1_det = int(box[1])
                    width_det = int(box[2])
                    height_det = int(box[3])
                    x2_det = x1_det + width_det
                    y2_det = y1_det + height_det

                    # переход от координат изображения на котором распознавалось к координатам исходного изображения
                    x1, y1 = self._coord_processed_image_to_image(x1_det, y1_det)
                    x2, y2 = self._coord_processed_image_to_image(x2_det, y2_det)

                    # переход от координат исходного изображения к координатам выходного кадра
                    x1, y1 = self._coord_image_to_full_frame(x1, y1)
                    x2, y2 = self._coord_image_to_full_frame(x2, y2)

                    self._draw_object_zone(
                        output_frame, float(weight),
                        x1, y1, x2, y2
                    )

                    self._draw_object_zone(processed_frame, weight, x1_det, y1_det, x2_det, y2_det)

                    object_detected = True

        if object_detected:
            # получим ширину и высоту окна распознавания в координатах изображения на котором распознавалось
            detection_window_width = self._hog.winSize[0]
            detection_window_height = self._hog.winSize[1]

            # посчитаем координаты окна распознавания, чтобы поместить его слева внизу
            # (координаты в системе изображения на котором распознавалось)
            detection_window_x1 = 0
            detection_window_y1 = self._PROCESSED_FRAME_RESOLUTION_HEIGHT - detection_window_height
            detection_window_x2 = detection_window_x1 + detection_window_width
            detection_window_y2 = detection_window_y1 + detection_window_height

            self._draw_rectangle(
                processed_frame,
                detection_window_x1, detection_window_y1,
                detection_window_x2, detection_window_y2
            )

            # перейдем к координатам исходного изображения
            detection_window_x1, detection_window_y1 = self._coord_processed_image_to_image(
                detection_window_x1, detection_window_y1)
            detection_window_x2, detection_window_y2 = self._coord_processed_image_to_image(
                detection_window_x2, detection_window_y2)

            # перейдем к координатам полного изображения
            detection_window_x1, detection_window_y1 = self._coord_image_to_full_frame(
                detection_window_x1, detection_window_y1)
            detection_window_x2, detection_window_y2 = self._coord_image_to_full_frame(
                detection_window_x2, detection_window_y2)

            detection_window_width = detection_window_x2 - detection_window_x1
            detection_window_height = detection_window_y2 - detection_window_y1

            self._draw_rectangle(
                output_frame,
                detection_window_x1, detection_window_y1,
                detection_window_width, detection_window_height,
                color=(0, 0, 0)
            )

            cv2.imshow('detection', output_frame)
            cv2.imshow('processed_frame', processed_frame)
            self._out_video.write(output_frame)

    def end_detection(self):
        self._out_video.release()

    def _coord_processed_image_to_image(self, x: int, y: int) -> typing.Tuple[int, int]:
        """
        Переход от координат обрабатываемого изображения к координатам исходного изображения.
        :param x: значение x
        :param y: значение y
        :return: (x, y)
        """
        x_image_frame = round(x * self._resize_coef)
        y_image_frame = round(y * self._resize_coef)
        return x_image_frame, y_image_frame

    def _coord_image_to_full_frame(self, x: int, y: int) -> typing.Tuple[int, int]:
        """
        Переход от координат исходного изображения к координатам выходного кадра.
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
            1
        )

    def _draw_object_zone(
            self,
            frame: numpy.ndarray,
            weight: typing.Optional[float],
            x1: int,
            y1: int,
            x2: int,
            y2: int,
            color: tuple = (255, 255, 0)
    ):
        assert isinstance(frame, numpy.ndarray)
        assert isinstance(weight, float) or weight is None
        assert isinstance(x1, int)
        assert isinstance(y1, int)
        assert isinstance(x2, int)
        assert isinstance(y2, int)
        assert x1 <= x2
        assert y1 <= y2

        w = x2 - x1
        h = y2 - y1
        self._draw_rectangle(frame, x1, y1, w, h, color)

        if weight is not None:
            text = '{0:.2f}'.format(weight)
            text_x1 = x1
            text_y1 = y1 - 10
            self._print_text(frame, text_x1, text_y1, text)

    def _print_text(self, frame: numpy.ndarray, x: int, y: int, text: str):
        assert isinstance(frame, numpy.ndarray)
        assert isinstance(x, int)
        assert isinstance(y, int)
        assert isinstance(text, str)

        (width, height), _ = cv2.getTextSize(
            text,
            cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            thickness=2
        )
        x2 = x + width
        y2 = y - height

        cv2.rectangle(
            frame,
            (x - 7, y + 4),
            (x2 + 7, y2 - 4),
            color=(0, 0, 0),
            thickness=-1
        )

        cv2.putText(
            frame,
            text,
            (x, y),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(0, 0, 255),
            thickness=2
        )

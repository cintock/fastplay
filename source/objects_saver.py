#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy

from source.utils import Frozen


class ObjectSaver(Frozen):
    """
    Класс для сохранения объектов из кадра в файл
    """

    def __init__(self):
        super().__init__()
        self._n = 0
        self.freeze()

    def reset(self):
        self._n = 0

    def save_object(
            self,
            frame: numpy.ndarray,
            x1: int, y1: int,
            w: int, h: int,
            weight: float
    ):
        x2 = x1 + w
        y2 = y1 + h
        obj_image = frame[
                    round(y1): round(y2),
                    round(x1): round(x2)
        ]
        self._n += 1
        cv2.imshow('person', obj_image)
        cv2.imwrite(r'img\obj_{0:0f}_{1}.jpeg'.format(weight * 100, self._n), obj_image)
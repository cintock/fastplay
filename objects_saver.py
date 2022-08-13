#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy

from utils.frozen import Frozen


class ObjectSaver(Frozen):
    """
    Класс для сохранения объектов из кадра в файл
    """

    def __init__(self):
        super().__init__()
        self._n = 0
        self._resize_coef: float = 1.0
        self.freeze()

    @property
    def resize_coef(self):
        return self._resize_coef

    @resize_coef.setter
    def resize_coef(self, value: float):
        assert isinstance(value, float)
        self._resize_coef = value

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
                    round(y1 * self._resize_coef): round(y2 * self._resize_coef),
                    round(x1 * self._resize_coef): round(x2 * self._resize_coef)
        ]
        self._n += 1
        cv2.imshow('person', obj_image)
        cv2.imwrite(r'img\obj_{0:0f}_{1}.jpeg'.format(weight * 100, self._n), obj_image)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import typing
from abc import ABC

import numpy

from i_frame_post_processor import IFramePostProcessor
from object_detector import ObjectDetector


class PersonDetectorFramePostprocessor(IFramePostProcessor):
    def __init__(self, filename: str):
        self._person_detector = ObjectDetector()
        self._person_detector.set_output_filename(filename)

    def __enter__(self):
        # todo: определять
        self._person_detector.begin_detection(1920, 1080)
        return self

    def process_frame(self, frame: numpy.ndarray):
        self._person_detector.process_frame(frame)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._person_detector.end_detection()

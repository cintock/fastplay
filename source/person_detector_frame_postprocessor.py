#!/usr/bin/env python
# -*- coding: utf-8 -*-
import typing

import numpy

from source.i_frame_post_processor import IFramePostProcessor
from source.object_detector import ObjectDetector


class PersonDetectorFramePostprocessor(IFramePostProcessor):
    def __init__(self, filename: typing.Optional[str]):
        self._person_detector: typing.Optional[ObjectDetector] = None
        if filename is not None:
            self._person_detector = ObjectDetector()
            self._person_detector.set_output_filename(filename)

    def __enter__(self):
        if self._person_detector is not None:
            # todo: определять
            self._person_detector.begin_detection(1920, 1080)
        return self

    def is_enabled(self) -> bool:
        return self._person_detector is not None

    def process_frame(self, frame: numpy.ndarray):
        assert self._person_detector is not None
        self._person_detector.process_frame(frame)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._person_detector is not None:
            self._person_detector.end_detection()


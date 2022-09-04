#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import abstractmethod, ABC

import numpy


class IFramePostProcessor(ABC):
    @abstractmethod
    def process_frame(self, frame: numpy.ndarray):
        pass

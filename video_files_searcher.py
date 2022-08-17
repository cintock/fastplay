#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import glob
import os
from typing import List

from utils.frozen import Frozen


class VideoFilesSearcher(Frozen):
    def __init__(self):
        super().__init__()
        self._prefix_pattern: str = ''
        self._suffix_pattern: str = ''
        self._strftime_pattern: str = ''
        self.freeze()

    @property
    def prefix_pattern(self) -> str:
        return self._prefix_pattern

    @prefix_pattern.setter
    def prefix_pattern(self, value: str):
        assert isinstance(value, str)
        self._prefix_pattern = value

    @property
    def suffix_pattern(self) -> str:
        return self._suffix_pattern

    @suffix_pattern.setter
    def suffix_pattern(self, value: str):
        assert isinstance(value, str)
        self._suffix_pattern = value

    def get_pattern_for_datetime(self, dt: datetime.datetime):
        assert isinstance(dt, datetime.datetime)
        return self._prefix_pattern + dt.strftime('%Y%m%d%H') + self._suffix_pattern

    def search_video_files(self, dir: str) -> List[str]:
        assert os.path.isdir(dir)
        video_files: List[str] = []
        current_date = datetime.datetime.now()
        begin_date = current_date - datetime.timedelta(hours=24, minutes=2)
        for i in range(24):
            selected_time = begin_date + datetime.timedelta(hours=i)
            pattern = self.get_pattern_for_datetime(selected_time)
            files = glob.glob('{dir}\\{pattern}'.format(dir=dir, pattern=pattern))
            video_files.extend(files)
        return video_files
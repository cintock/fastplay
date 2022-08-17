#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from pathlib import Path
from typing import Optional, List

from utils.frozen import Frozen


class TaskDescription(Frozen):
    def __init__(self):
        super().__init__()
        self._input_files: List[str] = []
        self._output_concatenation_filename: Optional[str] = None
        self._auto_add_date: bool = True
        self._prefix_strftime_format = '%Y%m%d%H%M'
        self.freeze()

    @property
    def input_files(self) -> List[str]:
        return self._input_files

    @input_files.setter
    def input_files(self, value: List[str]):
        assert isinstance(value, list)
        assert all([isinstance(name, str) for name in value])
        self._input_files = value

    @property
    def output_concatenation_filename(self):
        return self._output_concatenation_filename

    @output_concatenation_filename.setter
    def output_concatenation_filename(self, value: Optional[str]):
        assert isinstance(value, str) or value is None
        self._output_concatenation_filename = value

    @property
    def auto_add_date_prefix_to_result_file(self):
        return self._auto_add_date

    @auto_add_date_prefix_to_result_file.setter
    def auto_add_date_prefix_to_result_file(self, value: bool):
        assert isinstance(value, bool)
        self._auto_add_date = value

    def get_actual_output_concatenation_filename(self) -> Path:
        """
        Получить актуальный путь к файлу, куда будет помещен результат объединения.
        В случае необходимости модифицирует имя файла префиксом с датой-временем
        :return: путь к файлу с результатом объединения
        """
        prefix = ''
        if self._auto_add_date:
            current_date = datetime.datetime.now()
            prefix = current_date.strftime(self._prefix_strftime_format) + '_'
        path = Path(self.output_concatenation_filename)
        dirname = path.parent
        filename = path.name
        actual_filename_only = prefix + filename
        actual_full_filename = dirname / actual_filename_only
        assert isinstance(actual_full_filename, Path)
        return actual_full_filename

    def check(self) -> bool:
        return all([
            self._output_concatenation_filename is not None
        ])

    def __str__(self) -> str:
        return f'Task (input[{self._input_files}]: output[{self._output_concatenation_filename}])'

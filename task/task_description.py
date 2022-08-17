#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from pathlib import Path
from typing import Optional

from utils.frozen import Frozen


class TaskDescription(Frozen):
    def __init__(self):
        super().__init__()
        self._input_folder: Optional[str] = None
        self._output_concatenation_filename: Optional[str] = None
        self._auto_add_date: bool = True
        self.freeze()

    @property
    def input_folder(self):
        return self._input_folder

    @input_folder.setter
    def input_folder(self, value: Optional[str]):
        assert isinstance(value, str) or value is None
        self._input_folder = value

    @property
    def output_concatenation_filename(self):
        return self._output_concatenation_filename

    @output_concatenation_filename.setter
    def output_concatenation_filename(self, value: Optional[str]):
        assert isinstance(value, str) or value is None
        self._output_concatenation_filename = value

    @property
    def auto_add_date(self):
        return self._auto_add_date

    @auto_add_date.setter
    def auto_add_date(self, value: bool):
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
            prefix = current_date.strftime('%Y%m%d%H%M') + '_'
        path = Path(self.output_concatenation_filename)
        dirname = path.parent
        filename = path.name
        actual_filename_only = prefix + filename
        actual_full_filename = dirname / actual_filename_only
        assert isinstance(actual_full_filename, Path)
        return actual_full_filename

    def check(self) -> bool:
        return all([
            self._output_concatenation_filename is not None,
            self._input_folder is not None
        ])

    def __str__(self) -> str:
        return f'Task (input[{self._input_folder}]: output[{self._output_concatenation_filename}])'

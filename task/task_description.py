#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import pathlib
from pathlib import Path
from typing import Optional, List

from utils.frozen import Frozen


class TaskDescription(Frozen):
    def __init__(self):
        super().__init__()
        self._input_files: List[str] = []
        self._output_concatenation_filename: Optional[str] = None
        self._auto_add_date: bool = True
        self._prefix_strftime_format: str = '%Y%m%d%H%M'
        self._output_video_width: int = 960
        self._output_video_height: int = 540
        self._skipped_frames_count: int = 110
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

    @property
    def output_video_width(self) -> int:
        return self._output_video_width

    @output_video_width.setter
    def output_video_width(self, value: int):
        assert isinstance(value, int)
        self._output_video_width = value

    @property
    def output_video_height(self) -> int:
        return self._output_video_height

    @output_video_height.setter
    def output_video_height(self, value: int):
        assert isinstance(value, int)
        self._output_video_height = value

    @property
    def skipped_frames_count(self):
        return self._skipped_frames_count

    @skipped_frames_count.setter
    def skipped_frames_count(self, value: int):
        assert isinstance(value, int)
        self._skipped_frames_count = value

    @property
    def output_object_detection_filename(self):
        # todo: сделать задаваемым
        fn = self.output_concatenation_filename
        p = Path(fn)
        p.pa

    def get_actual_output_concatenation_filename(self) -> Path:
        """
        Получить актуальный путь к файлу, куда будет помещен результат объединения.
        В случае необходимости модифицирует имя файла префиксом с датой-временем
        :return: путь к файлу с результатом объединения
        """
        actual_full_filename = self._get_actual_filename(self.output_concatenation_filename)
        return actual_full_filename

    def get_actual_output_object_detection_filename(self) -> Path:
        # todo: сделать задаваемым
        actual_full_filename = self._get_actual_filename('person.mp4')
        return actual_full_filename

    def check(self) -> bool:
        result = self._output_concatenation_filename is not None
        result = result and pathlib.Path(self._output_concatenation_filename).parent.exists()
        return result

    def _get_actual_filename(self, simple_filename: str):
        path = Path(simple_filename)
        prefix = ''
        if self._auto_add_date:
            current_date = datetime.datetime.now()
            prefix = current_date.strftime(self._prefix_strftime_format) + '_'
        dirname = path.parent
        filename = path.name
        actual_filename_only = prefix + filename
        actual_full_filename = dirname / actual_filename_only
        assert isinstance(actual_full_filename, Path)
        return actual_full_filename

    def __str__(self) -> str:
        return \
            f'--- Описание задачи ---\n' \
            f'    Количество входных файлов: {len(self._input_files)}\n' \
            f'    Имя выходного файла с результатами объединения "{self._output_concatenation_filename}"\n' \
            f'    Пример результирующего имени выходного файла "{self.get_actual_output_concatenation_filename()}"\n' \
            f'    Автоматически добавлять префикс-дату к имени выходного файла: ' \
            f'{"Да" if self._auto_add_date else "Нет"}\n' \
            f'    Формат префикса strftime для выходного файла: {self._prefix_strftime_format}\n' \
            f'    Ширина выходного видео: {self._output_video_width}\n' \
            f'    Высота выходного видео: {self._output_video_height}\n' \
            f'    Пропускать каждый {self._skipped_frames_count} кадр\n' \
            f'--- конец ---'

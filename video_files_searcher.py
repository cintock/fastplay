#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import glob
import os
from typing import List, Set, Optional

from utils.frozen import Frozen


class VideoFilesSearcher(Frozen):
    """
    Класс поиска видеофайлов для указанных дат.
    Например, если заданы настройки

    video_files_searcher = VideoFilesSearcher()

    # указываем, что после шаблона даты-времени могут быть любые символы, но расширение файла обязательно h264
    video_files_searcher.suffix_pattern = '*.h264'

    # указываем шаблон даты времени ГОД МЕСЯЦ ДЕНЬ ЧАС (без пробелов)
    video_files_searcher.strftime_pattern = '%Y%m%d%H'

    # префикс не задаем, поэтому имя файла должно строго начинаться с шаблона даты-времени
    # (то есть с года в нашем случае)

    res = video_files_searcher.search_video_files(r'T:\Record\cam vet 2\1')

    будет такой результат

    T:\Record\cam vet 2\1\20220816180000.h264
    T:\Record\cam vet 2\1\20220816190000.h264
    T:\Record\cam vet 2\1\20220816200000.h264
    T:\Record\cam vet 2\1\20220816210000.h264
    T:\Record\cam vet 2\1\20220816220000.h264
    T:\Record\cam vet 2\1\20220816230001.h264
    T:\Record\cam vet 2\1\20220817000000.h264
    T:\Record\cam vet 2\1\20220817010001.h264
    T:\Record\cam vet 2\1\20220817020000.h264
    T:\Record\cam vet 2\1\20220817030001.h264
    T:\Record\cam vet 2\1\20220817040000.h264
    T:\Record\cam vet 2\1\20220817050000.h264
    T:\Record\cam vet 2\1\20220817060000.h264
    T:\Record\cam vet 2\1\20220817070000.h264
    T:\Record\cam vet 2\1\20220817080000.h264
    T:\Record\cam vet 2\1\20220817090000.h264
    T:\Record\cam vet 2\1\20220817100000.h264
    T:\Record\cam vet 2\1\20220817110000.h264
    T:\Record\cam vet 2\1\20220817120818.h264
    T:\Record\cam vet 2\1\20220817130000.h264
    T:\Record\cam vet 2\1\20220817140000.h264
    T:\Record\cam vet 2\1\20220817150000.h264
    T:\Record\cam vet 2\1\20220817160000.h264
    T:\Record\cam vet 2\1\20220817170000.h264

    (обратите внимание, что есть файлы, где минуты и секунды не равны 0, и они тоже добавлены,
    что и требуется в данном случае).

    Еще пример как можно получить тот же список файлов
    (понятно, что так делать не нужно в данном случае, просто для понимания синтаксиса):
    video_files_searcher.prefix_pattern = '20??'
    video_files_searcher.suffix_pattern = '*.h264'
    video_files_searcher.strftime_pattern = '%m%d%H'
    """

    _MINUTES_PER_HOUR = 60

    def __init__(self):
        super().__init__()
        self._prefix_pattern: str = ''
        self._suffix_pattern: str = ''
        self._strftime_pattern: str = ''

        # точка начала отсчета времени (если None, то текущая дата-время),
        # от этой точки отсчитываем дельту времени НАЗАД
        self._reference_date: Optional[datetime.datetime] = None

        # начинаем поиск по файлам за 25 часов и 2 минуты назад относительно начальной точки (или текущего времени)
        self._reference_date_delta_hours: int = 25
        self._reference_date_delta_minutes: int = 2

        # продолжительность поиска с начальной точки времени 24 часа и 0 минут
        self._video_length_hours: int = 24
        self._video_length_minutes: int = 0

        self.freeze()

    @property
    def prefix_pattern(self) -> str:
        """
        Шаблон имени файла с которого начинается имя видеофайла. Может содержать спецсимволы * и ?
        Например, если имя файла имеет вид Camera_1_2022-08-17-10-00-00.mp4, то шаблон префикса может быть Camera_1_
        :return: шаблон префикса видеофайла
        """
        return self._prefix_pattern

    @prefix_pattern.setter
    def prefix_pattern(self, value: str):
        assert isinstance(value, str)
        self._prefix_pattern = value

    @property
    def suffix_pattern(self) -> str:
        """
        Шаблон суффикса видеофайла. Может содержать спецсимволы * и ?
        Должен включать расширение видеофайла. Например, для случая Camera_1_2022-08-17-10-00-00.mp4
        шаблон суффикса может быть *.mp4
        :return:
        """
        return self._suffix_pattern

    @suffix_pattern.setter
    def suffix_pattern(self, value: str):
        assert isinstance(value, str)
        self._suffix_pattern = value

    @property
    def strftime_pattern(self) -> str:
        """
        Шаблон имени файла с датой временем. Содержит символы, которые разбирает Питоновский метод strftime.
        Например, для случая Camera_1_2022-08-17-10-15-00.mp4 может быть %Y-%m-%d-%H если интересует
        захват времени без минут, или %Y-%m-%d-%H-%M если нужен захват времени с минутами.
        Какой формат использовать, зависит от того, как настроен видеорегистратор
        (создавать видео через часы или через интервал в минутах)
        :return:
        """
        return self._strftime_pattern

    @strftime_pattern.setter
    def strftime_pattern(self, value: str):
        assert isinstance(value, str)
        self._strftime_pattern = value

    @property
    def reference_date(self) -> Optional[datetime.datetime]:
        return self._reference_date

    @reference_date.setter
    def reference_date(self, value: Optional[datetime.datetime]):
        assert isinstance(value, datetime.datetime) or value is None
        self._reference_date = value

    @property
    def reference_date_delta_hours(self) -> int:
        return self._reference_date_delta_hours

    @reference_date_delta_hours.setter
    def reference_date_delta_hours(self, value: int):
        assert isinstance(value, int)
        self._reference_date_delta_hours = value

    @property
    def reference_date_delta_minutes(self) -> int:
        return self._reference_date_delta_minutes

    @reference_date_delta_minutes.setter
    def reference_date_delta_minutes(self, value: int):
        assert isinstance(value, int)
        self._reference_date_delta_minutes = value

    @property
    def video_length_hours(self) -> int:
        return self._video_length_hours

    @video_length_hours.setter
    def video_length_hours(self, value: int):
        assert isinstance(value, int)
        self._video_length_hours = value

    @property
    def video_length_minutes(self) -> int:
        return self._video_length_minutes

    @video_length_minutes.setter
    def video_length_minutes(self, value: int):
        assert isinstance(value, int)
        self._video_length_minutes = value

    def get_actual_reference_date_point(self) -> datetime.datetime:
        """
        Получить точку начала отсчета времени (от которого считаем дельту по времени НАЗАД).
        Если начальная точка отсчета времени не задана, то будет взято текущее время
        :return: точка отсчета времени
        """
        return self._reference_date or datetime.datetime.now()

    def get_pattern_for_datetime(self, dt: datetime.datetime):
        assert isinstance(dt, datetime.datetime)
        return self._prefix_pattern + dt.strftime(self._strftime_pattern) + self._suffix_pattern

    def search_video_files(self, dir: str) -> List[str]:
        assert os.path.isdir(dir)
        video_files: List[str] = []

        # будет происходить дублирующее добавление в множество
        # (оптимизация времени выполнения за счет затрат памяти)
        video_files_set: Set[str] = set()

        date_reference_point = self.get_actual_reference_date_point()
        begin_date = date_reference_point - datetime.timedelta(
            hours=self._reference_date_delta_hours,
            minutes=self._reference_date_delta_minutes
        )
        search_length_minutes = (self._video_length_hours * self._MINUTES_PER_HOUR) + self._video_length_minutes
        for current_minute in range(search_length_minutes):
            selected_time = begin_date + datetime.timedelta(minutes=current_minute)
            pattern = self.get_pattern_for_datetime(selected_time)
            files = glob.glob('{dir}\\{pattern}'.format(dir=dir, pattern=pattern))
            files.sort()
            for file in files:
                if file not in video_files_set:
                    video_files.append(file)
                    video_files_set.add(file)
        return video_files


if __name__ == '__main__':
    # тестирование
    video_files_searcher = VideoFilesSearcher()
    video_files_searcher.prefix_pattern = '20??'
    video_files_searcher.suffix_pattern = '*.h264'
    video_files_searcher.strftime_pattern = '%m%d%H%M'
    # video_files_searcher.reference_date = datetime.datetime(2022, 8, 17, 19, 1, 50, 0)
    res = video_files_searcher.search_video_files(r'T:\Record\cam vet 2\1')
    for r in res:
        print(r)
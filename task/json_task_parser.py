#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json
import os.path
import typing

from task.task_description import TaskDescription
from video_files_searcher import VideoFilesSearcher


class JsonTaskParserException(Exception):
    def __init__(self, mes: str):
        self._mes = mes

    def __str__(self):
        return self._mes


class JsonTaskParser:
    def __init__(self):
        pass

    def tasks_from_json(self, text: str) -> typing.List[TaskDescription]:
        text = self._delete_comments(text)
        root_json_dict = json.loads(text)
        tasks = root_json_dict['tasks']
        tasks_description = []
        for task in tasks:
            task_description = self.task_from_dict(task)
            if task_description is not None:
                tasks_description.append(task_description)
        return tasks_description

    def task_from_dict(self, task_dict: dict) -> typing.Optional[TaskDescription]:
        assert isinstance(task_dict, dict)
        task = None
        object_type = task_dict.get('type')
        if object_type != 'process_video_task':
            raise JsonTaskParserException(f'Ожидался тип process_video_task, получен "{object_type}"')

        task = TaskDescription()
        task.input_files = self._get_input_files(task_dict)
        try:
            task.output_concatenation_filename = task_dict['output_concatenation_filename']
        except KeyError:
            raise JsonTaskParserException('Не задан параметр output_concatenation_filename')

        task.output_video_width = task_dict.get('output_video_width', task.output_video_width)
        task.output_video_height = task_dict.get('output_video_height', task.output_video_height)
        task.skipped_frames_count = task_dict.get('skipped_frames_count', task.skipped_frames_count)

        return task

    def _get_input_files(self, task_dict: dict) -> typing.List[str]:
        input_files = task_dict.get('input_files')
        video_searcher = task_dict.get('video_searcher')
        if input_files is not None:
            for input_file in input_files:
                if not isinstance(input_file, str):
                    raise JsonTaskParserException('Ошибка. Входные файлы должны быть строками')
                if not os.path.isfile(input_file):
                    raise JsonTaskParserException('Не является файлом: "{0}"'.format(input_file))
            print('Использован список входных файлов')
            input_files = input_files
        else:
            if video_searcher is None:
                raise JsonTaskParserException(
                    'Ошибка: список файлов должен быть задан либо'
                    ' списком (input_files), либо поисковиком (video_searcher)')
            if not isinstance(video_searcher, dict):
                raise JsonTaskParserException(
                    f'video_searcher должен иметь тип словарь, получен {type(video_searcher)}')
            searcher = VideoFilesSearcher()
            searcher.video_length_hours = video_searcher['video_length_hours']
            searcher.video_length_minutes = video_searcher['video_length_minutes']
            searcher.prefix_pattern = video_searcher.get('prefix_pattern', '')
            searcher.suffix_pattern = video_searcher.get('suffix_pattern', '')
            searcher.strftime_pattern = video_searcher['strftime_pattern']
            reference_date_str: typing.Optional[str] = video_searcher.get('reference_date', None)
            if reference_date_str is None:
                searcher.reference_date = None
            else:
                searcher.reference_date = datetime.datetime.strptime(reference_date_str, '%Y-%m-%d %H:%M')
                print('Дата начала отсчета: {0}'.format(searcher.reference_date))
            searcher.reference_date_delta_hours = video_searcher['reference_date_delta_hours']
            searcher.reference_date_delta_minutes = video_searcher['reference_date_delta_minutes']
            input_files = searcher.search_video_files(video_searcher['dir'])
            print('Заданы настройки поисковика:')
            print(searcher)
            print(f'Поисковик нашел следующие видео ({len(input_files)}) по критериям:')
            print('--- начало ---')
            for input_file in input_files:
                print(input_file)
            print('--- конец ---')
        return input_files

    @staticmethod
    def _delete_comments(text: str) -> str:
        lines = text.splitlines()
        return '\n'.join([line for line in lines if not line.startswith('--')])

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os.path

from source.task.json_task_parser import JsonTaskParser, JsonTaskParserException
from source.task_processor import TaskProcessor


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('json_config_filename')
    argument_parser.add_argument('--only_info', '-i', action='store_true')
    args = argument_parser.parse_args()
    json_config_filename = args.json_config_filename
    only_info = args.only_info
    print(f'Получен файл с настройками: {json_config_filename}')
    exit_code = 0
    try:
        if os.path.isfile(json_config_filename):
            with open(json_config_filename, 'r') as file:
                file_content = file.read()

            parser = JsonTaskParser()
            tasks = parser.tasks_from_json(file_content)
            for task in tasks:
                print(task)

            all_task_correct = True
            for task in tasks:
                if not task.check():
                    all_task_correct = False
                    print('Не могу обработать задачу. Задача не корректная: {0}'.format(task))

            if not only_info:
                is_interrupted = False
                if all_task_correct:
                    task_processor = TaskProcessor()
                    for task in tasks:
                        task_processor.process_task(task)
                        if task_processor.is_exit_requested():
                            exit_code = 4
                            break

        else:
            print(f'Файл с настройками не найден: {json_config_filename}')
            exit_code = 2
    except JsonTaskParserException as error:
        print(f'Обнаружена ошибка: {error}')
        exit_code = 3

    exit(exit_code)

    # searcher = VideoFilesSearcher()
    # searcher.strftime_pattern = '%Y%m%d%H'
    # searcher.suffix_pattern = '*.h264'
    # searcher.reference_date_delta_hours = 25
    # searcher.reference_date_delta_minutes = 2
    # searcher.video_length_hours = 24
    # searcher.video_length_minutes = 0
    #
    # cam2_task = TaskDescription()
    # cam2_task.input_files = searcher.search_video_files(r'T:\Record\cam vet 2\1')
    # cam2_task.output_video_width = 1920
    # cam2_task.output_video_height = 1080
    # cam2_task.skipped_frames_count = 120
    # cam2_task.output_concatenation_filename = r'T:\CamRecordAnalysis\cam2.mkv'
    #
    # cam3_task = TaskDescription()
    # cam3_task.input_files = searcher.search_video_files(r'T:\Record\ip cam vet 3\1')
    # cam3_task.output_video_width = 1920
    # cam3_task.output_video_height = 1080
    # cam3_task.skipped_frames_count = 120
    # cam3_task.output_concatenation_filename = r'T:\CamRecordAnalysis\cam3.mkv'
    #
    # processed_tasks = [cam2_task, cam3_task]
    #



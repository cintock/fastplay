#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2

from task.task_description import TaskDescription
from task_processor import TaskProcessor
from video_files_searcher import VideoFilesSearcher


if __name__ == '__main__':
    searcher = VideoFilesSearcher()
    searcher.strftime_pattern = '%Y%m%d%H'
    searcher.suffix_pattern = '*.h264'
    searcher.reference_date_delta_hours = 25
    searcher.reference_date_delta_minutes = 2
    searcher.video_length_hours = 24
    searcher.video_length_minutes = 0

    cam2_task = TaskDescription()
    cam2_task.input_files = searcher.search_video_files(r'T:\Record\cam vet 2\1')
    cam2_task.output_video_width = 1920
    cam2_task.output_video_height = 1080
    cam2_task.skipped_frames_count = 120
    cam2_task.output_concatenation_filename = r'T:\CamRecordAnalysis\cam2.mkv'

    cam3_task = TaskDescription()
    cam3_task.input_files = searcher.search_video_files(r'T:\Record\ip cam vet 3\1')
    cam3_task.output_video_width = 1920
    cam3_task.output_video_height = 1080
    cam3_task.skipped_frames_count = 120
    cam3_task.output_concatenation_filename = r'T:\CamRecordAnalysis\cam3.mkv'

    processed_tasks = [cam2_task, cam3_task]

    all_task_correct = True
    for task in processed_tasks:
        if not task.check():
            all_task_correct = False
            print('Can not process task. Task is not correct: {0}'.format(task))

    if all_task_correct:
        task_processor = TaskProcessor()
        try:
            for task in processed_tasks:
                task_processor.process_task(task)
                if task_processor.is_exit_requested():
                    break
        finally:
            cv2.destroyAllWindows()

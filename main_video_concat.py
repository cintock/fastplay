#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2

from task.task_description import TaskDescription
from video_concatenator import VideoConcatenator
from video_files_searcher import VideoFilesSearcher


def process_task(task_description: TaskDescription):
    assert isinstance(task_description, TaskDescription)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_video_resolution = (task_description.output_video_width, task_description.output_video_height)
    output_video = cv2.VideoWriter(
        str(task_description.get_actual_output_concatenation_filename()),
        fourcc,
        30.0,
        output_video_resolution
    )
    try:
        concatenator = VideoConcatenator(output_video, task_description.output_video_width, task_description.output_video_height)
        for file in task_description.input_files:
            input_video = cv2.VideoCapture(file)
            try:
                print('process: {0}'.format(file))
                concatenator.append_video(input_video)
                print('avg frame time: ', concatenator.get_avg_frame_time())
                concatenator.reset_avg_frame_time()
            finally:
                input_video.release()
    finally:
        output_video.release()


if __name__ == '__main__':
    searcher = VideoFilesSearcher()
    searcher.strftime_pattern = '%Y%m%d%H'
    searcher.suffix_pattern = '*.h264'
    searcher.reference_date_delta_hours = 3
    searcher.reference_date_delta_minutes = 2
    searcher.video_length_hours = 2
    searcher.video_length_minutes = 0

    cam2_task = TaskDescription()
    cam2_task.input_files = searcher.search_video_files(r'T:\Record\cam vet 2\1')
    cam2_task.output_concatenation_filename = r'T:\CamRecordAnalysis\cam2.mp4'

    cam3_task = TaskDescription()
    cam3_task.input_files = searcher.search_video_files(r'T:\Record\ip cam vet 3\1')
    cam3_task.output_concatenation_filename = r'T:\CamRecordAnalysis\cam3.mp4'

    processed_tasks = [cam2_task, cam3_task]

    all_task_correct = True
    for task in processed_tasks:
        if not task.check():
            all_task_correct = False
            print('Can not process task. Task is not correct: {0}'.format(task))

    if all_task_correct:
        try:
            for task in processed_tasks:
                process_task(task)
        finally:
            cv2.destroyAllWindows()

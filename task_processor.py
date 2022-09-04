#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2

from person_detector_frame_postprocessor import PersonDetectorFramePostprocessor
from task.task_description import TaskDescription
from video_concatenator import VideoConcatenator


class TaskProcessor:
    def __init__(self):
        self._is_exit_requested: bool = False

    def process_task(self, task_description: TaskDescription):
        assert isinstance(task_description, TaskDescription)
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        output_video_resolution = (task_description.output_video_width, task_description.output_video_height)
        output_video = cv2.VideoWriter(
            task_description.get_actual_output_concatenation_filename(),
            fourcc,
            30.0,
            output_video_resolution
        )
        try:
            concatenator = VideoConcatenator(
                output_video,
                task_description.output_video_width,
                task_description.output_video_height
            )
            object_detection_filename = task_description.get_actual_output_object_detection_filename()
            with PersonDetectorFramePostprocessor(object_detection_filename) as person_detector:
                if person_detector.is_enabled():
                    concatenator.add_post_processor(person_detector)
                concatenator.skipped_frames_count = task_description.skipped_frames_count
                for file in task_description.input_files:
                    input_video = cv2.VideoCapture(file)
                    try:
                        print('process: {0}'.format(file))
                        concatenator.append_video(input_video)
                        print('avg frame time: ', concatenator.get_avg_frame_time())
                        concatenator.reset_avg_frame_time()
                        if concatenator.is_exit_requested():
                            self._is_exit_requested = True
                            break
                    finally:
                        input_video.release()
        finally:
            output_video.release()
            cv2.destroyAllWindows()

    def is_exit_requested(self) -> bool:
        return self._is_exit_requested

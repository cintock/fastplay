#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import cv2
import time
import datetime
import glob
import numpy

from task.task_description import TaskDescription


def append_file(out: cv2.VideoWriter, input: cv2.VideoCapture):
    assert isinstance(out, cv2.VideoWriter)
    assert isinstance(input, cv2.VideoCapture)
    key = -1
    eof = False

    # счетчик неудачных попыток подряд получить кадр
    empty_count = 0

    # счетчик удачно полученных подряд кадров
    good_frames = 0

    frame_times = []
    while input.isOpened() and key != 27 and not eof:
        start_t = time.time()
        # vc.set(cv2.CAP_PROP_POS_FRAMES, frame_no)

        ret = input.grab()
        if not ret:
            good_frames = 0
            empty_count += 1

            # больше 150 подряд кадров не читаются (критерий, что файл завершен)
            # если только несколько кадров не читается, то это может быть просто битый участок
            eof = empty_count >= 150
        else:
            good_frames += 1
            empty_count = 0

        # чтобы кадр стал "хороший" (картинка стабилизировалась после ключевого кадра),
        # нужно после начала того, как что-то получено получить еще N кадров подряд
        if good_frames >= 100:
            ret, frame = input.retrieve()

            if ret:
                frame = cv2.resize(frame, (1920, 1080))
                cv2.imshow('frame', frame)

                out.write(frame)

                # пропускаем кадры (решение CAP_PROP_POS_FRAMES не срабатывает как надо для данного типа видео)
                for i in range(110):
                    input.grab()

                key = cv2.waitKey(1)
                end_t = time.time()
                frame_time = end_t - start_t
                frame_times.append(frame_time)
            else:
                good_frames = 0
                print('Can not retrieve grabbed frame!')

    avg_frame_time = numpy.average(frame_times)
    print('avg frame time: {0}'.format(avg_frame_time))


def search_video_files(dir: str):
    assert os.path.isdir(dir)
    video_files = []
    current_date = datetime.datetime.now()
    begin_date = current_date - datetime.timedelta(hours=24, minutes=2)
    print(begin_date)
    for i in range(24):
        selected_time = begin_date + datetime.timedelta(hours=i)
        pattern = selected_time.strftime('%Y%m%d%H') + '*'
        files = glob.glob('{dir}\\{pattern}.h264'.format(dir=dir, pattern=pattern))
        video_files.extend(files)
    return video_files


def process_task(task: TaskDescription):
    assert isinstance(task, TaskDescription)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(task.get_actual_output_concatenation_filename()), fourcc, 30.0, (1920, 1080))
    try:
        videofiles = search_video_files(str(task.input_folder))
        for file in videofiles:
            input = cv2.VideoCapture(file)
            try:
                print('process: {0}'.format(file))
                append_file(out, input)
            finally:
                input.release()
    finally:
        out.release()


if __name__ == '__main__':
    cam2_task = TaskDescription()
    cam2_task.input_folder = r'T:\Record\cam vet 2\1'
    cam2_task.output_concatenation_filename = 'cam2.mp4'

    cam3_task = TaskDescription()
    cam3_task.input_folder = r'T:\Record\ip cam vet 3\1'
    cam3_task.output_concatenation_filename = 'cam3.mp4'

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

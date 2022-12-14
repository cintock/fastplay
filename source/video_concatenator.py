#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import typing
from typing import Tuple
import cv2

from source.i_frame_post_processor import IFramePostProcessor
from source.utils.frozen import Frozen


class VideoConcatenator(Frozen):
    _EOF_FILE_ERROR_FRAMES_COUNT = 150
    _STABILISATION_FRAMES_COUNT = 100

    _KEY_ESC = 27
    _KEY_SPACE = 32

    def __init__(self, output_video: cv2.VideoWriter, out_frame_width: int, out_frame_height):
        super().__init__()
        assert isinstance(output_video, cv2.VideoWriter)
        assert isinstance(out_frame_width, int)
        assert isinstance(out_frame_height, int)
        assert output_video.isOpened()
        self._out_video_resolution: Tuple[int, int] = (out_frame_width, out_frame_height)
        self._output_video = output_video
        self._frame_times: float = 0.0
        self._frame_count: int = 0
        self._skipped_frames_count = 110

        self._post_processors: typing.List[IFramePostProcessor] = []

        # флаг активируется, если пользователь запросил выход
        self._exit_requested = False

        self.freeze()

    @property
    def skipped_frames_count(self) -> int:
        return self._skipped_frames_count

    @skipped_frames_count.setter
    def skipped_frames_count(self, value: int):
        assert isinstance(value, int)
        self._skipped_frames_count = value

    def add_post_processor(self, processor: IFramePostProcessor):
        assert isinstance(processor, IFramePostProcessor)
        self._post_processors.append(processor)

    def clear_all_post_processors(self):
        self._post_processors.clear()

    def append_video(self, input_video: cv2.VideoCapture):
        assert isinstance(input_video, cv2.VideoCapture)
        key = -1
        eof = False

        # счетчик неудачных попыток подряд получить кадр
        empty_count = 0

        # счетчик удачно полученных подряд кадров
        good_frames = 0

        while input_video.isOpened() and key not in [self._KEY_ESC, self._KEY_SPACE] and not eof:
            start_t = time.time()

            ret = input_video.grab()
            if not ret:
                good_frames = 0
                empty_count += 1

                # больше N подряд кадров не читаются (критерий, что файл завершен)
                # если только несколько кадров не читается, то это может быть просто битый участок
                eof = empty_count >= self._EOF_FILE_ERROR_FRAMES_COUNT
            else:
                good_frames += 1
                empty_count = 0

            # чтобы кадр стал "хороший" (картинка стабилизировалась после ключевого кадра),
            # нужно после начала того, как что-то получено получить еще N кадров подряд
            if good_frames >= self._STABILISATION_FRAMES_COUNT:
                ret, frame = input_video.retrieve()

                if ret:
                    # приводим кадр к размеру, который помещается в выходной файл
                    frame = cv2.resize(frame, self._out_video_resolution)
                    cv2.imshow('frame', frame)

                    self._output_video.write(frame)

                    for post_processor in self._post_processors:
                        post_processor.process_frame(frame)

                    # пропускаем кадры (решение CAP_PROP_POS_FRAMES не срабатывает как надо для данного типа видео)
                    for i in range(self._skipped_frames_count):
                        input_video.grab()

                    key = cv2.waitKey(1)
                    end_t = time.time()
                    frame_time = end_t - start_t
                    self._frame_times += frame_time
                    self._frame_count += 1
                else:
                    good_frames = 0
                    print('Can not retrieve grabbed frame!')
        if key == self._KEY_ESC:
            self._exit_requested = True

    def get_avg_frame_time(self) -> float:
        return self._frame_times / self._frame_count

    def reset_avg_frame_time(self):
        self._frame_times = 0.0
        self._frame_count = 0

    def is_exit_requested(self):
        return self._exit_requested

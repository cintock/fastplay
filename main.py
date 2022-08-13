import os

import cv2
import time
import datetime
import glob

import numpy


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


if __name__ == '__main__':
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('out3.avi', fourcc, 30.0, (1920, 1080))
    try:
        videofiles = search_video_files(r'T:\Record\cam vet 2\1')
        for file in videofiles:
            input = cv2.VideoCapture(file)
            try:
                print('process: {0}'.format(file))
                append_file(out, input)
            finally:
                input.release()
    finally:
        out.release()
        cv2.destroyAllWindows()

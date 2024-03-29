## Анализ камер видеонаблюдения

### Функциональность
- Собирает видео с каждой камеры за последние сутки в 12 минутный ролик. 
Результирующий ролик выглядит как:
  - объединение видео
  - ускоренное воспроизведение
- Анализирует наличие людей на видео, моменты, где есть люди записываются в отдельный видео файл

### Применение

При просмотре видео с камер наблюдения столкнулись с проблемой, что для того, чтобы
проанализировать видео за прошлый день нужно искать данные в большом объеме файлов, 
24 файла с каждой камеры. Например, знаем, что некоторое событие произошло днем. И нужно
отсмотреть видео с 11 до 16 часов включительно, это получается 6 файлов. Поскольку видео
пишется в архив в достаточно хорошем качестве, возникает еще проблема с быстрым воспроизведением.
При запуске ускоренного воспроизведения видео упираемся в жесткий диск и процессор. 
То есть не получится стандартными средствами воспроизвести часовое видео за одну минуту. 
И каждый из этих 6 файлов еще придется смотреть с перемотками, чтобы найти нужное событие.

Это приложение запускается в фоновом режиме планировщиком в определенное время и обрабатывает 
все видео за последние сутки, результат сгружая в один файл. И в этом ускоренном воспроизведении 
уже намного проще понять, в какое приблизительно время произошло событие. А дальше уже смотрят этот момент 
по времени в полном архиве, где воспроизведение не ускорено.

Также создается дополнительный файл с найденными людьми на видео. И для поиска необходимого
события бывает достаточно посмотреть этот файл 
(что может быть еще быстрее, если не было большого количества людей за день). Увидеть нужный 
момент и уже детально 
посмотреть его в полном архиве.

В качестве демонстрации приведем отрывок файла с результатом определением людей на видео

https://github.com/cintock/fastplay/assets/46611567/658245a3-914d-4bfd-a374-8086cefebb28


# zalupabot.py - скрипт для вставки залупного клоуна в видео из тиктока

## Запуск на windows:
1) Скачать сам скрипт [zalupabot.py](../../archive/refs/heads/main.zip) и видео с клоуном в одну папку
2) Установить [python](https://www.python.org/downloads/)
3) Скачать [ffmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-lgpl.zip)
4) Распаковать файлы `ffprobe.exe` и `ffmpeg.exe`, положить в папку со скриптом
5) Установить нужные библиотеки командой в консоли:

`python -m pip install TikTokApi`

`python -m playwright install`

5) Запустить скрипт командой: `python zalupabot.py`. При запуске без параметров скачивается одно случайное видео.

   Справка по параметрам скрипта: `python zalupabot.py -h`

## FAQ:

Q: Как быстро обработать много тиктоков с нужного аккаунта?

A:

1) Открыть в браузере аккаунт, пролистать ленту до нужного количества
2) Открыть консоль (F12 в firefox, ctrl+shift+J в хроме)
3) Вставить и запустить код:
```
{
var t = document.getElementsByTagName('a');
var s = '';
for (var i of t)
{
  var f = i.href.search('/video/');
  if (f != -1) s += i.href.substr(f+7) + ',';
}
console.log(s.substr(0, s.length-1));
}
```
4) Скопировать полученный список id в файл, запустить скрипт с этим файлом

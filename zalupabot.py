import os
import subprocess
import codecs
import random
import datetime
import argparse
import requests

from TikTokApi import TikTokApi

def processVideo(args, videoName):
    introDuration =  random.randint(int(args['s'].split(',')[0]), int(args['s'].split(',')[1]))
    if introDuration < 1:
        introDuration = 1
    outroDuration = random.randint(int(args['e'].split(',')[0]), int(args['e'].split(',')[1]))
    outputName = f"{random.randint(int(datetime.datetime(2021, 1, 1).timestamp()), int(datetime.datetime.now().timestamp()))}{random.randint(100,999)}"

    # прочитать ширину и высоту видео
    ffprobeOutput = subprocess.check_output(['ffprobe', "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", videoName])
    width, height = codecs.decode(ffprobeOutput, 'ascii').strip().split(',')
    print(width, height)

    if (outroDuration > 0):
        # сохранить первый кадр
        os.system(f'ffmpeg -y -i "{videoName}" -ss 00:00:00 -frames:v 1 _outro.jpg')
        # создать концовку видео (статичный первый кадр + зацикленное аудио с залупой)
        os.system(f'ffmpeg -y -loop 1 -i _outro.jpg -stream_loop -1 -i "{args["i"]}" -c:v h264 -vf "fps=30" -t {outroDuration} _outro.mp4')

    # создать начало видео с оригиналом
    os.system(f'ffmpeg -y -i "{videoName}" -t {introDuration} -c copy _intro.mp4')

    # склеить всё
    if (outroDuration > 0):
        os.system(f'ffmpeg -y -i _intro.mp4 -i "{args["i"]}" -i _outro.mp4 -filter_complex '+
        f'"[0]setdar={width}/{height},fps=30[0:v:0];[1]scale={width}:{height},setdar={width}/{height},fps=30[1:v:0];[2]setdar={width}/{height},fps=30[2:v:0]; '+
        '[0:v:0][0:a:0][1:v:0][1:a:0][2:v:0][2:a:0]concat=n=3:v=1:a=1[outv][outa]" '+
        f'-map "[outv]" -map "[outa]" -c:v h264 -c:a aac -b:v 3000k "{outputName}.mp4"')
    else:
        os.system(f'ffmpeg -y -i _intro.mp4 -i "{args["i"]}" -filter_complex '+
        f'"[0]setdar={width}/{height},fps=30[0:v:0];[1]scale={width}:{height},setdar={width}/{height},fps=30[1:v:0]; '+
        '[0:v:0][0:a:0][1:v:0][1:a:0]concat=n=2:v=1:a=1[outv][outa]" '+
        f'-map "[outv]" -map "[outa]" -c:v h264 -c:a aac -b:v 3000k "{outputName}.mp4"')

    # удалить временные файлы
    os.remove('_intro.mp4')
    if (outroDuration > 0):
        os.remove('_outro.jpg')
        os.remove('_outro.mp4')
    if not args['save'] and not args['v']:
        os.remove(videoName)

def main(args):
    isFiles = False
    if args['v']:
        videos = args['v'].split(',')
        isFiles = True
    elif args['l']:
        videos = open(args['l'], 'r').read().strip().split(',')
        videos = [i.strip() for i in videos]
    elif args['id']:
        videos = args['id'].split(',')

    if args['r']:
        videos = [random.choice(videos),]

    if isFiles:
        for path in videos:
            processVideo(args, path)
    else:
        ttApi = TikTokApi()
        for id in videos:
            videoBytes = ttApi.video(id=id).bytes()
            with open(f'{id}.mp4', 'wb') as output:
                output.write(videoBytes)
            processVideo(args, f'{id}.mp4')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Скрипт для вставки видео в другое видео. Если видео не заданы, берется один случайный тикток из списка: '+
        'https://github.com/anoniy/zalupabot/raw/main/video_list.txt')
    parser.add_argument('-s', type=str, metavar='3,8', default='3,8', help='длина начала видео с оригиналом (диапазон). По умолчанию - рандом от 3 до 8 секунд')
    parser.add_argument('-e', type=str, metavar='5,20', default='5,20', help='длина концовки видео с зацикленной картинкой (диапазон). '+
        '0,0 - не создавать концовку. По умолчанию - рандом от 5 до 20 секунд')
    parser.add_argument('-l', type=str, metavar='video_list.txt', help='путь к файлу со списком id видео из тиктока, разделенных запятыми')
    parser.add_argument('-id', type=str, metavar='7061281971581783297', help='id видео из тиктока. Можно задать несколько, разделив запятыми')
    parser.add_argument('-v', type=str, metavar='saved_video.mp4', help='путь к файлу видео. Можно задать несколько, разделив запятыми')
    parser.add_argument('-r', action='store_const', const=True, help='сконвертировать только одно случайное видео из списка')
    parser.add_argument('-i', type=str, metavar='zalupa.webm', default='zalupa.webm', help='путь к файлу видео, которое будет вставлено. По умолчанию - "zalupa.webm"')
    parser.add_argument('-save', action='store_const', const=True, help='сохранять оригиналы загруженных видео')

    args = vars(parser.parse_args())

    if (not not args['l']) + (not not args['id']) + (not not args['v']) > 1:
        raise Exception('Укажите только 1 параметр: -l, -id или -v')

    if not args['l'] and not args['id'] and not args['v']:
        r = requests.get('https://github.com/anoniy/zalupabot/raw/main/video_list.txt').text
        args['id'] = r
        args['r'] = True

    main(args)
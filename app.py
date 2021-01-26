import os
import pathlib
import time
import uuid
import threading
import numpy as np

import ffmpeg
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_file

from setting import mode_dev as mode

is_pi = mode['pi']
is_playing = mode['movie_playing']

pathlib.Path(mode['image_path']).mkdir(exist_ok=True)
pathlib.Path(mode['video_path']).mkdir(exist_ok=True)

if is_pi:
    from waveshare_epd import epd7in5_V2
    
    epd = epd7in5_V2.EPD()
    epd.init()

app = Flask(__name__)


def read_frame_as_jpeg(in_file, frame_num):
    out, err = (
        ffmpeg.input(in_file)
            .filter('select', 'gte(n,{})'.format(frame_num))
            .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
            .run(capture_stdout=True)
    )
    return out


def play_video(video_path):
    global is_playing
    is_playing = True
    total_frames = int(ffmpeg.probe(video_path)['streams'][0]['nb_frames'])
    count = 1
    while count < total_frames:
        out = read_frame_as_jpeg(video_path, count)
        image_array = np.asarray(bytearray(out), dtype='uint8')
        img = Image.fromarray(image_array)
        show(img, 0)
        time_count = 0
        
        while time_count < 60:
            if not is_playing:
                return
            time.sleep(1)
            time_count += 1
        count += 1


def show(img, transpose):
    _transpose = int(transpose)
    if _transpose != 0:
        img = img.transpose(_transpose)
    img.convert(mode='1', dither=Image.FLOYDSTEINBERG)
    if is_pi:
        img = img.resize((epd.width, epd.height))
        epd.display(epd.getbuffer(img))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/image')
def image():
    return render_template('image.html')


@app.route('/api/image', methods=['POST'])
def api_image():
    upload_file = request.files['image']
    transpose = request.form.get('transpose')
    filename = os.path.join(mode['image_path'], str(uuid.uuid4()) + '.jpg')
    upload_file.save(filename)
    
    img = Image.open(upload_file.stream)
    show(img, transpose)
    
    return jsonify({
        'msg': '上传成功'
    })


@app.route('/api/image/show', methods=['POST'])
def api_image_show():
    global is_playing
    is_playing = False
    # 等待1.5秒, 等待上个播放线程结束
    time.sleep(1.5)
    img = Image.open(mode['image_path'] + '/' + request.form.get('name'))
    show(img, request.form.get('transpose'))
    
    return jsonify({
        'msg': '发布成功'
    })


@app.route('/api/video/show', methods=['POST'])
def api_video_show():
    video_path = mode['video_path'] + '/' + request.form.get('name')
    global is_playing
    is_playing = False
    # 等待1.5秒, 等待上个播放线程结束
    time.sleep(1.5)
    t = threading.Thread(target=play_video, args=(video_path, ))
    t.start()
    t.join()
    return jsonify({
        'msg': '发布成功'
    })


@app.route('/api/image/upload', methods=['POST'])
def api_image_upload():
    upload_file = request.files['image']
    filename = os.path.join(mode['image_path'], str(uuid.uuid4()) + '.jpg')
    upload_file.save(filename)
    return jsonify({
        'msg': '上传成功'
    })


@app.route('/api/video/upload', methods=['POST'])
def api_video_upload():
    upload_file = request.files['video']
    filename = os.path.join(mode['video_path'], str(uuid.uuid4()) + '.mp4')
    upload_file.save(filename)
    return jsonify({
        'msg': '上传成功'
    })


def list_images(path):
    files = os.listdir(path)
    return [{'name': file,
             'path': path + '/' + file,
             'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.stat(path + '/' + file).st_mtime)),
             'size': round(os.path.getsize(path + '/' + file) / float(1024 * 1024), 2)} for file in files]


@app.route('/images/list')
def images_list():
    return jsonify(list_images(path=mode['image_path']))


@app.route('/videos/list')
def videos_list():
    return jsonify(list_images(path=mode['video_path']))


@app.route('/videos')
def videos():
    return render_template('videos.html')


@app.route('/images')
def images():
    return render_template('images.html')


@app.route('/del/image', methods=['POST'])
def del_image():
    os.remove(mode['image_path'] + '/' + request.form.get('name'))
    return jsonify({
        'msg': '删除成功'
    })


@app.route('/del/video', methods=['POST'])
def del_video():
    os.remove(mode['video_path'] + '/' + request.form.get('name'))
    return jsonify({
        'msg': '删除成功'
    })


@app.route('/get/image')
def get_image():
    return send_file(mode['image_path'] + '/' + request.args.get('name'))


@app.route('/get/video')
def get_video():
    return send_file(mode['video_path'] + '/' + request.args.get('name'))


if __name__ == '__main__':
    app.run(host='0.0.0.0')

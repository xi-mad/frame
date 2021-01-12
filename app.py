import os
import uuid

from PIL import Image
from flask import Flask, render_template, request, jsonify

from setting import mode_dev as mode

is_pi = mode['pi']

if is_pi:
    from waveshare_epd import epd7in5_V2
    
    epd = epd7in5_V2.EPD()
    epd.init()

app = Flask(__name__)


def show(img, transpose, threshold):
    _transpose = int(transpose)
    _threshold = int(threshold)
    if _transpose != 0:
        img = img.transpose(_transpose)
    img = img.convert('L')
    if _threshold != 0:
        w, h = img.size
        pixels = img.load()
        for x in range(w):
            for y in range(h):
                pix = pixels[x, y]
                pixels[x, y] = 1 if pix > _threshold else 0
    else:
        img.convert(mode='1', dither=Image.FLOYDSTEINBERG)
    
    if is_pi:
        epd.Clear()
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
    threshold = request.form.get('threshold')
    filename = os.path.join(mode['image_path'], str(uuid.uuid4()) + '.jpg')
    upload_file.save(filename)
    
    img = Image.open(upload_file.stream)
    show(img, transpose, threshold)
    
    return jsonify({
        'msg': '上传成功'
    })


@app.route('/video')
def video():
    return render_template('video.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0')

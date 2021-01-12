from flask import Flask, render_template, request, jsonify
from setting import mode_pi as mode
import uuid
from PIL import Image
import os

is_pi = mode['pi']

if is_pi:
    from waveshare_epd import epd7in5_V2
    epd = epd7in5_V2.EPD()
    epd.init()
    epd.Clear()
    
    
app = Flask(__name__)


def show(img, transpose):
    _transpose = int(transpose)
    if _transpose != 0:
        img = img.transpose(_transpose)
    img = img.convert(mode='1', dither=Image.FLOYDSTEINBERG)
    if is_pi:
        img = img.resize((epd.width, epd.height))
        epd.display(epd.getbuffer(img))
        epd.sleep()
    
    
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
        'code': 0
    })


@app.route('/video')
def video():
    return render_template('video.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0')

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/image')
def image():
    return render_template('image.html')


@app.route('/video')
def video():
    return render_template('video.html')


if __name__ == '__main__':
    app.run()

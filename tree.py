import atexit
import colorzero
import concurrent.futures
import flask
import logging
import pitree
import random

app = flask.Flask(__name__)

executor = concurrent.futures.ThreadPoolExecutor(1)

tree = pitree.RGBXmasTree()
tree_state = 0

hue = 0
saturation = 0
brightness = 0

colors = [
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (0.5, 0, 0.5), # purple
    (1, 1, 0), # yellow
    (1, 0.55, 0), # orange
]

def get_next_color():
    global hue
    global saturation
    if saturation <= 50:
        return random.choice(colors)
    else:
        shifted_hue = (hue + random.randint(-10, 10)) % 360 / 360
        shifted_saturation = min(100, saturation + random.randint(-10, 10)) / 100
        c = colorzero.Color.from_hsv(shifted_hue, shifted_saturation, 1.0)
        return c

def twinkle():
    global tree_state
    tree.brightness = 0.1
    while tree_state:
        pixel = random.choice(tree)
        pixel.color = get_next_color()

    tree.off()

def cleanup():
    logging.error('cleaning up')
    tree_state = 0
    tree.off()
    tree.close()

atexit.register(cleanup)

@app.route('/on')
def on():
    global tree_state
    if tree_state == 0:
        tree_state = 1
        #tree.on()
        tree_thread = executor.submit(twinkle)

    return 'on'

@app.route('/off')
def off():
    global tree_state
    tree_state = 0
    return 'off'

@app.route('/status')
def status():
    return f'{tree_state}'

@app.route('/getHue')
def getHue():
    return f'{hue}'

@app.route('/setHue/<int:value>')
def setHue(value):
    global hue
    hue = value
    return f'{hue}'

@app.route('/getSaturation')
def getSaturation():
    return f'{saturation}'

@app.route('/setSaturation/<int:value>')
def setSaturation(value):
    global saturation
    saturation = value
    return f'{saturation}'

@app.route('/getBrightness')
def getBrightness():
    return f'{brightness}'

@app.route('/setBrightness/<int:value>')
def setBrightness(value):
    global brightness
    brightness = value
    tree.brightness = brightness / 100
    return f'{brightness}'

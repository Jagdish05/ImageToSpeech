from flask import Flask, render_template,request, redirect, url_for, Response, flash
import cv2
import imutils
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import requests
import time
from base64 import b64encode
from IPython.display import Image
from pylab import rcParams
rcParams['figure.figsize'] = 10, 20
import sqlite3
# pip install google-cloud-vision
# pip install google-cloud-texttospeech
from google.cloud import vision,translate_v2 as translate
import six
import io
from camera import Camera
import socket
camera = None
# from PIL import
# import pygame
# import pygame.camera
# import PIL.Image as Image
from cv2 import *
from google.cloud import speech
import io
import os
from pydub import AudioSegment



# from SimpleCV import Image, Camera

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"sixth-well-302300-cc8ce0454489.json"


app = Flask(__name__)
# pygame.camera.init()
# pygame.camera.list_cameras() #Camera detected or not
# cam = pygame.camera.Camera("/dev/video0",(640,480))

image_path = "static/captures/"

##============================ Extract text from image==================

# vidcap = cv2.VideoCapture(0)
cam = VideoCapture(0)

def transcript(file,language):
    check_available_lang = {"en":"en-US","es":"es-US","ru":"ru-RU"}
    language = check_available_lang[language]
    print("language",language)
    client = speech.SpeechClient()
    song = AudioSegment.from_mp3(file)
    song.export("file.wav", format="wav")
    with io.open("file.wav", "rb") as audio_file:
        content = audio_file.read()
        # print("content",content)

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=song.frame_rate,
    language_code="en-US",
    enable_word_time_offsets=True,
    enable_automatic_punctuation=True,
    model="Phone_call",
    )
    print(config)
    response = client.recognize(config=config, audio=audio)
    myJson = []
    import json
    for result in response.results:
#        print("result",result)
        alternative = result.alternatives[0]
        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
            myDictObj = { "end":str(end_time.total_seconds()), "start":str(start_time.total_seconds()), "text":word }
            myJson.append(myDictObj)
    return myJson

# @app.route('/')
def convertor_image_to_text(filename):

# Extract text from image
        
        client = vision.ImageAnnotatorClient()
        file_name = os.path.abspath(image_path+filename)
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations
        for text in texts:
            print('\n"{}"'.format(text.description))

            vertices = (['({},{})'.format(vertex.x, vertex.y)
                        for vertex in text.bounding_poly.vertices])

            print('bounds: {}'.format(','.join(vertices)))
#        print(response)
#        print('Texts:',texts[0].description)
        myJson = []
#        print("response",response)
#        for word_info in texts:
#            word = word_info.word
#            start_time = word_info.start_time
#            end_time = word_info.end_time
#            myDictObj = { "end":str(end_time.total_seconds()), "start":str(start_time.total_seconds()), "text":word }
#            myJson.append(myDictObj)
#        print("myJson",myJson)
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        if print(len(texts))==0:
            return redirect(url_for('index'))
        return '\n"{}"'.format(texts[0].description)




 # return '\n"{}"'.format(text.description)
        
#--------------------------------------------------------------------------

def translate_text(target, Listoftext):
    
    """Translates text into the target language.
    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    # print("target",target)
    # print("List",Listoftext)
    import six
    from google.cloud import translate_v2 as translate
    d = dict()
    translate_client = translate.Client()
    for text in Listoftext:
        # print("insideloop",text)
        if isinstance(text, six.binary_type):
            text = text.decode("utf-8")
            # print("afterif",text)

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    
        result = translate_client.translate(text, target_language=target)
        temp = format(result["translatedText"])
        d[text]= temp
    return d

def convertor_text_to_speech(translated_text,language):
    
        
        from google.cloud import texttospeech


    ## Synthesizes speech from the input string of text
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=translated_text)

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        voice = texttospeech.VoiceSelectionParams(
            language_code=language, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        try:
            os.remove("static/output.mp3")
        except OSError:
            pass

        # The response's audio_content is binary.
        with open("static/output.mp3", "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            print('Audio content written to file "output.mp3"')

#         return '\n"{}"'.format(texts[0].description)
        # return "Done"

from werkzeug.utils import secure_filename
from mutagen.mp3 import MP3


UPLOAD_FOLDER = image_path
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
           
import numpy as np
from PIL import Image
import base64
import re
#import StringIO
from io import StringIO

@app.route('/hook', methods=['POST'])
def get_image():
    data = request.values['imageBase64']
    data = re.sub('^data:image/.+;base64,', '', data)
    with open("static/captures/Image.jpg", 'wb+') as image:
        image.write(base64.b64decode(data))
    return 'Ok'


@app.route('/index', methods=('GET', 'POST'))
def index():
    try:
        os.remove("static/output.mp3")
    except OSError:
        pass
    result = "Translated_Text"
    translated_result  = dict()
    trans_list = []
    translated_final_text = []
    myJson = []
    print("request",request)
#    token = request.get_json()['token']
    if request.method == 'POST':
        filename='Image.jpg'
        print("inside post request",request)
        # check if the post request has the file part
          
#             return render_template("translate.html", text=temp)
        # check if the post request has the file part
        # if 'file' not in request.files:
        #     flash('No file part')
        #     return redirect(request.url)
#        file = request.files['file']
#        print(file)
        # if user does not select file, browser also
        # submit an empty part without filename
        # if file.filename == '':
        #     flash('No selected file')
            # return redirect(request.url)

#        if file and allowed_file(file.filename):
#            filename = secure_filename(file.filename)
#            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
          
#        print(filename)
#        print("checking for tanslation button",request.form)
        
        # if request.form['Start_translate'] == 'Translate':
        language = request.form["language"]
        print(language)
#        language = "en-US"
        result = convertor_image_to_text(filename)
        list_of_text = result.splitlines()
#        print(result)
        translated_result = translate_text(language,list_of_text)
        translated_text = translated_result.values()
        translated_final_text = '. '.join(translated_text)
        convertor_text_to_speech(translated_final_text,language)
        check_available_lang = {"en":"en-US","es":"es-US","ru":"ru-RU"}
        if language in check_available_lang:
            myJson = transcript("static/output.mp3",language)
            print("Google API transcribe")
        else:
            print(translated_final_text)
            translated_final_text = translated_final_text.split()
            audio = MP3("static/output.mp3")
            lenAudio = audio.info.length
            lenText = len(translated_final_text)
            time = lenAudio/lenText
            time = round(time,1)
            totalTime = 0
            for text in translated_final_text:
                end_time = totalTime + time
    #            start_time = totalTime
                myDictObj = { "end":str(round(end_time,1)), "start":str(round(totalTime,1)), "text":text }
                myJson.append(myDictObj)
                totalTime = totalTime + time
            print("myJson",myJson)

    return render_template('index.html', content = trans_list, text = translated_result, finalTextList = myJson)
   

##============================Capture image from camera ==================

# camera = None
# def get_camera():
#     global camera
#     if not camera:
#         camera = Camera()
#     return camera


# @app.route('/',methods=('GET', 'POST'))
# def index():
#     return render_template('index.html')

@app.route('/video/')
def video():
    return render_template('video.html')

def gen(camera):
    while True:
        # frame = camera.get_feed()
        # print(frame)
        s, img = cam.read()
        ret, jpeg = cv2.imencode('.jpg', img)
        frame=jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed/')
def video_feed():
    capture()
    return Response(gen(camera),
        mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture/')
def capture():
    s, img = cam.read()
    if s:imwrite("static/captures/Image.jpg",img)
    # cam.release()
    # if request.form['Start_translate'] == 'Translate':
    #     # language = request.form["language"]
        
    #     result = convertor_image_to_text(filename)
    #     list_of_text = result.split('\n')

    #     translated_result = translate_text(language,list_of_text)
    #     translated_text = translated_result.values()
    #     translated_final_text = ''.join(translated_text)
    #     print("translated_final_text",translated_final_text)
    #     convertor_text_to_speech(translated_final_text,language)


    # return render_template('index.html', content1 = translated_result, text = translated_result)
    # index()
    return redirect(url_for('index'))



@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(host="0.0.0.0",port="8080",debug=True)
# host="localhost",port="8000",debug=True

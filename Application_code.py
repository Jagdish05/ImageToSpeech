from flask import Flask, render_template,request
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

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"sixth-well-302300-cc8ce0454489.json"


app = Flask(__name__)

# @app.route('/')
def convertor_image_to_text(filename):

# Extract text from image
        
        client = vision.ImageAnnotatorClient()
        file_name = os.path.abspath("Image/"+filename)
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations
#         print('Texts:',texts[0].description)
        
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        return '\n"{}"'.format(texts[0].description)



        # for text in texts:
        # 	result='\n"{}"'.format(text.description)
        # 	print("My",result)

        #     vertices = (['({},{})'.format(vertex.x, vertex.y)
        #                 for vertex in text.bounding_poly.vertices])

        #     print('bounds: {}'.format(','.join(vertices)))
        #     # return '\n"{}"'.format(text.description)
        
#--------------------------------------------------------------------------

def translate_text(target, Listoftext):
    
    """Translates text into the target language.
    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    print("target",target)
    print("List",Listoftext)
    import six
    from google.cloud import translate_v2 as translate
    d = dict()
    translate_client = translate.Client()
    for text in Listoftext:
        print("insideloop",text)
        if isinstance(text, six.binary_type):
            text = text.decode("utf-8")
            print("afterif",text)

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

        # The response's audio_content is binary.
        with open("output1.mp3", "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            print('Audio content written to file "output.mp3"')

#         return '\n"{}"'.format(texts[0].description)
        # return "Done"

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'Image'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=('GET', 'POST'))

def index():
    result = "Translated_Text"
    translated_result  = dict()
    if request.method == 'POST':
        # check if the post request has the file part
          
#             return render_template("translate.html", text=temp)
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
#         print("checking for tanslation button",request.form)
        
        if request.form['Start_translate'] == 'Translate':
            language = request.form["language"]
            
            result = convertor_image_to_text(filename)
            list_of_text = result.split('\n')
        
            translated_result = translate_text(language,list_of_text)
            translated_text = translated_result.values()
            translated_final_text = ''.join(translated_text)
            print("translated_final_text",translated_final_text)
            convertor_text_to_speech(translated_final_text,language)

    return render_template('index.html', content1 = translated_result, text = translated_result)
    

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'  

    app.run()
# host="localhost",port="8000",debug=True
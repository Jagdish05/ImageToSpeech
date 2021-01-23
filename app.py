#!flask/bin/python
from flask import Flask
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

app = Flask(__name__)

@app.route('/')
def index():

# Extract text from image
	from google.cloud import vision
	import io
	client = vision.ImageAnnotatorClient()
	file_name = os.path.abspath('Image1.jpg')
	with io.open(file_name, 'rb') as image_file:
	    content = image_file.read()

	image = vision.Image(content=content)

	response = client.text_detection(image=image)
	texts = response.text_annotations
	print('Texts:',texts[0].description)

	# for text in texts:
	# 	result='\n"{}"'.format(text.description)
	# 	print("My",result)

	#     vertices = (['({},{})'.format(vertex.x, vertex.y)
	#                 for vertex in text.bounding_poly.vertices])

	#     print('bounds: {}'.format(','.join(vertices)))
	#     # return '\n"{}"'.format(text.description)

	if response.error.message:
	    raise Exception(
	        '{}\nFor more info on error messages, check: '
	        'https://cloud.google.com/apis/design/errors'.format(
	            response.error.message))
	from google.cloud import texttospeech


## Synthesizes speech from the input string of text
	# Instantiates a client
	client = texttospeech.TextToSpeechClient()

	# Set the text input to be synthesized
	synthesis_input = texttospeech.SynthesisInput(text=texts[0].description)

	# Build the voice request, select the language code ("en-US") and the ssml
	# voice gender ("neutral")
	voice = texttospeech.VoiceSelectionParams(
	    language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
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
	with open("output.mp3", "wb") as out:
	    # Write the response to the output file.
	    out.write(response.audio_content)
	    print('Audio content written to file "output.mp3"')

	return "Done"
	# import io
	# import os

	# # Imports the Google Cloud client library
	# from google.cloud import vision

	# # Instantiates a client
	# client = vision.ImageAnnotatorClient()

	# # The name of the image file to annotate
	# file_name = os.path.abspath('Image.jpg')

	# # Loads the image into memory
	# with io.open(file_name, 'rb') as image_file:
	#     content = image_file.read()

	# image = vision.Image(content=content)

	# # Performs label detection on the image file
	# response = client.label_detection(image=image)
	# labels = response.label_annotations

	# # print('Labels:',labels)
	# for label in labels:
	#     print(label.description)

if __name__ == '__main__':
    app.run(debug=True)
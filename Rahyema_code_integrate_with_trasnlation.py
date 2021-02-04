import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\bgurung\Documents\SoftDevwithAI\sixth-well-302300-cc8ce0454489.json"

UPLOAD_FOLDER = 'C:/Users/Raheyma Arshad/Desktop/FlaskApp/static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def translate_text(target, Listoftext):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    import six
    from google.cloud import translate_v2 as translate
    d = dict()
    translate_client = translate.Client()
    for text in Listoftext:
        if isinstance(text, six.binary_type):
            text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    
        result = translate_client.translate(text, target_language=target)
        temp = format(result["translatedText"])
        d[text]= temp
    return d

List =['あなたは良いです','食物','こんにちは']
#
di = dict()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if request.form['Start_translate'] == 'Translate':
            language = request.form["language"]
            temp = translate_text(language,List)   
            return render_template("translate.html", text=temp)
            
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
            return redirect(url_for('uploaded_file',
                                    filename=filename))
        

        
    return '''
    <!doctype html>
    <title>Text To Speech Translator</title>
    <body style="background-color:#87CEEB">
    <h1 style="text-align:center;color:#ffffff;font-size:300%;font-family:verdana"> TRANSLATOR GURU </h1>
    <p style="text-align:center;color:#ffffff;font-size:100%;font-family:verdana"> Image to Text.. Text to Speech</p>
    <form style = "position:relative; left:525px; top:80px" method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload color=white>
      <label for="language">Language:</label>
        <select id="language" name="language">
            <option value="en">English</option>
            <option value="zh">Chinese(Mandarin)</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="ru">Russian</option>
            <option value="hi">Hindi</option>
            <option value="ko">Korean</option>
            <option value="ja">Japanese</option>
        </select>
    <input type="submit" name="Start_translate" value=Translate>
    </form>
    </body>
    '''
from flask import send_from_directory

@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


app.run(debug=True)
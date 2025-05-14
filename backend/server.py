from flask import Flask, request, make_response, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# helper methods


def send_error(message, status_number):
    return {
        "message": message,
        "status": status_number
    }, status_number


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def home():
    return {
        "message": "Hello World",
    }


@app.route('/api', methods=['GET'])
def api():
    return {
        "routes": {
            "/": {
                "method": "GET",
                "description": "Base route"
            },
            "/api": {
                "method": "GET",
                "description": "API Base endpoint"
            },
            "/api/upload": {
                "method": "POST",
                "description": "Upload images to local storage",
                "body": {
                    "type": "form-data",
                    "key": "files",
                    "value": "Array[]"
                }
            },
        }
    }


@app.route('/api/upload', methods=['POST'])
def upload():
    if not request.files:
        return send_error("Files not found in request", 406)
    else:
        print(request.files)
        return {
            ...
        }
# ImmutableMultiDict([('files', <FileStorage: 'sukuna_minimalist_wallpaper__jujutsu_kaisen__by_notdyn_dhemjqz-fullview.jpg' ('image/jpeg')>), ('files', <FileStorage: 'Black Swordsman in the Forest 1920 x 1080p.jpg' ('image/jpeg')>)])


app.run(debug=True)

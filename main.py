from flask import Flask, request, render_template
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from  werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)

#engine = create_engine('postgresql+psycopg2://user_database:user_pass@localhost/dbname')

engine = create_engine(f"postgresql+psycopg2://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}")

@app.route('/')
def index():
    return render_template('Seleção.html')

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in {'csv'}

""" @app.route('/eleitor', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded', 400
        
        file = request.files['file']
        if file.filename == ' ':
            return 'No file selected', 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('/tmp', filename)
            file.upload(file_path)

            file.save(file_path)
"""


if __name__ == '__main__':
    app.run(debug=True)





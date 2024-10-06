from flask import Flask, render_template
import webbrowser
import os

# current folder
current_path = os.path.dirname(__file__)
# parent folder relative
parent_path = os.path.abspath(os.path.join(current_path, '..'))
# web folder
web_path = os.path.join(parent_path, 'web')

app = Flask(__name__,
            template_folder=os.path.join(web_path, 'templates'),
            static_folder=os.path.join(web_path, 'static'))


@app.route('/')
def display_thermodb():
    return render_template('index.html')


def check_lib():
    '''
    Check thermodb on browser
    '''
    webbrowser.open('http://127.0.0.1:5000/')
    app.run(debug=True)

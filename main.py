from flask import Flask
app = Flask(__name__)

@app.route('/')
def main():

    return ''

@app.route('/register', methods=['POST'])
def register():
    return ''


@app.route('/changePassword', methods=['POST'])
def changePassword():
    return ''


@app.route('/login', methods=['GET'])
def login():
    if request.method == 'POST':
        return do_the_login()
    else:
        return show_the_login_form()
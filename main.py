from flask import Flask, request
from hashlib import sha256
import os
app = Flask(__name__)

users_data_file = './usersdata'
ec_bad_username_or_password = 1
ec_general_failure = 4
ec_success = 0

if not os.path.isfile(users_data_file):
    open(users_data_file, 'a').close()

@app.route('/')
def main():
    output = "\nThis web server only provides register, password change and login endpoints.\n" \
             "Please refer to README.md for details\n\n"
    return output, 201

@app.route('/register', methods=['POST'])
def register():
    return request.args.get("lala"), 200


@app.route('/changePassword', methods=['POST'])
def changePassword():
    return ''


@app.route('/login', methods=['GET'])
def login():
    username = request.args.get("username")
    password = request.args.get("pass")

    return output, 200


def get_user_data(username):
    # using open with w+ mode in case it doesn't exist
    with open(users_data_file, 'r') as users_file:
        current_userline = users_file.readline()
        if "{0}::".format(username) in current_userline:
            user_desc = current_userline.split("::")
            return user_desc[0], user_desc[1]


    return user, pass_hash

def update_user_password(username):
    return


def add_user(user, password):
    if ":" in user or ":" in password or not user or not password:
        return ec_bad_username_or_password

    with open(users_data_file, 'a') as users_file:
        current_user = users_file.write("{0}::{1}".format(user, password))
    return ec_success

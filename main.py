from flask import Flask, request
from hashlib import sha256
import os
app = Flask(__name__)

users_data_file = './usersdata'
ec_bad_username_or_password = 1
ec_illigal_username_or_password = 4
ec_user_already_exists = 2
ec_user_does_not_exist = 3
ec_success = 0

if not os.path.isfile(users_data_file):
    open(users_data_file, 'a').close()


def get_error_msg(exit_code):
    if exit_code == ec_success:
        output = "Success!"
    elif exit_code == ec_bad_username_or_password:
        output = "Bad username or password"
    elif exit_code == ec_user_already_exists:
        output = "User already exists"
    else:
        output = "General error"
    return output


@app.route('/')
def main():
    output = "\nThis web server only provides register, password change and login endpoints.\n" \
             "Please refer to README.md for details\n\n"
    return output, 201


@app.route('/register', methods=['POST'])
def register():
    ec = add_user(request.args.get("username"), request.args.get("password"))
    if ec != 0:
        return get_error_msg(ec), 400

    #TODO: Write the user to the other servers

    return "User added successfully!", 200


@app.route('/changePassword', methods=['POST'])
def changePassword():

    #TODO: implement change password
    # also, after successfully adding it to local file
    # add to all other servers

    return ''


# works with url args ?username=<>&pass=<>
@app.route('/login', methods=['GET'])
def login():
    username = request.args.get("username")
    password = request.args.get("pass")

    ec = verify_user(username, password)
    if ec != 0:
        return get_error_msg(ec), 401

    return "Logged in Succesfully!", 200


def get_user_data(username):
    # using open with w+ mode in case it doesn't exist
    with open(users_data_file, 'r') as users_file:
        current_userline = users_file.readline()
        if "{0}::".format(username) in current_userline:
            user_desc = current_userline.split("::")
            return user_desc[0], user_desc[1]
    return "", ""


def update_user_password(username):
    return


def verify_user(username, password):
    u, pass_hash = get_user_data(username)
    if not u or pass_hash != sha256(password):
        return ec_bad_username_or_password
    return ec_success


def add_user(user, password):
    if ":" in user or ":" in password or " " in user or " " in password or not user or not password:
        return ec_illigal_username_or_password

    user, x = get_user_data(user)
    if user:
        return ec_user_already_exists

    with open(users_data_file, 'a') as users_file:
        current_user = users_file.write("{0}::{1}".format(user, sha256(password)))
    return ec_success

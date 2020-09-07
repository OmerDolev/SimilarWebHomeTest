from flask import Flask, request
import requests
import os
import socket
app = Flask(__name__)

# run flask with 'flask run --port=8080'
users_data_file = './usersdata'
listen_port = '8080'
servers_list_file = './servers'
ec_bad_username_or_password = 1
ec_illigal_username_or_password = 4
ec_user_already_exists = 2
ec_user_does_not_exist = 3
ec_success = 0

if not os.path.isfile(users_data_file):
    open(users_data_file, 'a').close()


def get_error_msg(exit_code):
    if exit_code == ec_success:
        output = "Success!\n"
    elif exit_code == ec_bad_username_or_password:
        output = "Bad username or password\n"
    elif exit_code == ec_user_already_exists:
        output = "User already exists\n"
    elif exit_code == ec_user_does_not_exist:
        output = "User does not exist\n"
    elif exit_code == ec_illigal_username_or_password:
        output = "Illigal username or password (must not contain ':' or spaces)\n"
    else:
        output = "General error\n"
    return output


@app.route('/')
def main():
    output = "\nThis web server only provides register, password change and login endpoints.\n" \
             "Please refer to README.md for details\n\n"
    return output, 201

# example query "curl -XPOST -H "auth: hello::world" http://127.0.0.1:8080/register"
@app.route('/register', methods=['POST'])
def register():
    basic_auth_data = request.headers['auth'].split("::")
    ec = add_user(basic_auth_data[0], basic_auth_data[1])
    if ec != 0:
        return get_error_msg(ec), 400

    if os.path.isfile(servers_list_file):
        send_post_to_remaining_servers("register", "auth", basic_auth_data.join("::"))
    #TODO: Write the user to the other servers

    return "User registered successfully!\n", 200

# example query "curl -XPOST -H "auth: hello::wholeworld" http://127.0.0.1:8080/changePassword"
@app.route('/changePassword', methods=['POST'])
def changePassword():
    basic_auth_data = request.headers['auth'].split("::")
    ec = update_user_password(basic_auth_data[0], basic_auth_data[1])

    if ec != 0:
        return get_error_msg(ec), 400

    if os.path.isfile(servers_list_file):
        send_post_to_remaining_servers("changePassword", "auth", basic_auth_data.join("::"))
    #TODO: add write to other servers

    return "Password was updated Succesfully!\n", 200


# exmaple query "http://127.0.0.1:8080/login?username=hello&password=world"
@app.route('/login', methods=['GET'])
def login():
    username = request.args.get("username")
    password = request.args.get("password")

    ec = verify_user(username, password)
    if ec != 0:
        return get_error_msg(ec), 401

    return "Logged in Succesfully!\n", 200


def get_user_data(username):
    # using open with w+ mode in case it doesn't exist
    with open(users_data_file, 'r') as users_file:
        current_userline = users_file.readline()
        while current_userline:
            if "{0}::".format(username) in current_userline:
                user_desc = current_userline.split("::")
                return user_desc[0].rstrip(), user_desc[1].rstrip()
            current_userline = users_file.readline()
    return "", ""


def update_user_password(username, new_password):
    with open(users_data_file, 'r') as users_file:
        users_data = users_file.readlines()
        for idx, line in enumerate(users_data):
            if "{0}::".format(username) in line:
                users_data[idx] = "{0}::{1}\n".format(username, new_password)
                with open(users_data_file, 'w') as users_file:
                    users_file.writelines(users_data)
                return ec_success
    return ec_user_does_not_exist


def verify_user(username, password):
    u, pass_hash = get_user_data(username)
    if u != username or pass_hash != password:
        return ec_bad_username_or_password
    return ec_success


def add_user(user, password):
    if ":" in user or ":" in password or " " in user or " " in password or not user or not password:
        return ec_illigal_username_or_password

    user_from_file, x = get_user_data(user)
    if user_from_file:
        return ec_user_already_exists

    with open(users_data_file, 'a') as users_file:
        users_file.write("{0}::{1}\n".format(user, password))
    return ec_success


def get_target_servers():
    with open(servers_list_file, 'r') as servers_file:
        server_list = servers_file.readlines()
    return server_list.remove(socket.gethostname())

def send_post_to_remaining_servers(location, header_key, header_value):
    for server in get_target_servers():
        url = "http://{0}:{1}/{2}".format(server, listen_port, location)
        response = requests.post(url, headers={header_key: header_value})
        if not response.status_code.startswith("2"):
            print("There has been a problem writing data to {0}, skipping...".format(server))

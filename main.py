from flask import Flask, request
import requests
import time
import sys
app = Flask(__name__)

users = {}
current_port = int(sys.argv[1])
second_server_port = 8085 if current_port == 8080 else 8080

# metrics
metrics_4XX_responses_count = 0
metrics_2XX_responses_count = 0

# exit codes
ec_bad_username_or_password = 1
ec_illigal_username_or_password = 4
ec_user_already_exists = 2
ec_user_does_not_exist = 3
ec_sync_servers_failed = 5
ec_password_already_updated = 6
ec_success = 0


def add_4xx_response():
    global metrics_4XX_responses_count
    metrics_4XX_responses_count += 1


def add_2xx_response():
    global metrics_2XX_responses_count
    metrics_2XX_responses_count += 1


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
    elif exit_code == ec_sync_servers_failed:
        output = "Couldn't sync data to second server\n"
    else:
        output = "General error\n"
    return output


@app.route('/')
def main():
    output = "\nThis web server only provides register, password change and login endpoints.\n" \
             "Please refer to README.md for details\n\n"
    add_2xx_response()
    return output, 200


@app.route('/metrics', methods=['GET'])
def metrics():
    global metrics_2XX_responses_count
    output = "\n"
    output += "# amount of users in database\n{0}\n\n".format(format_metric_line("number_of_users_in_database", len(users)))
    output += "# amount 2XX responses\n{0}\n\n".format(format_metric_line("number_of_2XX_responses", metrics_2XX_responses_count))
    output += "# amount 4XX responses\n{0}\n\n".format(format_metric_line("number_of_4XX_responses", metrics_4XX_responses_count))

    add_2xx_response()
    return output, 200


# example query "curl -XPOST -H "username: hello" -H "password: wholeworld" http://127.0.0.1:8080/register"
@app.route('/register', methods=['POST'])
def register():
    username = request.headers['username']
    password = request.headers['password']
    ec = add_user(username, password)
    if ec == ec_user_already_exists:
        add_2xx_response()
        return "User registered successfully!\n", 200
    elif ec != 0:
        add_4xx_response()
        return get_error_msg(ec), 400

    #TODO: Write the user to the other servers
    sync_servers("register", username, password)
    add_2xx_response()
    return "User registered successfully!\n", 200


# example query "curl -XPOST -H "username: hello" -H "newPassword: wholeworld" http://127.0.0.1:8080/changePassword"
@app.route('/changePassword', methods=['POST'])
def changePassword():
    username = request.headers['username']
    newPassword = request.headers['password']
    ec = update_user_password(username, newPassword)

    if ec == ec_password_already_updated:
        add_2xx_response()
        return "Password was updated Succesfully!\n", 200
    if ec != 0:
        add_4xx_response()
        return get_error_msg(ec), 400

    #TODO: add write to other servers
    sync_servers("changePassword", username, newPassword)

    add_2xx_response()
    return "Password was updated Succesfully!\n", 200


# exmaple query "http://127.0.0.1:8080/login?username=hello&password=world"
@app.route('/login', methods=['GET'])
def login():
    username = request.args.get("username")
    password = request.args.get("password")

    ec = verify_user(username, password)
    if ec != 0:
        add_4xx_response()
        return get_error_msg(ec), 401
    add_2xx_response()
    return "Logged in Succesfully!\n", 200


def get_user_data(username):
    usernames = users.keys()
    if username in usernames:
        return username, users[username]
    return "", ""


def update_user_password(username, new_password):
    existing_users = users.keys()
    if username not in existing_users:
        return ec_user_does_not_exist
    if users[username] == new_password:
        return ec_password_already_updated
    users[username] = new_password
    return ec_success



def verify_user(username, password):
    existing_users = users.keys()
    if username not in existing_users:
        return ec_user_does_not_exist
    if password != users[username]:
        return ec_bad_username_or_password
    return ec_success


def add_user(user, password):
    if " " in user or " " in password or not user or not password:
        return ec_illigal_username_or_password

    for username in users.keys():
        if user == username:
            return ec_user_already_exists
    users[user] = password
    return ec_success


def format_metric_line(metric_name, value):
    return "{0} {1}\n".format(metric_name, value)


def sync_servers(location, header_username, header_password):
    return_code = ec_success
    counter = 5
    url = "http://localhost:{0}/{1}".format(second_server_port, location)
    response = requests.post(url, headers={"username": header_username, "password": header_password})
    if 200 > response.status_code > 300:
        while 200 > response.status_code > 300 and counter < 81:
            time.sleep(counter)
            response = requests.post(url, headers={"username": header_username, "password": header_password})
            counter *= 2

    if counter > 80:
        print("writing update to other server on port {0} failed 5 times".format(second_server_port))
        return_code = ec_sync_servers_failed
    return return_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=current_port)

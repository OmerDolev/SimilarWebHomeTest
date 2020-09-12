from flask import Flask, request, redirect, Response
import json
import requests
import time
import sys
app = Flask(__name__)

targets = {}
targets_file = "targets.json"
with open(targets_file, "r") as f:
    targets = json.load(f)["targets"]

rr_counter = 0
# exit codes
ec_bad_username_or_password = 1
ec_illigal_username_or_password = 4
ec_user_already_exists = 2
ec_user_does_not_exist = 3
ec_sync_servers_failed = 5
ec_password_already_updated = 6
ec_success = 0


def get_error_msg(exit_code):
    if exit_code == ec_success:
        output = "Success!\n"
    elif exit_code == ec_bad_username_or_password:
        output = "Bad username or password\n"
    else:
        output = "General error\n"
    return output


# exmaple query "http://127.0.0.1:8080/login?username=hello&password=world"
@app.route('/<path>', methods=['GET', 'POST'])
def proxy(path):
    global rr_counter
    target = targets[rr_counter]

    # update rr_counter
    rr_counter = (rr_counter + 1) % len(targets)

    if request.method == 'GET':
        if not request.args:
            return "No arguments found!", 400

        request_args = ""
        for idx, arg in enumerate(request.args):
            request_args += "{0}={1}&".format(arg, request.args[arg])
        request_args = request_args[:-1]

        resp = requests.get("http://{0}/{1}?{2}".format(target, path, request_args))
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
    if request.method == 'POST':
        resp = requests.post("{0}{1}".format(target, path), json=request.get_json())
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
    return response


@app.route('/metrics', methods=['GET'])
def metrics():
    return output, 200


def format_metric_line(metric_name, value):
    return "{0} {1}\n".format(metric_name, value)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

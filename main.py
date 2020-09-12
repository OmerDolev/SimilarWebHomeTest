from flask import Flask, request, Response
import multiprocessing
import json
import requests
import time
import socket

app = Flask(__name__)

targets = []
targets_file = "targets.json"
with open(targets_file, "r") as f:
    targets = json.load(f)["targets"]
healthy_targets = []
post_request_max_time_seconds = 11
backoff_interval = 5
rr_counter = 0
health_check_interval_seconds = 1

# metrics
metrics = {
    "metrics_2XX_reponses_count": 0,
    "metrics_4XX_reponses_count": 0,
    "metrics_5XX_reponses_count": 0
}


def add_2XX_response():
    global metrics
    metrics["metrics_2XX_reponses_count"] += 1


def add_4XX_response():
    global metrics
    metrics["metrics_4XX_reponses_count"] += 1


def add_5XX_response():
    global metrics
    metrics["metrics_5XX_reponses_count"] += 1


def debug(msg):
    print("DEBUG!!!!!!!!!!!!\n{0}\n\n".format(msg))


def check_targets_health():
    global targets
    global healthy_targets
    while True:
        for target in targets:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((target.split(":")[0], int(target.split(":")[1])))
                if result == 0 and target not in healthy_targets:
                    healthy_targets.append(target)
                elif result != 0 and target in healthy_targets:
                    healthy_targets.remove(target)
                sock.close()
            except Exception as e:
                print(e)
        debug(healthy_targets)
        time.sleep(health_check_interval_seconds)


health_process = multiprocessing.Process(target=check_targets_health)
health_process.start()


# exmaple query "http://127.0.0.1:8080/login?username=hello&password=world"
@app.route('/<path>', methods=['GET', 'POST'])
def proxy(path):
    global targets
    global rr_counter
    global healthy_targets

    if request.method == 'GET':

        debug(healthy_targets)

        if not request.args:
            add_4XX_response()
            return "No arguments found!", 400
        if len(targets) < 1:
            add_5XX_response()
            return "No healthy targets found!", 500

        # update rr_counter
        rr_counter = (rr_counter + 1) % len(healthy_targets)
        target = healthy_targets[rr_counter]
        # format get request args
        request_args = ""
        for idx, arg in enumerate(request.args):
            request_args += "{0}={1}&".format(arg, request.args[arg])
        request_args = request_args[:-1]

        # execute request
        resp = requests.get("http://{0}/{1}?{2}".format(target, path, request_args))
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)

        if 200 <= resp.status_code < 300:
            add_2XX_response()
        elif 400 <= resp.status_code < 500:
            add_4XX_response()
        elif 500 <= resp.status_code:
            add_5XX_response()

    if request.method == 'POST':

        response = ""
        sessions = {}
        manager = multiprocessing.Manager()
        return_value = manager.list()
        for t in healthy_targets:
            p = multiprocessing.Process(target=send_post_to_target,
                                        args=(t, path, dict([keyval for keyval in request.headers]), return_value))
            sessions[t] = p
            p.start()

        # for s in sessions:
        #     sessions[s].join()
        while not return_value:
            time.sleep(0.1)
        for r in return_value:
            if 200 <= r.status_code < 300:
                response = "{}\n".format(r.status), r.status_code
            else:
                response = "500 Couldn't complete request\n", 500

            if 200 <= r.status_code < 300:
                add_2XX_response()
            elif 400 <= r.status_code < 500:
                add_4XX_response()
            elif 500 <= r.status_code:
                add_5XX_response()

    return response


def send_post_to_target(target, path, headers, shared_value):
    global backoff_interval
    global post_request_max_time_seconds
    global healthy_targets

    current_backoff_interval = backoff_interval
    url = "http://{0}/{1}".format(target, path)

    # debug("in send post fund {}".format(healthy_targets))
    # if target not in healthy_targets:
    #     response = Response("Unhealthy target", 500)
    #     try:
    #         shared_value.append(response)
    #     except Exception as e:
    #         print("Couldn't add request to shared data, {}".format(e))
    #     return response

    try:
        # first try
        resp = requests.post(url, headers=headers)

        # retry backoff
        while resp.status_code != 201 and current_backoff_interval < post_request_max_time_seconds:
            time.sleep(current_backoff_interval)
            resp = requests.post(url, headers=headers)
            current_backoff_interval *= 2
    except Exception as e:
        print(e)
        if shared_value:
            shared_value.append(Response("Server Error", 500))

    # after timeout passed or request is completed
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)

    try:
        shared_value.append(response)
    except Exception as e:
        print("Couldn't add request to shared data, {}".format(e))
    return response


def extract_return_code(resp):
    return resp.split("[")[1].split("]")[0]


@app.route('/metrics', methods=['GET'])
def print_metrics():
    global metrics
    output = "## Simple Load Balancer Metrics ##\n\n"
    for metric in metrics:
        output += format_metric_line(metric, metrics[metric])

    add_2XX_response()
    return output, 200


def format_metric_line(metric_name, value):
    return "{0} {1}\n\n".format(metric_name, value)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

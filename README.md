# SimilarWeb Home Test

Simple Python Load Balancer

## Installation

1. Ensure you have python 3 installed

2. Clone this repo to your workstation.

3. Run pip install -r requirements.txt

4. Configure targets.json file with <hostname>:<port> of targets

5. See *Usage* below for further info.

## Usage

**NOTE:**
Load Balancer implements */metrics* endpoint.
Otherwise queries are sent to the upstream targets listed in targets.json
according to the task specifications.


There are 2 shell scripts (server_run_8080, server_run_8085).
Those are simple http servers one on port 8080, the other on 8085.
(they are configured to match the targets in the json file)

The simple web servers define 3 endpoints:

### */register*

Only allowed method is POST.

LB Example Query: curl -XPOST -H "user: hello" http://127.0.0.1:80/register 

### */changePassword*

Only allowed method is POST.

For success "user" header must have value: "hello"

To get Bad request change value from "hello" to something else.

LB Example Query: curl -XPOST -H "user: hello" http://127.0.0.1:80/changePassword 


### */login*

Only allowed method is GET.

For success "user" URL arg must have value: "hello"

To get Unauthorized change value from "hello" to something else.

LB Example Query: curl http://127.0.0.1:80/login?user=hello 


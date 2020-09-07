# SimilarWeb Home Test

Simple 2 server web authn service

####Installation

1. Clone this repo to your workstation.

2. There are 2 scripts, one for each server.
Run both scripts from different terminals and see
that the flask servers started successfully.

3. See *Usage* below for further info.

####Usage

**NOTE:** In current configuration web servers must run on the same machine

This simple web server defines 4 endpoints:

#####*/register*

Only allowed method is POST.

Needs to have "username" header and "password" header

Example Query: curl -XPOST -H "username: hello" -H "password: world" http://127.0.0.1:8080/register 

#####*/changePassword*

Only allowed method is POST.

Needs to have "username" header and "password" header

Example Query: curl -XPOST -H "username: hello" -H "password: world" http://127.0.0.1:8080/changePassword 


#####*/login*

Only allowed method is GET.

Needs to have "username" "password" URL arguments

Example Query: curl "http://127.0.0.1:8080/login?username=hello&password=world" 

#####*/metrics*

Only allowed method is GET.

Example Query: curl "http://127.0.0.1:8080/metrics" 


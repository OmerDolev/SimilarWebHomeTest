from flask import Flask, request
import sys
app = Flask(__name__)


# example query "curl -XPOST -H "username: hello" -H "password: wholeworld" http://127.0.0.1:8080/register"
@app.route('/register', methods=['POST'])
def register():
    return "User registered successfully!\n", 201


# exmaple successful query "curl -XPOST -H "username: hello" http://127.0.0.1:8080/changePassword"
# exmaple wrong query "curl -XPOST -H "username: world" http://127.0.0.1:8080/changePassword"
@app.route('/changePassword', methods=['POST'])
def changePassword():
    username = request.headers['user']
    if username == "hello":
        return "Password was updated Succesfully!\n", 201
    else:
        return "Password update failed!\n", 400


# exmaple successful login query "http://127.0.0.1:8080/login?username=hello"
# exmaple wrong login query "http://127.0.0.1:8080/login?username=world"

@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('user')
    if username == "hello":
        return "Logged in Succesfully!\n", 200
    else:
        return "Login Failed!\n", 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=sys.argv[1])

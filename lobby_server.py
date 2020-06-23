import os

from flask import Flask
 
app = Flask(__name__)
 
 
def get_build_script():
    return "docker build -t flask-sample:lastest ."

def get_run_script(port):
    return "docker run -d -p {}:5000 flask-sample".format(port)

@app.route("/one_player")
def setup_oneplayer():
    port = 5001

    os.system(get_build_script())
    os.system(get_run_script(port))

    return "localhost:{}".format(port)

 
if __name__ == '__main__':
    app.run(port=6969)
from flask import Flask
import time

app = Flask(__name__)


@app.route("/")
def index():
    return 'Regnio Raspberry Pi 4 cluster'


@app.route("test")
def test():
    start_time = time.time()
    a = [[0]] * 100000000
    end_time = time.time()

    return f'{end_time - start_time} {a}'


if __name__ == "__main__":
    port = 3000
    app.run(host="0.0.0.0", port=port)

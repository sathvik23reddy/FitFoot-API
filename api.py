from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def image_query():
    input_query = request.get_json()
    b64 = input_query['Image']
    return 'Your base64 Image is : ' + b64


if __name__ == "__main__":
    app.run(host='0.0.0.0')

from flask import Flask, Response, jsonify
from datetime import datetime
app = Flask(__name__)

@app.route('/')
def homepage():
    return """
    <h1>Hello heroku</h1>
    <p>It is currently {time}.</p>
    """.format(time=datetime.now())

@app.route('/slack/command/meal', methods=['POST'])
def meal():
    msg = {'text': '너에게 알려줄 급식따윈 없다'}
    return jsonify(msg)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

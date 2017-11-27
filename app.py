from flask import Flask, Response
from datetime import datetime
import json
app = Flask(__name__)

@app.route('/')
def homepage():
    return """
    <h1>Hello heroku</h1>
    <p>It is currently {time}.</p>
    """.format(time=datetime.now())

@app.route('/slack/command/meal')
def meal():
    msg = {'text': '너에게 알려줄 급식따윈 없다'}
    return Response(json.dumps(msg), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

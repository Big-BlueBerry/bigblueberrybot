from flask import Flask, Response, jsonify
from datetime import datetime
import urllib.request
import json
app = Flask(__name__)

@app.route('/')
def homepage():
    return """
    <h1>Hello heroku</h1>
    <p>It is currently {time}.</p>
    """.format(time=datetime.now())

@app.route('/slack/command/meal', methods=['POST'])
def meal():
    date = datetime.now()
    url = f'http://dsm2015.cafe24.com:3000/meal/{date.strftime("%Y-%m-%d")}'
    try:
        bs = urllib.request.urlopen(url).read()
        res = json.loads(bs)
    except:
        msg = {
            'response_type': 'in_channel',
            'text': '한심한 DMS 급식 또 터졌음 :thinking:\n왜냐하면 내가 잘못됐을리는 없거든'
        }
        return Response(json.dumps(msg), mimetype='application/json')

    msg = {
        'response_type': 'in_channel',
        "attachments": [
            {
                "fallback": "",
                "pretext": "오늘자 급식:rice:",
                "fields": [
                    {
                        "title": "아침",
                        "value": '\n'.join(res['breakfast']),
                        "short": True
                    },
                    {
                        "title": "점심",
                        "value": '\n'.join(res['lunch']),
                        "short": True
                    },
                    {
                        "title": "저녁",
                        "value": '\n'.join(res['dinner']),
                        "short": True
                    }
                    ],
                "color": "#7CD197"
            }
        ]
    }
    return Response(json.dumps(msg), mimetype='application/json')

if __name__ == '__main__':
    # app.run(debug=True, use_reloader=True)
    meal()

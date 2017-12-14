from flask import Flask, request, render_template
import requests
import json

app = Flask(__name__)


def prepare_data():
    try:
        with open("flask_data.json", 'r') as f:
            cached_data = f.read()
            data = json.loads(cached_data)
            for i in data['data']:
                for j in i['loot']:
                    j['stats'].strip('\\n').replace('\\n', '')
                    print(j['stats'])
            return data

    except:
        print("Please run 'python SI507F17_finalproject.py search (zone_name)' first!")


@app.route('/')
def index():
    render_dict = prepare_data()

    return render_template(
        'index.html',
        items_to_embed=render_dict['data'],
        search_term=render_dict['zone'])

if __name__ == '__main__':
    # auto reloads (mostly) new code and shows exception traceback in the
    # browser
    app.run(use_reloader=True, debug=True)

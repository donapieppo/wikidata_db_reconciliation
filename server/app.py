from flask import Flask, request, jsonify, render_template
from wikidata_local_reconciliator import WikidataLocalReconciliator
import json

app = Flask(__name__)

@app.route('/api/v1/s', methods=['GET'])
def api_search():
    # Get query parameters from the URL
    name = request.args.get('name')
    year = request.args.get('year')
    year = int(year) if len(year) > 0 else 2024

    reconciliator = WikidataLocalReconciliator(db_file='../../../tmp/wikidata.db')
    result = reconciliator.ask(name, year, 'film_director')

    response = app.response_class(
      response=json.dumps(result, default=tuple), 
      status=200, 
      mimetype='application/json')
    return response

@app.route('/search', methods=['POST'])
def search(): 
    name = request.form['name']
    year = request.form['year']
    year = int(year) if len(year) > 0 else 2024

    reconciliator = WikidataLocalReconciliator(db_file='../../../tmp/wikidata.db')
    result = reconciliator.ask(name, year, 'film_director')

    if result:
        return render_template('search.html', name=name, result=result)
    else:
        return "No result"


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

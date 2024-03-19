from flask import Flask, request, jsonify, render_template
from wikidata_local_reconciliator import WikidataLocalReconciliator
from wikidata_occupation import WikidataOccupation
import json

app = Flask(__name__)

@app.route('/api/v1/s', methods=['GET'])
def api_search():
    # Get query parameters from the URL
    name = request.args.get('name')
    year = request.args.get('year')
    occupations = request.args.get('occupations')
    year = int(year) if (year and len(year) > 0) else 2024

    reconciliator = WikidataLocalReconciliator(db_file='../../../tmp/wikidata.db')
    result = reconciliator.ask(name, year, occupations)

    response = app.response_class(
      response=json.dumps(result, default=tuple), 
      status=200, 
      mimetype='application/json')
    return response

@app.route('/search', methods=['POST'])
def search(): 
    name = request.form['name']
    year = request.form['year']
    occupations = ", ".join(request.form.getlist('occupations'))
    year = int(year) if (year and len(year) > 0) else 2024

    reconciliator = WikidataLocalReconciliator(db_file='../../../tmp/wikidata.db')
    result = reconciliator.ask(name, year, occupations)

    if result:
        return render_template('search.html', name=name, result=result)
    else:
        return "No result"


@app.route('/', methods=['GET'])
def index():
    wd_occupation = WikidataOccupation()
    return render_template('index.html', occupations = wd_occupation.occupations_by_name)

if __name__ == '__main__':
    app.run(debug=True)

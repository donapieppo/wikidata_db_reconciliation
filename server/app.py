from wikidata_local_reconciliator import WikidataLocalReconciliator
from flask import Flask, request, jsonify

reconciliator = WikidataLocalReconciliator(db_file='../tmp/wikidata.db')

app = Flask(__name__)

@app.route('/api/v1/s', methods=['GET'])
def search():
    # Get query parameters from the URL
    name = request.args.get('name')
    year = request.args.get('year')

    # Perform your search logic here (replace this with your actual implementation)
    # For example, just returning the parameters as JSON for demonstration purposes
    result = {'name': name, 'year': year}
    result = reconciliator.ask('martin scorsese', 2000, 'film_director')

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

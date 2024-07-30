from lib2to3.pgen2.tokenize import generate_tokens
from flask.templating import render_template
from joblib import load
from flask import Flask, redirect, url_for, request
import time
import json
import pyarrow.parquet as pq

def create_app():
    model = load('./data/model.pkl')
    template = """
                <div class="position-relative overflow-hidden" style="height: 300px;">
                    <img class="img-fluid h-100" src="img/news-700x435-1.jpg" style="object-fit: cover;">
                    <div class="overlay">
                        <div class="mb-2">
                            <a class="badge badge-primary text-uppercase font-weight-semi-bold p-2 mr-2"
                                href=""></a>
                            <a class="text-white" href=""><small></small></a>
                        </div>
                        <a class="h6 m-0 text-white text-uppercase font-weight-semi-bold" href=""></a>
                    </div>
                </div>
                    """

    app = Flask(__name__,template_folder='html')
    
    @app.route('/api/response/<txt>')
    def success(txt):
        result = model.predProb(txt)
        data = pq.read_table('./data/featurized_data.parquet').to_pandas()
        result = model.sort_dict(result)
        print(result)
        # Qualified Keys [5 Categories Per Request]
        i = 0
        qualified_cats = []
        for k,v in result.items():
            if i != 5:
                qualified_cats.append(k)
                i += 1
            else:
                break
        print(qualified_cats)
        filter_content_recommendations = data[data['intent'].isin(qualified_cats)].reset_index(drop=True)
        gen_template = ''
        for intent in qualified_cats:
            for j in range(0,6):
                broker_template = template
                broker = filter_content_recommendations[filter_content_recommendations['intent'] == intent].reset_index(drop=True)
                img = broker['card_img'][j]
                gen_template = gen_template + broker_template.replace("img/news-700x435-1.jpg",img)
        return gen_template

    @app.route('/api/',methods = ['POST', 'GET'])
    def search():
        if request.method == 'POST':
            text = request.form["nm"]
            return redirect(url_for('success',txt = text))
        else:
            text = request.args.get('nm')
            return redirect(url_for('success',txt = text))

    @app.route('/')
    def default():
        return render_template('index.html')


    
    return app

if __name__ == '__main__':
    app_ = create_app()
    app_.debug = True
    app_.run(host='0.0.0.0',port=5000,debug=True)


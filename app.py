# imports
from flask import Flask, render_template, request
import search
from search import final_processing
# create app
app = Flask(__name__, static_url_path='')


@app.route('/',methods=['GET','POST'])
def form():
    if request.method == 'POST':
        sk=request.form['my_form']
        l, t = final_processing(sk)
              
        return render_template('form.html',result=l, search_key = sk, timedVar=t, getRes = 1)
    if request.method == 'GET':
        return render_template('form.html')

if __name__ == '__main__':
     search.get_urls_from_ids()
     app.run(debug=False)   

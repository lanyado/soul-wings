from flask import Flask  
from flask import render_template
import sys
import os 
from flask import request
import json
import codecs
results =  [
  {
    "fileName":"עדות ויסק",
    "name": "משה ויסקופ",
    "lang": "עברית",
    "country": "אוסטריה",
    "year": "1945",
    "tags": "הצלב האדום",
    "contents": [{"timing":"13:52", "text":"צלב האדום, או , או תנועת הצלב האדום , או תנועת הצלב האדום והסהר האדום הבינלאומי הוא קבוצה של אר והסהר האדום הבינלאומי הוא קבוצה של אר תנועת הצלב האדום והסהר האדום הבינלאומי הוא קבוצה של ארגונים העוסקים "},
    {"timing":"13:52", "text":"צלב האדום, או , או תנועת הצלב האדום , או תנועת הצלב האדום והסהר האדום הבינלאומי הוא קבוצה של אר והסהר האדום הבינלאומי הוא קבוצה של אר תנועת הצלב האדום והסהר האדום הבינלאומי הוא קבוצה של ארגונים העוסקים "}] ,
    "url": "עכגעכגעכגעכגעכגעכגעכגעכגעכגעכגעכגעכג"
   },
   {
    "fileName":"רבקה-עדות 1",
    "name": "רבקה כהן",
    "lang": "עברית",
    "country": "לא",
    "year": "1943",
    "tags": "בודפסט",
    "contents": [{"timing":"13:52", "text":"צלב האדום, או , או תנועת הצלב האדום , או תנועת הצלב האדום והסהר האדום הבינלאומי הוא קבוצה של אר והסהר האדום הבינלאומי הוא קבוצה של אר תנועת הצלב האדום והסהר האדום הבינלאומי הוא קבוצה של ארגונים העוסקים "}] ,
    "url": "עכגעכגעכגעכגעכגעכגעכגעכגעכגעכגעכגעכג"
   },
   {
    "fileName":"יעקב-עדות 5",
    "name": "יעקב גרין",
    "lang": "1940",
    "country": "פולין",
    "year": "כן",
    "tags": "בודפשט",
    "contents": [{"timing":"13:52", "text":"צלב האדום, או , או תנועת הצלב האדום , או תנועת הצלב האדום והסהר האדום הבינלאומי הוא קבוצה של אר והסהר האדום הבינלאומי הוא קבוצה של אר תנועת הצלב האדום והסהר האדום הבינלאומי הוא קבוצה של ארגונים העוסקים "}] , 
    "url": "fdshfds"
   }
]
current_dir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__, template_folder=os.path.join(current_dir, 'html'))

@app.route("/")
def hello():  
	return render_template('index.html',  results=results)


@app.route('/search', methods = ['POST'])
def get_post_javascript_data6():
	text = request.form['javascript_data']
	return ( results)


# run the application
if __name__ == "__main__":  
	app.run(debug=True)
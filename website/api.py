from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
import numpy as np
import joblib
from sklearn.feature_extraction.text import CountVectorizer
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import requests
from .mysql_models import get_comments


api = Blueprint('api', __name__)
pipe = joblib.load('sentiment_analysis_pipeline.joblib')


def remove_tags(raw_text):
    cleaned_text = re.sub(re.compile('<.*?>'), '', raw_text)
    return cleaned_text


def remove_stopwords(text):
    english_stopwords = set(stopwords.words('english'))
    words = word_tokenize(text)
    filtered_words = [word for word in words if word.lower() not in english_stopwords]
    return ' '.join(filtered_words)


@api.route('/sentiment_analysis', methods=['GET', 'POST'])
def sentiment_analysis():
    try:
        comment = request.args.get('comment')
        comment = remove_tags(comment)
        comment = remove_stopwords(comment)
        comment = np.array([comment])
        response = {}
        response['negative'] = pipe.predict_proba(comment)[0][0]
        response['neutral'] = pipe.predict_proba(comment)[0][1]
        response['positive'] = pipe.predict_proba(comment)[0][2]
    except:
        return render_template("error.html")
    return jsonify(response)


@api.route("/analyze_comment", methods=['GET', 'POST'])
def analyze_comment():
    if request.method == 'POST':
        comment = request.form.get("comment")
        url = "http://127.0.0.1:9000/api/sentiment_analysis?comment='" + comment + "'"
        try:
            response = requests.get(url).json()
            return jsonify(response)
        except:
            return render_template("error.html")
    return render_template("test.html")


def get_sentiment_scores(comment):
    comment = remove_tags(comment)
    comment = remove_stopwords(comment)
    comment = np.array([comment])
    response = {}
    response['negative'] = pipe.predict_proba(comment)[0][0]
    response['neutral'] = pipe.predict_proba(comment)[0][1]
    response['positive'] = pipe.predict_proba(comment)[0][2]
    return response

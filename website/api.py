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
hate_speech_pipe = joblib.load("hate_speech_model.joblib")


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
    comment = request.args.get('comment')
    comment = remove_tags(comment)
    comment = remove_stopwords(comment)
    comment = np.array([comment])

    response = {}
    response['negative'] = pipe.predict_proba(comment)[0][0]
    response['neutral'] = pipe.predict_proba(comment)[0][1]
    response['positive'] = pipe.predict_proba(comment)[0][2]
    
    return jsonify(response)


@api.route('/emotional_analysis', methods=['GET', 'POST'])
def emotional_analysis():
    comment = request.args.get('comment')
    comment = remove_tags(comment)
    comment = remove_stopwords(comment)
    comment = np.array([comment])
    
    response = {}
    response['hate speech'] = hate_speech_pipe.predict_proba(comment)[0][0]
    response['offensive language'] = hate_speech_pipe.predict_proba(comment)[0][1]
    response['neutral'] = hate_speech_pipe.predict_proba(comment)[0][2]
    
    return response


@api.route("/analyze_comment", methods=['GET', 'POST'])
def analyze_comment():
    if request.method == 'POST':
        comment = request.form.get("comment")
        url = "http://127.0.0.1:9000/api/sentiment_analysis?comment='" + comment + "'"
        response = requests.get(url).json()
        return jsonify(response)
    return render_template("test.html")


@api.route("/analyze_sentiment", methods=['GET', 'POST'])
def analyze_comment():
    if request.method == 'POST':
        comment = request.form.get("comment")
        url = "http://127.0.0.1:9000/api/emotional_analysis?comment='" + comment + "'"
        response = requests.get(url).json()
        return jsonify(response)
    return render_template("test.html")


def get_overall_emotion(video_id):
    comments = get_comments(current_user.id, video_id)
    hate_speech = 0
    offensive_comment = 0
    neutral = 0
    for comment in comments:
        emotions = emotional_analysis(comment)
        hate_speech += emotions['hate speech']
        offensive_comment += emotions['offensive language']
        neutral += emotions['neutral']
    return {
        "hate speech": hate_speech,
        "offensive language": offensive_comment,
        "neutral": neutral
    }
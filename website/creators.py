from flask import Blueprint, render_template, request, redirect, url_for
from .mysql_models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import re
from .mysql_models import get_comments
import joblib
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import numpy as np


creators = Blueprint('creators', __name__)
pipe = joblib.load('hate_speech_model.joblib')


def remove_tags(raw_text):
    cleaned_text = re.sub(re.compile('<.*?>'), '', raw_text)
    return cleaned_text


def remove_stopwords(text):
    english_stopwords = set(stopwords.words('english'))
    words = word_tokenize(text)
    filtered_words = [word for word in words if word.lower() not in english_stopwords]
    return ' '.join(filtered_words)


def emotional_analysis(comment):
    # comment = remove_tags(comment)
    # comment = remove_stopwords(comment)
    comment = np.array([comment])
    
    response = {}
    response['hate speech'] = pipe.predict_proba(comment)[0][0]
    response['offensive language'] = pipe.predict_proba(comment)[0][1]
    response['neutral'] = pipe.predict_proba(comment)[0][2]
    
    return response


def get_overall_emotion(video_id):
    comments = get_comments(current_user.id, video_id)
    comments = [comment['comment'] for comment in comments]
    if len(comments) == 0:
        emotion = {
            "hate_speech": 0,
            "offensive_language": 0,
            "neutral": 100
        }
        return emotion
    hate_speech = 0
    offensive_comment = 0
    neutral = 0
    for comment in comments:
        emotions = emotional_analysis(comment)
        hate_speech += emotions['hate speech']
        offensive_comment += emotions['offensive language']
        neutral += emotions['neutral']

    total = hate_speech + offensive_comment + neutral
    hate_speech /= total
    offensive_comment /= total
    neutral /= total

    emotion = {
        "hate_speech": hate_speech * 100,
        "offensive_language": offensive_comment * 100,
        "neutral": neutral * 100
    }

    return emotion


@creators.route("/analytics", methods=['GET', 'POST'])
def show_analytics():
    if request.method == 'POST':
        try:
            url = request.form.get("url")
            pattern = re.compile(r'(?<=v=)[\w-]+|(?<=youtu.be\/)[\w-]+')
            video_id = pattern.findall(url)[0] 
            emotion = get_overall_emotion(video_id)
            return render_template("analysis.html", emotion=emotion)
        except:
            return render_template("error.html")
    return render_template("get.html")
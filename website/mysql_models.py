from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150))
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))


class SearchQuery(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    query = db.Column(db.String(150))
    video_clicked = db.Column(db.String(150))
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())


class NextVideo(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    current_video_id = db.Column(db.String(150))
    next_video_id = db.Column(db.String(150))
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())


class Like(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    video_id = db.Column(db.String(150))
    # like_status = db.Column(db.String(150))
    like_status = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())


class Subscribe(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    channel_id = db.Column(db.String(150))
    subscribe_status = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())


def get_click_through_data(user_id, video_id):
    next_video_data = NextVideo.query.filter_by(user_id=user_id, current_video_id=video_id).all()
    
    data = []
    for video in next_video_data:
        data.append({
            'user_id': video.user_id,
            'current_video_id': video.current_video_id,
            'next_video_id': video.next_video_id,
        })
    
    return data


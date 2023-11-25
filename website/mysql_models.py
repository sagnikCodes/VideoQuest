from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import desc


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


class Comment(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    video_id = db.Column(db.String(150))
    comment = db.Column(db.String(150))
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())


def get_click_through_data():
    next_video_data = NextVideo.query.all()

    from mongodb_models import MongoDBHandler
    mongo_handler = MongoDBHandler()
    unique_video_ids = set()
    for video in next_video_data:
        unique_video_ids.add(video.next_video_id)

    videos_data = {}
    for video_id in unique_video_ids:
        videos_data[video_id] = {}
        videos_data[video_id]['likes'] = mongo_handler.get_data(video_id)['likeCount']
        videos_data[video_id]['dislikes'] = mongo_handler.get_data(video_id)['dislikeCount']
        videos_data[video_id]['views'] = mongo_handler.get_data(video_id)['viewCount']

    data = []
    for video in next_video_data:
        data.append({
            'user_id': video.user_id,
            'current_video_id': video.current_video_id,
            'current_video_likes': videos_data[video.current_video_id]['likes'],
            'current_video_dislikes': videos_data[video.current_video_id]['dislikes'],
            'current_video_views': videos_data[video.current_video_id]['views'],
            'next_video_id': video.next_video_id,
        })
    
    return data


def get_comments(current_user_id, video_id):
    current_user_comment = (
        Comment.query
        .filter_by(video_id=video_id, user_id=current_user_id)
        .order_by(desc(Comment.timestamp))
        .first()
    )

    other_users_comments = (
        Comment.query
        .filter_by(video_id=video_id)
        .filter(Comment.user_id != current_user_id)
        .order_by(desc(Comment.timestamp))
        .distinct(Comment.user_id)
        .all()
    )

    other_users = set()
    other_comments = []
    for comment in other_users_comments:
        other_user = comment.user_id
        if other_user not in other_users:
            other_users.add(other_user)
            other_comments.append(comment)

    comments_data = [
        {
            'username': User.query.get(current_user_id).username,
            'comment': current_user_comment.comment,
            # 'timestamp': current_user_comment.timestamp.isoformat()
        }
    ] if current_user_comment else []

    comments_data += [
        {
            'username': User.query.get(comment.user_id).username,
            'comment': comment.comment,
            # 'timestamp': comment.timestamp.isoformat()
        }
        for comment in other_comments
    ]

    return comments_data
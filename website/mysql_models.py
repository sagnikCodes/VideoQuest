from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import desc
from .mongodb_models import MongoDBHandler
from .neo4j_models import Neo4jHandler


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
    negative_sentiment_score = db.Column(db.Float)
    neutral_sentiment_score = db.Column(db.Float)
    positive_sentiment_score = db.Column(db.Float)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())


class History(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    video_id = db.Column(db.String(150))
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())


def get_click_through_data():
    next_video_data = NextVideo.query.all()
    neo4j_handler = Neo4jHandler()
    mongodb_handler = MongoDBHandler()
    unique_video_ids = set()
    for video in next_video_data:
        unique_video_ids.add(video.next_video_id)

    # videos_data = {}
    # for video_id in unique_video_ids:
    #     videos_data[video_id] = {}
    #     videos_data[video_id]['likes'] = neo4j_handler.get_video_property(video_id, 'likes')
    #     videos_data[video_id]['dislikes'] = neo4j_handler.get_video_property(video_id, 'dislikes')
    #     videos_data[video_id]['views'] = neo4j_handler.get_video_property(video_id, 'views')

    data = []
    for video in next_video_data:
        data.append({
            'user_id': video.user_id,
            'current_video_id': video.current_video_id,
            # 'current_video_likes': neo4j_handler.get_video_property(video.current_video_id, 'likes'),
            # 'current_video_dislikes': neo4j_handler.get_video_property(video.current_video_id, 'dislikes'),
            # 'current_video_views': neo4j_handler.get_video_property(video.current_video_id, 'views'),
            'current_video_likes': mongodb_handler.get_data(video.current_video_id)['likeCount'],
            'current_video_dislikes': mongodb_handler.get_data(video.current_video_id)['dislikeCount'],
            'current_video_views': mongodb_handler.get_data(video.current_video_id)['viewCount'],
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
            'negative_sentiment_score': current_user_comment.negative_sentiment_score,
            'neutral_sentiment_score': current_user_comment.neutral_sentiment_score,
            'positive_sentiment_score': current_user_comment.positive_sentiment_score,
        }
    ] if current_user_comment else []

    comments_data += [
        {
            'username': User.query.get(comment.user_id).username,
            'comment': comment.comment,
            # 'timestamp': comment.timestamp.isoformat()
            'negative_sentiment_score': comment.negative_sentiment_score,
            'neutral_sentiment_score': comment.neutral_sentiment_score,
            'positive_sentiment_score': comment.positive_sentiment_score,
        }
        for comment in other_comments
    ]

    return comments_data
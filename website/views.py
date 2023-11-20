from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask import request
from flask import jsonify
from .mongodb_models import MongoDBHandler
from .neo4j_models import Neo4jHandler, User as Neo4jUser
from .mysql_models import SearchQuery, NextVideo, Like, Subscribe
from . import db
from sys import stderr

views = Blueprint('views', __name__)


@views.route('/')
def index():
    return render_template("index.html", user=current_user)


@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            new_search_query = SearchQuery(user_id=current_user.id, query=search_query)
            db.session.add(new_search_query)
            db.session.commit()
            mongo_handler = MongoDBHandler(url="localhost", port=27017, db_name="testdb", collection_name="videos")
            search_results = mongo_handler.search(search_query=search_query)
        if search_results:
            return render_template("search.html", user=current_user, search_query=search_query, search_results=search_results)
    
    return render_template("search.html", user=current_user)


@views.route('/video/<video_id>', methods=['GET', 'POST'])
@login_required
def video(video_id):
    neo4j = Neo4jHandler(uri="bolt://localhost:7687", username="neo4j", password="password")
    mongo_handler = MongoDBHandler(url="localhost", port=27017, db_name="testdb", collection_name="videos")

    neo4j_user = Neo4jUser(user_id=current_user.id)
    user_metadata = neo4j_user.get_metadata(video_id=video_id)
    liked = user_metadata['liked']
    disliked = user_metadata['disliked']
    subscribed = user_metadata['subscribed']

    suggested_video_ids = neo4j.get_score_wrt_current_video(video_id)
    suggested_videos = []
    for suggested_video_id in suggested_video_ids:
        video_data = mongo_handler.get_data(video_id=suggested_video_id)
        video_data['likeCount'] = neo4j.get_video_property(video_id=suggested_video_id, property_name='likes')
        video_data['dislikeCount'] = neo4j.get_video_property(video_id=suggested_video_id, property_name='dislikes')
        video_data['viewCount'] = neo4j.get_video_property(video_id=suggested_video_id, property_name='views')

        suggested_videos.append(mongo_handler.get_data(video_id=suggested_video_id))
    
    current_video_data = mongo_handler.get_data(video_id=video_id)
    current_video_data['likeCount'] = neo4j.get_video_property(video_id=video_id, property_name='likes')
    current_video_data['dislikeCount'] = neo4j.get_video_property(video_id=video_id, property_name='dislikes')
    current_video_data['viewCount'] = neo4j.get_video_property(video_id=video_id, property_name='views')

    return render_template("video.html", user=current_user, video_id=video_id, 
        current_video_data=current_video_data, suggested_videos=suggested_videos,
        liked=liked, disliked=disliked, subscribed=subscribed)

@views.route('/like', methods=['GET', 'POST'])
@login_required
def like():
    if request.method == 'POST':
        data = request.get_json()
        action = data['action']
        video_id = data['video_id']

        neo4j_user = Neo4jUser(user_id=current_user.id)
        neo4j_handler = Neo4jHandler()

        if action == 'like':
            neo4j_user.like(video_id=video_id)

            # prev_like_count = neo4j_handler.get_video_property(video_id=video_id, property_name='likes')
            # prev_dislike_count = neo4j_handler.get_video_property(video_id=video_id, property_name='dislikes')
            
            user_metadata = neo4j_user.get_metadata(video_id=video_id)
            liked = user_metadata['liked']
            disliked = user_metadata['disliked']

            like_count = neo4j_handler.get_video_property(video_id=video_id, property_name='likes')
            dislike_count = neo4j_handler.get_video_property(video_id=video_id, property_name='dislikes')
    
            # like_state = 'l+' if prev_like_count < like_count else 'l-' if prev_like_count > like_count else ''
            # dislike_state = 'd+' if prev_dislike_count < dislike_count else 'd-' if prev_dislike_count > dislike_count else ''
            # overall_like_state = like_state + dislike_state
            # like_status = ''
            # if 'l+' in overall_like_state:
            #     like_status = 'liked'
            # elif 'd+' in overall_like_state:
            #     like_status = 'disliked'
            # elif overall_like_state == 'l-':
            #     like_status = 'removed like'
            # elif overall_like_state == 'd-':
            #     like_status = 'removed dislike'

            like_status = 1
            new_like = Like(user_id=current_user.id, video_id=video_id, like_status=like_status)
            db.session.add(new_like)
            db.session.commit()

            return jsonify({'status': 'success', 'message': 'Request successful', 
                'liked': liked, 'disliked': disliked,
                'likeCount': like_count, 'dislikeCount': dislike_count,})
        
        elif action == 'dislike':
            neo4j_user.dislike(video_id=video_id)

            # prev_like_count = neo4j_handler.get_video_property(video_id=video_id, property_name='likes')
            # prev_dislike_count = neo4j_handler.get_video_property(video_id=video_id, property_name='dislikes')
            
            user_metadata = neo4j_user.get_metadata(video_id=video_id)
            liked = user_metadata['liked']
            disliked = user_metadata['disliked']

            like_count = neo4j_handler.get_video_property(video_id=video_id, property_name='likes')
            dislike_count = neo4j_handler.get_video_property(video_id=video_id, property_name='dislikes')

            # like_state = 'l+' if prev_like_count < like_count else 'l-' if prev_like_count > like_count else ''
            # dislike_state = 'd+' if prev_dislike_count < dislike_count else 'd-' if prev_dislike_count > dislike_count else ''
            # overall_like_state = like_state + dislike_state
            # like_status = ''
            # if overall_like_state in ['l+','l+d-']:
            #     like_status = 'liked'
            # elif overall_like_state in ['d+','l-d+']:
            #     like_status = 'disliked'
            # elif overall_like_state == 'l-':
            #     like_status = 'removed like'
            # elif overall_like_state == 'd-':
            #     like_status = 'removed dislike'

            like_status = 0
            new_dislike = Like(user_id=current_user.id, video_id=video_id, like_status=like_status)
            db.session.add(new_dislike)
            db.session.commit()

            return jsonify({'status': 'success', 'message': 'Request successful.',
                'liked': liked, 'disliked': disliked,
                'likeCount': like_count, 'dislikeCount': dislike_count,})
        
    return jsonify({"message": "Invalid request."})


@views.route('/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe():
    if request.method == 'POST':
        data = request.get_json()
        action = data['action']
        video_id = data['video_id']
        
        mongodb_handler = MongoDBHandler(url="localhost", port=27017, db_name="testdb", collection_name="videos")
        neo4j_user = Neo4jUser(user_id=current_user.id)

        if action == 'subscribe':
            channel_id = mongodb_handler.get_data(video_id=video_id)['channelId']
            neo4j_user.subscribe(channel_id=channel_id)
            user_metadata = neo4j_user.get_metadata(video_id=video_id)
            subscribed = user_metadata['subscribed']

            new_subscribe = Subscribe(user_id=current_user.id, channel_id=video_id, subscribe_status=subscribed)
            db.session.add(new_subscribe)
            db.session.commit()

            return jsonify({'status': 'success', 'message': 'Request successful.', 'subscribed': subscribed})
        
    return jsonify({"message": "Invalid request."})


@views.route('/next_video', methods=['GET', 'POST'])
@login_required
def next_video():
    if request.method == 'POST':
        data = request.get_json()
        current_video_id = data['current_video_id']
        next_video_id = data['next_video_id']

        new_next_video = NextVideo(user_id=current_user.id, current_video_id=current_video_id, next_video_id=next_video_id)
        db.session.add(new_next_video)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Request successful.'})
    
    return jsonify({"message": "Invalid request."})

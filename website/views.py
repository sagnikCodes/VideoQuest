from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask import request
from .mongodb_model import MongoDBHandler
from .neo4j_models import Neo4jHandler

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

    suggested_video_ids = neo4j.get_score_wrt_current_video(video_id)
    suggested_videos = []
    for suggested_video_id in suggested_video_ids:
        suggested_videos.append(mongo_handler.get_data(video_id=suggested_video_id))
    
    current_video_data = mongo_handler.get_data(video_id=video_id)

    return render_template("video.html", user=current_user, video_id=video_id, 
        current_video_data=current_video_data, suggested_videos=suggested_videos)

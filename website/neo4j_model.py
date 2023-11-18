import os
import json
from pymongo import MongoClient, ASCENDING
from py2neo import Graph, Node, Relationship
import nltk
from nltk.corpus import stopwords

client = MongoClient('localhost', 27017)
db = client['test_database']
collection = db['test_collection']
videos_data = list(collection.find())
nltk.download('stopwords')
english_stopwords = set(stopwords.words('english'))


class Neo4jHandler(object):
    
    def __init__(self, uri, username, password):
        self.graph = Graph(uri, auth=(username, password))
    
    def __get_video_property(self, video_id, property_name):
        query = f"MATCH (v:VIDEO {{video_id: '{video_id}'}}) RETURN v.{property_name} AS result"
        result = self.graph.run(query).evaluate()
        return result
    
    def __get_num_common_property(self, video_node1, video_node2, property_name):
        video_id1, video_id2 = video_node1['video_id'], video_node2['video_id']
        property_video1 = self.__get_video_property(video_id1, property_name)
        property_video2 = self.__get_video_property(video_id2, property_name)
        if(property_name != 'tags'):
            property_video1 = property_video1.split()
            property_video2 = property_video2.split()
        try:
            property_lower_capped_1 = [each.lower() for each in property_video1 if each not in english_stopwords]
        except TypeError:
            property_lower_capped_1 = []
        try:
            property_lower_capped_2 = [each.lower() for each in property_video2 if each not in english_stopwords]
        except TypeError:
            property_lower_capped_2 = []
            
        return len(set(property_lower_capped_1) & set(property_lower_capped_2))
        
        
    def create_video_node(self, video_data):
        # We are storing each important information in video node so that accessing the relevant information is faster
        video_id = video_data["videoInfo"]["id"]
        likes = video_data["videoInfo"]["statistics"]["likeCount"]
        dislikes = video_data["videoInfo"]["statistics"]["dislikeCount"]
        views = video_data["videoInfo"]["statistics"]["viewCount"]
        channel = video_data["videoInfo"]["snippet"]["channelId"]
        title = video_data["videoInfo"]["snippet"]["title"]
        description = video_data["videoInfo"]["snippet"]["description"]
        try:
            tags = video_data["videoInfo"]["snippet"]["tags"]
        except:
            tags = []
        video_node = Node("VIDEO", video_id=video_id, likes=likes, dislikes=dislikes, views=views, channel=channel, tags=tags, title=title, description=description)
        self.graph.create(video_node)
    
    def create_same_channel_relationship(self, video_id1, video_id2):
        video_node1 = self.graph.nodes.match("VIDEO", video_id=video_id1).first()
        video_node2 = self.graph.nodes.match("VIDEO", video_id=video_id2).first()
        channel_id1 = self.__get_video_property(video_id1, "channel")
        channel_id2 = self.__get_video_property(video_id2, "channel")
        if(channel_id1 == channel_id2):
            same_channel_relation = Relationship(video_node1, "SAME_CHANNEL", video_node2)
            self.graph.create(same_channel_relation)
        
    def create_similar_tags_relationship(self, video_id1, video_id2):
        video_node1 = self.graph.nodes.match("VIDEO", video_id=video_id1).first()
        video_node2 = self.graph.nodes.match("VIDEO", video_id=video_id2).first()
        num_common_tags = self.__get_num_common_property(video_node1, video_node2, "tags")
        if(num_common_tags > 0):
            common_tag_relationship = Relationship(video_node1, "HAS_COMMON_TAG", video_node2, num_common_tags=num_common_tags)
            self.graph.create(common_tag_relationship)
    
    def create_similar_description_relationship(self, video_id1, video_id2):
        video_node1 = self.graph.nodes.match("VIDEO", video_id=video_id1).first()
        video_node2 = self.graph.nodes.match("VIDEO", video_id=video_id2).first()
        num_common_description_words = self.__get_num_common_property(video_node1, video_node2, "description")
        if(num_common_description_words > 5):
            similar_description_relationship = Relationship(video_node1, "HAS_SIMILAR_DESCRIPTION", video_node2, num_common_description_words=num_common_description_words)
            self.graph.create(similar_description_relationship)
            
    def create_similar_title_relationship(self, video_id1, video_id2):
        video_node1 = self.graph.nodes.match("VIDEO", video_id=video_id1).first()
        video_node2 = self.graph.nodes.match("VIDEO", video_id=video_id2).first()
        num_common_title_words = self.__get_num_common_property(video_node1, video_node2, "title")
        if(num_common_title_words > 2):
            similar_title_relationship = Relationship(video_node1, "HAS_SIMILAR_TITLE", video_node2, num_common_title_words=num_common_title_words)
            self.graph.create(similar_title_relationship)
            
    def create_video_channel_relationship(self, video_id):
        video_node = self.graph.nodes.match("VIDEO", video_id=video_id).first()
        channel_id = self.__get_video_property(video_id, "channel")
        # Create channel node
        channel_node = Node("CHANNEL", channel_id=channel_id)
        self.graph.create(channel_node)
        video_channel_relationship = Relationship(video_node, "CHANNEL_NAME", channel_node)
        self.graph.create(video_channel_relationship)
        
    def create_user_subscribed_channel_relationship(self, user_id, channel_id):
        user_node = self.graph.nodes.match("USER", user_id=user_id).first() or Node("USER", user_id=user_id)
        channel_node = self.graph.nodes.match("CHANNEL", channel_id=channel_id).first()
        user_subsribed_channel_relationship = Relationship(user_node, "SUBSCRIBED", channel_node)
        self.graph.create(user_subsribed_channel_relationship)
            
    def user_hit_bell_icon(self, user_id, channel_id):
        user_node = self.graph.nodes.match("USER", user_id=user_id).first()
        channel_node = self.graph.nodes.match("CHANNEL", channel_id=channel_id).first()
        user_hit_bell_icon_relationship = Relationship(user_node, "HIT_BELL_ICON", channel_node)
        self.graph.create(user_hit_bell_icon_relationship)
        
    def create_user_liked_video_relationship(self, user_id, video_id):
        user_node = self.graph.nodes.match("USER", user_id=user_id).first()
        video_node = self.graph.nodes.match("VIDEO", video_id=video_id).first()
        user_liked_video_relationship = Relationship(user_node, "LIKED", video_node)
        self.graph.create(user_liked_video_relationship)
        query = (
            f"MATCH (video:VIDEO {{video_id: '{video_id}'}}) "
            "SET video.likes = video.likes + 1"
        )
        self.graph.run(query)
    
    def create_user_disliked_video_relationship(self, user_id, video_id):
        user_node = self.graph.nodes.match("USER", user_id=user_id).first()
        video_node = self.graph.nodes.match("VIDEO", video_id=video_id).first()
        user_disliked_video_relationship = Relationship(user_node, "DISLIKED", video_node)
        self.graph.create(user_disliked_video_relationship)
        query = (
            f"MATCH (video:VIDEO {{video_id: '{video_id}'}}) "
            "SET video.dislikes = video.dislikes + 1"
        )
        self.graph.run(query)
        
    def create_initial_graph(self):
        # for video_data in videos_data:
        #     self.create_video_node(video_data)
        video_id_list = [video_data["videoInfo"]["id"] for video_data in videos_data]
        num_videos = len(video_id_list)
        for i in range(num_videos):
            for j in range(num_videos):
                if(i == j):
                    continue
                video_id1 = video_id_list[i]
                video_id2 = video_id_list[j]
                self.create_same_channel_relationship(video_id1, video_id2)
                self.create_similar_tags_relationship(video_id1, video_id2)
                self.create_similar_description_relationship(video_id1, video_id2)
                self.create_similar_title_relationship(video_id1, video_id2)
        for video_id in video_id_list:
            self.create_video_channel_relationship(video_id)


neo4j = Neo4jHandler(uri="bolt://localhost:7687", username="neo4j", password="password")
neo4j.create_initial_graph()

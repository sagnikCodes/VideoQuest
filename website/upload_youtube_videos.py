import json
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException
from pymongo import MongoClient
import re
from .mongodb_models import MongoDBHandler
from .neo4j_models import Neo4jHandler
from .preprocessing import get_relevant_keywords_from_videodata, get_captions


class Upload(object):

    def get_tags(self, description):
        # tags are in last line of description
        last_line = description.split('\n')[-1]
        if '#' in last_line:
            # means video has tags as tags are always written with # 
            tags = last_line.split("#")
            tags = [tag.strip() for tag in tags]
            return tags[1:]
        else:
            return []
        

    def format_likeCount(self, likes):
        likeCount_uncleaned = ''.join(likes.split('\n'))[1:]
        likesCount = ''
        multiplier = 1
        for digit in likeCount_uncleaned:
            if digit == ' ':
                continue
            elif digit == 'K':
                multiplier = 1000
                continue
            elif digit == 'M':
                multiplier = 1000000
                continue
            elif digit == 'B':
                multiplier = 100000000
                continue
            likesCount += digit
        return int(float(likesCount) * multiplier)
            
        
        
    def get_video_data(self, url, waiting_time=5):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')  # Because, we don't want it to pop up
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        WebDriverWait(driver, waiting_time).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.ytd-watch-metadata'))
        )
        title = driver.find_element(By.CSS_SELECTOR, 'h1.ytd-watch-metadata').text
        channel_element = driver.find_element(By.ID, 'owner')
        channelId = channel_element.find_element(By.ID, 'channel-name').text
        driver.find_element(By.ID, 'description-inline-expander').click()
        viewCount = driver.find_elements(By.CSS_SELECTOR, '#info-container span')[0].text.replace(' views', '')
        if ',' in viewCount:
            viewCount = viewCount.replace(',', '')
        description = driver.find_element(By.CSS_SELECTOR, '#description-inline-expander .ytd-text-inline-expander span').text
        likeCount = driver.find_element(By.ID, 'segmented-like-button').text
        likeCount = self.format_likeCount(likeCount)
        tags = self.get_tags(description)
        result = {}
        pattern = re.compile(r'(?<=v=)[\w-]+|(?<=youtu.be\/)[\w-]+')
        videoId = pattern.findall(url)[0]

        with open('individual.json', 'r') as file:
            individual = json.load(file)
        if videoId in individual:
            return None

        tags = tags + get_captions(videoId)
        result["videoId"] = videoId
        result["channelId"] = channelId
        result["title"] = title
        result["channelTitle"] = channelId
        result["description"] = description
        result["categoryId"] = 0
        result["tags"] = tags
        result["viewCount"] = int(viewCount)
        result["likeCount"] = likeCount
        result["dislikeCount"] = 0  # youtube doesn't show dislike count nowadays
        result["thumbnails"] = {
            "high": {"url": f"https://img.youtube.com/vi/{videoId}/hqdefault.jpg"}
        }
        result["relevantKeywords"] = get_relevant_keywords_from_videodata(title, channelId, description, tags)
        driver.close()
        return result

    def add_data_to_mongodb(self, video_data):
        mongo_handler = MongoDBHandler()
        mongo_handler.upload_single_video_data(video_data)

    def add_data_to_neo4j(self, video_data):
        neo4j_handler = Neo4jHandler()
        neo4j_handler.create_video_node(video_data)
        client = MongoClient('localhost', 27017)
        db = client['testdb']
        collection = db['videos']
        videos_data = list(collection.find())
        for video_data_ in videos_data:
            video_id = video_data_["videoId"]
            uploaded_video_id = video_data["videoId"] 
            neo4j_handler.create_same_channel_relationship(video_id, uploaded_video_id)
            neo4j_handler.create_similar_tags_relationship(video_id, uploaded_video_id)
            neo4j_handler.create_similar_description_relationship(video_id, uploaded_video_id)
            neo4j_handler.create_similar_title_relationship(video_id, uploaded_video_id)
            neo4j_handler.create_video_channel_relationship(uploaded_video_id)

    def upload_video(self, url):
        print(url)
        video_data = self.get_video_data(url)
        if video_data is None:
            return
        self.add_data_to_mongodb(video_data)
        self.add_data_to_neo4j(video_data)
        neo4j = Neo4jHandler()
        neo4j.add_uploaded_video_info_to_individual_cache(video_data['videoId'])
        neo4j.add_uploaded_video_info_to_relations_cache(video_data['videoId'])
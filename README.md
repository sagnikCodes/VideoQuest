# VideoQuest - Video Search Engine


## Overview
This project is a video search engine application with a graphical user interface (GUI) using MongoDB, Neo4j, and MySQL for data storage and retrieval. The application includes features such as video indexing, relationship management, user authentication, sentiment analysis for user comments, and personalized video recommendations.


## Important Links
- [Video Demonstration](https://drive.google.com/file/d/1EUzJmuM91H0Fe28PXFvUMv_X57JwLa-Z/view?usp=drive_link)
- [Saved Models](https://drive.google.com/drive/folders/1PQxg29JX-YMdvFJCsMQGtK1B7J8ujtuk?usp=drive_link)

## Project Directory Structure
### Root Directory
| Directory/File | Description |
|-|-|
| `hate_speech_model.joblib` | Joblib file for the hate speech detection model. |
| `individual.json` | JSON file containing individual video data. |
| `main.py` | Main script for the video search engine application. |
| `preprocessed_data` | Directory containing preprocessed video data in JSON format. |
| `relations.json` | JSON file containing relationship data. |
| `sentiment_analysis_pipeline.joblib` | Joblib file for the sentiment analysis model pipeline. |
| `sentiment_analysis_training.py` | Script for training the sentiment analysis model. |
| `users.json` | JSON file containing user data. |
| `users_relation.json` | JSON file containing user relationship data. | 
| `video_data` | Directory containing raw video data. |

### `website` Directory
| Directory/File | Description |
|-|-|
| `api.py` | Flask Blueprint for sentiment analysis API routes. |
| `auth.py` | Flask Blueprint for user authentication routes. |
| `creators.py` | Flask Blueprint for user analytics routes. |
| `mongodb_models.py` | Class for MongoDB interactions. |
| `mysql_models.py` | Data models for SQLAlchemy and MySQL. |
| `neo4j_models.py` | Class for Neo4j interactions and search recommendations. |
| `preprocessing.py` | Script for video data preprocessing. |
| `static` | Directory for static assets in the Flask application. |
| `templates` | Directory for HTML templates in the Flask application. |
| `upload_youtube_videos.py` | Class for uploading YouTube video data. |
| `views.py` | Flask Blueprint for general web application routes. |

## User Interface Preview
#### Beautiful Backend and Landing Page
![landingpages](https://github.com/sagnikCodes/VideoQuest/assets/101598170/177a5e5f-aeb4-42b0-a31e-1a8e501def8c)  
Showcasing the aesthetically designed backend and landing page of the video search engine.

#### Sign Up and Login Pages
![signinpages](https://github.com/sagnikCodes/VideoQuest/assets/101598170/b9074603-9c66-43ee-b16c-f2206b4addf2)  
Highlighting the user-friendly sign-up and login pages for seamless authentication.

### Home Screen with Search Bar
![home](https://github.com/sagnikCodes/VideoQuest/assets/101598170/a6aafdfc-9280-40c2-8c1e-8cd363804f76)  
Illustrating the home screen featuring an intuitive search bar for easy video queries.

#### Video Page with Suggestions and Interactions
![video](https://github.com/sagnikCodes/VideoQuest/assets/101598170/fd7c88bf-3c26-495b-b01f-aaf08a203152)
Providing a glimpse of the video page presenting the selected video, related suggestions, and interactive options like liking, subscribing, and adding comments.

#### Upload Videos and Sentiment Analysis
![uploadsentiment](https://github.com/sagnikCodes/VideoQuest/assets/101598170/1b08a4c6-0fd5-4f22-9f64-1a2746f6d639)  
Showcasing the functionality allowing users to upload favorite YouTube videos and creators to check sentiment analysis for their videos.

## Features
### Multi-Database Integration
- **MongoDB:**
  - Indexing Video Files: Efficient indexing of video files for fast retrieval.
  - Search Functionality: MongoDB used for search based on common words and relevant keywords. Jaro similarity-based scoring system employed to rank search results.

- **Neo4j:**
  - Managing Relationships: Nodes for 'USER,' 'CHANNEL,' and 'VIDEO.' Relationships established based on commonalities such as subscribed channels, liked videos, and similar content.

- **MySQL:**
  - Relational Information Storage: Storing click-through data and relational information, critical for improving search results and personalized recommendations.

### Graphical User Interface (GUI)
- **Components:**
  - **Search Query Panel (SQP):** Allows users to input video search queries.
  - **Search Button (SB):** Initiates the search based on the query.
  - **Search Result Panel (SRP):** Displays a list of relevant videos.
  - **Current Video Panel (CVP):** Shows detailed information about the selected video.

- **Workflow:**
  - Users input search queries in SQP and click SB to view relevant videos in SRP.
  - Clicking on a video in SRP updates CVP with video details and refreshes SRP with related videos from Neo4j.
  - Click-through information is stored in MySQL, capturing details about user interactions and preferences.

### User Authentication and Customization
- **Authentication:**
  - User login, logout, and signup functionality.
  - Secure password hashing.

- **Customization:**
  - Initial video suggestions based on common words.
  - User behavior tracking for customization as users interact more.

### Sentiment Analysis
- Sentiment analysis on user comments using a machine learning pipeline.
- Trained model utilized in the Flask API to provide sentiment scores for comments.

### Web Scraping and External APIs
- Web scraping for extracting video data from YouTube.
- External APIs used for correcting English in search queries.

### Analytics and Collaborative Filtering
- User analytics for processing and analyzing user comments using a pre-trained machine learning model for hate speech detection.
- Collaborative filtering using Neo4j, creating relationships based on user interactions.

### Caching Mechanism
  - Implemented a **JSON-based** caching mechanism to store user activity and metadata changes.
  - Data, such as video metadata and user activity, cached in JSON files for faster retrieval and updating.
  - Optimized data fetching from Neo4j, particularly when dealing with slow Python abstractions.


## System and Database Dependencies
| Dependency | Purpose |
|-|-|
| `Python 3.x` | Programming language for the project.  |
| `mongodb` | Database for storing video information and enabling fast queries. |
| `mysql` | Database for managing user-related data, login credentials, and user behavior tracking. |
| `neo4j` | Database for storing relationships between users, channels, and videos for the recommendation engine. |

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`.
2. Configure database connections in respective files.
3. Run the Flask application: `python main.py`.


## Authors
- **[Akriti Gupta](mailto:gupta.97@iitj.ac.in)**: Pre-final Year (B.Tech. Artificial Intelligence & Data Science)
- **[Sagnik Goswami](mailto:goswami.5@iitj.ac.in)**: Pre-final Year (B.Tech. Artificial Intelligence & Data Science)
- **[Tanish Pagaria](mailto:pagaria.2@iitj.ac.in)**: Pre-final Year (B.Tech. Artificial Intelligence & Data Science)  
(IIT Jodhpur Undergraduates)

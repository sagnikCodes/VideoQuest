document.addEventListener('DOMContentLoaded', function() {
    const data = {
        "videoInfo": {
            "snippet": {
                "thumbnails": {
                    "default": {
                        "url": "https://i.ytimg.com/vi/_-Qxl9eE8Mk/default.jpg",
                        "width": 120,
                        "height": 90
                    },
                    "high": {
                        "url": "https://i.ytimg.com/vi/_-Qxl9eE8Mk/hqdefault.jpg",
                        "width": 480,
                        "height": 360
                    },
                    "medium": {
                        "url": "https://i.ytimg.com/vi/_-Qxl9eE8Mk/mqdefault.jpg",
                        "width": 320,
                        "height": 180
                    },
                    "maxres": {
                        "url": "https://i.ytimg.com/vi/_-Qxl9eE8Mk/maxresdefault.jpg",
                        "width": 1280,
                        "height": 720
                    },
                    "standard": {
                        "url": "https://i.ytimg.com/vi/_-Qxl9eE8Mk/sddefault.jpg",
                        "width": 640,
                        "height": 480
                    }
                },
                "tags": [
                    "top news",
                    "news in hindi",
                    "hindi news",
                    "today's news",
                    "delhi news",
                    "best news",
                    "aajtak",
                    "aajtak news",
                    "latest news",
                    "latest hindi news",
                    "Pepper media"
                ],
                "channelId": "UCt4t-jeY85JegMlZ-E5UWtA",
                "publishedAt": "2016-09-19T06:25:30.000Z",
                "liveBroadcastContent": "none",
                "channelTitle": "Aaj Tak",
                "title": "20 Jawans Injured In Uri Attack, Rajnath Singh To Submit Report To PM Modi Today",
                "categoryId": "25",
                "localized": {
                    "description": "Follow us:\nYouTube: https://www.youtube.com/user/aajtaktv?sub_confirmation=1\nTwitter: https://twitter.com/aajtak\nFacebook: http://www.facebook.com/aajtak\n\nTags: Fast News,Breaking News,Top Headlines,Super fast news,Khabare Superfast,Superfast!,news,sensational news,political news,sports news,Super fast,Jawaharlal Nehru University,controversy,students,union leader,sedition,anti-national\u2019 slogans,Parliament attack,Kanhaiya Kumar,Rohith Vemula,Manish Sisodia,Nirbhaya Case,protests,Juvenile,Delhi Gang Rapist,DUSU,Delhi University Students Union,Jawaharlal Nehru University Students Union,JNUSU,Jantar Mantar,demonstrations,Union Finance Minister,Quota ,Arun Jaitley,criminal,defamation,Delhi Chief Minister,Patiala House,AAP,Arvind Kejriwal,DDCA,Salman Khan,Acquittal,Salman Khan (Film Actor),Bollywood,Bollywood Str,Asaduddin,Owaisi,AIMIM,Bharat Mata Ki Jai,RSS,Bombay High Court,Congress,Sonia Gandhi,Rahul Gandhi,trial court,National Herald case,Gandhi,Congress,BJP,National Herald,Subramanian Swamy,Pakistan,Narendra Modi,Nawaz Sharif,Pakistani Terrorists,Pathankot,Uttarakhand",
                    "title": "20 Jawans Injured In Uri Attack, Rajnath Singh To Submit Report To PM Modi Today"
                },
                "description": "Follow us:\nYouTube: https://www.youtube.com/user/aajtaktv?sub_confirmation=1\nTwitter: https://twitter.com/aajtak\nFacebook: http://www.facebook.com/aajtak\n\nTags: Fast News,Breaking News,Top Headlines,Super fast news,Khabare Superfast,Superfast!,news,sensational news,political news,sports news,Super fast,Jawaharlal Nehru University,controversy,students,union leader,sedition,anti-national\u2019 slogans,Parliament attack,Kanhaiya Kumar,Rohith Vemula,Manish Sisodia,Nirbhaya Case,protests,Juvenile,Delhi Gang Rapist,DUSU,Delhi University Students Union,Jawaharlal Nehru University Students Union,JNUSU,Jantar Mantar,demonstrations,Union Finance Minister,Quota ,Arun Jaitley,criminal,defamation,Delhi Chief Minister,Patiala House,AAP,Arvind Kejriwal,DDCA,Salman Khan,Acquittal,Salman Khan (Film Actor),Bollywood,Bollywood Str,Asaduddin,Owaisi,AIMIM,Bharat Mata Ki Jai,RSS,Bombay High Court,Congress,Sonia Gandhi,Rahul Gandhi,trial court,National Herald case,Gandhi,Congress,BJP,National Herald,Subramanian Swamy,Pakistan,Narendra Modi,Nawaz Sharif,Pakistani Terrorists,Pathankot,Uttarakhand"
            },
            "kind": "youtube#video",
            "statistics": {
                "commentCount": 1,
                "viewCount": 5905,
                "favoriteCount": 0,
                "dislikeCount": 1,
                "likeCount": "6"
            },
            "etag": "\"gMxXHe-zinKdE9lTnzKu8vjcmDI/wA0x3F2EZ4f29zQDJx_2_piNN6A\"",
            "id": "_-Qxl9eE8Mk"
        }
    };

    const videoId = data.videoInfo.id;

    const iframe = document.createElement("iframe");
    iframe.setAttribute("width", "560");
    iframe.setAttribute("height", "315");
    iframe.setAttribute("src", `https://www.youtube.com/embed/${videoId}`);
    iframe.setAttribute("frameborder", "0");
    iframe.setAttribute("allowfullscreen", "true");

    console.log(`https://www.youtube.com/embed/${videoId}`)

    const videoContainer = document.getElementById("video-container");
    videoContainer.appendChild(iframe);

    const suggestedVideos = [
        {
            title: "Suggested Video 1",
            id: videoId,
            thumbnail: data.videoInfo.snippet.thumbnails.default.url,
            description: "Short description of Suggested Video 1"
        },
        {
            title: "Suggested Video 2",
            id: videoId,
            thumbnail: data.videoInfo.snippet.thumbnails.default.url,
            description: "Short description of Suggested Video 2"
        }
    ];

    const suggestedVideosContainer = document.getElementById("suggested-videos");
    suggestedVideos.forEach((video) => {
        const suggestionLink = document.createElement("a");
        suggestionLink.href = `https://www.youtube.com/watch?v=${video.id}`;
        suggestionLink.classList.add("suggestion-link");

        const suggestionBox = document.createElement("div");
        suggestionBox.classList.add("suggestion-box");

        const thumbnail = document.createElement("div");
        thumbnail.classList.add("suggestion-thumbnail");
        const thumbnailImage = document.createElement("img");
        thumbnailImage.src = video.thumbnail;
        thumbnail.appendChild(thumbnailImage);

        const details = document.createElement("div");
        details.classList.add("suggestion-details");

        const title = document.createElement("div");
        title.classList.add("suggestion-title");
        title.textContent = video.title;

        const description = document.createElement("div");
        description.classList.add("suggestion-description");
        description.textContent = video.description;

        details.appendChild(title);
        details.appendChild(description);
        suggestionBox.appendChild(thumbnail);
        suggestionBox.appendChild(details);
        suggestionLink.appendChild(suggestionBox);
        suggestedVideosContainer.appendChild(suggestionLink);
    });


    const likeButton = document.getElementById('like-button');
    const dislikeButton = document.getElementById('dislike-button');
    const subscribeButton = document.getElementById('subscribe-button');
    const bellIconButton = document.getElementById('bell-icon-button');

    let likeActive = false;
    let dislikeActive = false;
    let subscribeActive = false;
    let bellIconActive = false;

    function toggleButtonState(button, isActive) {
        if (isActive) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    }

    function updateSubscribeButton() {
        if (subscribeActive) {
            subscribeButton.textContent = "SUBSCRIBED";
            bellIconButton.style.display = "inline-block";
        } else {
            subscribeButton.textContent = "SUBSCRIBE";
            bellIconButton.style.display = "none";
        }
    }

    likeButton.addEventListener('click', function() {
        likeActive = !likeActive;
        dislikeActive = false;
        toggleButtonState(likeButton, likeActive);
        toggleButtonState(dislikeButton, dislikeActive);
    });

    dislikeButton.addEventListener('click', function() {
        dislikeActive = !dislikeActive;
        likeActive = false;
        toggleButtonState(likeButton, likeActive);
        toggleButtonState(dislikeButton, dislikeActive);
    });

    subscribeButton.addEventListener('click', function () {
        subscribeActive = !subscribeActive;
        bellIconActive = false;

        toggleButtonState(subscribeButton, subscribeActive);
        toggleButtonState(bellIconButton, bellIconActive);

        updateSubscribeButton();
    });

    bellIconButton.addEventListener('click', function () {
        bellIconActive = !bellIconActive;

        toggleButtonState(bellIconButton, bellIconActive);
    });
});

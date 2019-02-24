
import requests
import json
import time

__version__ = "0.2.2 Beta"

class TimelineConfig:
    URL = "https://timeline.line.me/api/"
    SESSION_ID = ""
    HOME_ID = ""
    HEADERS = {
        "Accept" : "application/json",
        "X-Timeline-WebVersion" : "1.11.9",
        "X-Line-AcceptLanguage" : "en",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36",
        "Origin" : "https://timeline.line.me",
        "Referer": "https://timeline.line.me/"
    }

    def set_session(self, session):
        self.SESSION_ID = session

    def set_home_id(self, homeid):
        self.HOME_ID = homeid

    def set_header(self, key, value):
        self.HEADERS[key] = value

    def get_config(self):
        self.set_header("Cookie", "lwtl=" + self.SESSION_ID)
        config = {
            "URL" : self.URL,
            "SESSION_ID" : self.SESSION_ID,
            "HOME_ID" : self.HOME_ID,
            "HEADERS" : self.HEADERS
        }
        return config

class TimelineReader:
    DATA = None
    FEED = []
    SCROLL_ID = None

    FEED_IS_FETCHED = False
    COUNT = 0

    def __init__(self, config):
        self.config = config.get_config()
    
    def request_feed(self, has_next=False):
        results = requests.get(
            self.config["URL"] + 
            "/post/list.json?homeId=" + self.config["HOME_ID"] + 
            (("&scrollId=" + self.SCROLL_ID) if has_next else "") +
            "&requestTime=" + str(time.time() * 1000), headers=self.config["HEADERS"])
        self.DATA = json.loads(results.text)

        try:
            self.SCROLL_ID = self.DATA["result"]["nextScrollId"]
        except KeyError:
            self.SCROLL_ID = None

        self.FEED = []
        self.FEED_IS_FETCHED = False
        self.COUNT = 0

        try:
            feeds = self.DATA["result"]["feeds"]
        except KeyError:
            feeds = []

        for feed in feeds:
            contents = feed["post"]["contents"]
            if "text" not in contents:
                continue
            feed_data = {
                "postId" : feed["post"]["postInfo"]["postId"],
                "type" : feed["feedInfo"]["type"],
                "likeCount" : feed["post"]["postInfo"]["likeCount"],
                "commentCount" : feed["post"]["postInfo"]["commentCount"],
                "content" : contents["text"],
                "commentScrollId" : feed["post"]["comments"]["nextScrollId"]
            }
            self.FEED.append(feed_data)

    
    def get_account_name(self):
        return self.DATA["result"]["homeInfo"]["userInfo"]["nickname"]

    def get_feed(self):
        if not len(self.FEED):
            return None
        feed = self.FEED[self.COUNT]
        return feed
    
    def fetch_feed(self):
        if not self.FEED_IS_FETCHED:
            self.FEED_IS_FETCHED = True
            return self.get_feed()

        self.COUNT += 1
        if(self.COUNT >= len(self.FEED)):
            return None

        return self.get_feed()

    def fetch_page(self):
        if self.DATA == None:
            self.request_feed()
        else:
            self.request_feed(True)
        return self.get_feed()

    def request_comment(self, content_id, scroll_id):
        results = requests.get(
            self.config["URL"] +
            "/comment/getList.json?homeId=" + self.config["HOME_ID"] + 
            "&actorId=" + self.config["HOME_ID"] + 
            "&contentId=" + content_id +
            "&scrollId=" + scroll_id, headers=self.config["HEADERS"]
        )
        try:
            data = json.loads(results.text)
        except JSONDecodeError:
            data = None
        return data
    
    def fetch_comments(self):
        comments = []
        feed = self.get_feed()
        content_id = feed["postId"]
        scroll_id = feed["commentScrollId"]
        has_next = True

        while has_next:
            data = self.request_comment(content_id, scroll_id)
            if data == None:
                break
            scroll_id = data["result"]["nextScrollId"]
            has_next = data["result"]["existNext"]
            tmp_comments = []
            for comment in data["result"]["commentList"]:
                tmp_comments.append(comment["commentText"])
            comments = tmp_comments + comments
        return comments

# THIS IS AN EXAMPLE FILE
# Gathering All Post and Comment from Line Official Account

import linelime
import json
import threading
from copy import copy

# Session ID from cookie
session = "YOUR_SESSION_ID"

# Home ID from URL
home_id = "_dc-7fplr21FHo7GOzNeg9XSmLgAineSgyAle1sE" # Draft SMS UGM Home ID

config = linelime.TimelineConfig()
config.set_session(session)
config.set_home_id(home_id)
reader = linelime.TimelineReader(config)

feeds = []

threads = []

def get_feed_threading(reader):
    feed = reader.get_feed()
    result = {
        "postId" : feed["postId"],
        "likeCount" : feed["likeCount"],
        "content" : feed["content"],
        "comments" : reader.fetch_comments()
    }
    feeds.append(result)

    # Save available data to txt file
    with open ('Draft_SMS_UGM.txt', 'a+', encoding="utf-8") as f:
        f.write(json.dumps(result) + "\n")

def run_threads(threads):
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

page = 1
while reader.fetch_page():
    print("Fetching page " + str(page) + "...")
    while reader.fetch_feed() != None:
        threads.append(threading.Thread(target=get_feed_threading, args=(copy(reader),)))
    if page % 25 == 0:
        run_threads(threads)
        threads = []
    page += 1

run_threads(threads)

# Save all data to JSON file after completed
data = {
    "feeds" : feeds
}
with open ('Draft_SMS_UGM.json', 'w+', encoding="utf-8") as f:
    f.write(json.dumps(data))

import requests

API_KEY = "REMOVED_KEY"
CHANNEL_ID = "UCWJ2lWNubArHWmf3FIHbfcQ"

url = f"https://www.googleapis.com/youtube/v3/search?part=id&channelId={CHANNEL_ID}&eventType=live&type=video&key={API_KEY}"

def get_live_video_id(url):
    response = requests.get(url).json()
    if "items" in response and len(response["items"]) > 0:
        LIVE_VIDEO_ID = response["items"][0]["id"]["videoId"]
        # print(f"Live Video ID: {LIVE_VIDEO_ID}")
        return LIVE_VIDEO_ID
    else:
        print("No active live stream found.")

def get_live_chat_id(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id={video_id}&key={API_KEY}"
    response = requests.get(url).json()
    return response["items"][0]["liveStreamingDetails"]["activeLiveChatId"]

def fetch_live_chat_messages(live_chat_id):
    url = f"https://www.googleapis.com/youtube/v3/liveChat/messages?liveChatId={live_chat_id}&part=snippet,authorDetails&key={API_KEY}"
    response = requests.get(url).json()
    for item in response.get("items", []):
        print(f"{item['authorDetails']['displayName']}: {item['snippet']['displayMessage']}")
    return response["nextPageToken"]

if __name__ == "__main__":
    LIVE_VIDEO_ID = get_live_video_id(url)
    live_chat_id = get_live_chat_id(LIVE_VIDEO_ID)
    fetch_live_chat_messages(live_chat_id)

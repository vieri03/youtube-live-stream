import requests
import json
import time
from kafka import KafkaProducer

# Your YouTube API Key
API_KEY = ""
CHANNEL_ID = ""

KAFKA_TOPIC = "youtube-live-chat"
KAFKA_SERVER = "kafka:9092"  # Kafka in Docker

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Fetch Live Stream ID
def get_live_video_id():
    url = f"https://www.googleapis.com/youtube/v3/search?part=id&channelId={CHANNEL_ID}&eventType=live&type=video&key={API_KEY}"
    response = requests.get(url).json()
    if "items" in response and response["items"]:
        return response["items"][0]["id"]["videoId"]
    return None

# Fetch Live Chat ID
def get_live_chat_id(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id={video_id}&key={API_KEY}"
    response = requests.get(url).json()
    return response["items"][0]["liveStreamingDetails"].get("activeLiveChatId")

# Stream Data to Kafka
def stream_to_kafka():
    video_id = get_live_video_id()
    if not video_id:
        print("No active live stream found.")
        return

    live_chat_id = get_live_chat_id(video_id)
    print(f"Streaming chat messages from YouTube Live Stream: {video_id}")

    next_page_token = None

    while True:
        url = f"https://www.googleapis.com/youtube/v3/liveChat/messages?liveChatId={live_chat_id}&part=snippet,authorDetails&key={API_KEY}"
        if next_page_token:
            url += f"&pageToken={next_page_token}"

        response = requests.get(url).json()

        messages = response.get("items", [])
        next_page_token = response.get("nextPageToken")

        for msg in messages:
            message_data = {
                "messageId": msg["id"],
                "message": msg["snippet"]["displayMessage"],
                "authorChannelId": msg["authorDetails"]["channelId"],
                "author": msg["authorDetails"]["displayName"],
                "timestamp": msg["snippet"]["publishedAt"]
            }
            producer.send(KAFKA_TOPIC, value=message_data)
            print(f"Sent: {message_data}")

        polling_interval = int(response.get("pollingIntervalMillis", 5000)) / 1000.0
        time.sleep(polling_interval)


if __name__ == "__main__":
    stream_to_kafka()

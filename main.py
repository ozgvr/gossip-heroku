import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time
import requests
import json
from sources import sources
from news_request import create_request_body
import os

cred = credentials.Certificate({
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN"),
})

firebase_admin.initialize_app(cred)

db = firestore.client()

def create_document():

    url = "https://newsapi.ai/api/v1/minuteStreamArticles"

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(create_request_body(sources=sources, apiKey=os.getenv("NEWS_API_KEY")))
    )

    response_text = response.text[14:-1]
    news = json.loads(response_text)

    # Save the news to Firestore
    for article in news["recentActivityArticles"]["activity"]:
        news_ref = db.collection('news').document()
        condensed_article = {
            "uri": article["uri"],
            "title": article["title"],
            "body": article["body"],
            "dateTime": article["dateTime"],
            "source": article["source"]["title"],
            "sourceUri": article["source"]["uri"],
            "url": article["url"],
            "image": article["image"],
            "language": article["lang"]
        }
        news_ref.set(condensed_article)

    print("Created a new document in 'news' collection.")

while True:
    create_document()
    time.sleep(7200)
import os
import json
import requests
from flask import Flask, request
from notion_client import Client

app = Flask(__name__)

# Environment variables for security
TELEGRAM_TOKEN = os.getenv("NOTION_TG_BOT")
NOTION_TOKEN = os.getenv("TG_NOTION_KEY")

# Initialize Notion client
notion = Client(auth=NOTION_TOKEN)

# Dictionary to store the current page for each user
user_pages = {}


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response


@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        if text.startswith("/setpage"):
            _, page_id = text.split(maxsplit=1)
            user_pages[chat_id] = page_id
            send_message(chat_id, f"Page set to {page_id}")

        elif text.startswith("/add"):
            if chat_id in user_pages:
                page_id = user_pages[chat_id]
                content = text[len("/add") :].strip()
                notion.pages.create(
                    parent={"page_id": page_id},
                    properties={},
                    children=[
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {"content": content},
                                    }
                                ]
                            },
                        }
                    ],
                )
                send_message(chat_id, "Content added to the page.")
            else:
                send_message(
                    chat_id, "Please set the page first using /setpage <PAGE_ID>."
                )

    return "OK"


if __name__ == "__main__":
    app.run(port=5000)

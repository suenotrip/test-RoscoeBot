import os
import sys
import json

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == 'test_token':#os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message


                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    send_message(sender_id, "got it, thanks!")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    
                    payload = messaging_event["postback"]["payload"]
                    if (payload=="START"):

                        sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                        recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                        #message_text = messaging_event["message"]["text"]  # the message's text

                        #fetch first name from FB graph
                        access_token=os.environ["PAGE_ACCESS_TOKEN"]
                        #access_token='EAAS7TZAqQM7UBAKeTGRXC8KNtUyBWE55nSCZAumZCEg2dZASkAUQdNhZCDAd7Ni7oZBOlaTHSGOdQ3BVV5vLLvDHJHZAnwTuIZBbBrXLiSHLJKRLza21deZAezRVZArrUZBT5R9PC3Eq7qrZBrpcxaI0ZAHIGr8FhcEs7qD4RxSXLhWrkvAZDZD'
                        r = requests.get("https://graph.facebook.com/v2.6/"+ sender_id + "?access_token="+access_token)
                        if r.status_code != 200:
                            log(r.status_code)
                            log(r.text)
                        else:
                            print(r.status_code)
                            print(r.text)
                            profile=json.loads(r.text)
                            first_name=profile['first_name']
                            #print(profile)
                            #print(first_name)
                            
                            send_message(sender_id, "Hi "+ first_name+ ", what would you like to do tonight?")
                            #pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        #"access_token":'EAAS7TZAqQM7UBAKeTGRXC8KNtUyBWE55nSCZAumZCEg2dZASkAUQdNhZCDAd7Ni7oZBOlaTHSGOdQ3BVV5vLLvDHJHZAnwTuIZBbBrXLiSHLJKRLza21deZAezRVZArrUZBT5R9PC3Eq7qrZBrpcxaI0ZAHIGr8FhcEs7qD4RxSXLhWrkvAZDZD'
        "access_token": os.environ["PAGE_ACCESS_TOKEN"] #|| 'EAAS7TZAqQM7UBAKeTGRXC8KNtUyBWE55nSCZAumZCEg2dZASkAUQdNhZCDAd7Ni7oZBOlaTHSGOdQ3BVV5vLLvDHJHZAnwTuIZBbBrXLiSHLJKRLza21deZAezRVZArrUZBT5R9PC3Eq7qrZBrpcxaI0ZAHIGr8FhcEs7qD4RxSXLhWrkvAZDZD'
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)

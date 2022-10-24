from requests_oauthlib import OAuth1Session
import os
import json
import config

# bearer = ""
consumer_key = ""
consumer_secret = ""

client_key = ""
client_secret = ""

class tweetAPI(object):
    def __init__(self, consumer, consumer_secret):
        self.consumer = consumer
        self.consumer_secret = consumer_secret

        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        self.oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

        try:
            fetch_response = self.oauth.fetch_request_token(request_token_url)
        except ValueError:
            print(
                "There may have been an issue with the consumer_key or consumer_secret you entered."
            )

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        print("Got OAuth token: %s" % resource_owner_key)

        # Get authorization
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = self.oauth.authorization_url(base_authorization_url,
                                                    scope="tweet.read%20users.read%20tweet.write%20like.write")
        print("Please go here and authorize: %s" % authorization_url)
        verifier = input("Paste the PIN here: ")

        # Get the access token
        access_token_url = "https://api.twitter.com/oauth/access_token"
        self.oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_tokens = self.oauth.fetch_access_token(access_token_url)

        self.access_token = oauth_tokens["oauth_token"]
        self.access_token_secret = oauth_tokens["oauth_token_secret"]

    def send_tweet(self, text):
        payload = {"text": text}

        response = self.oauth.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )
        return response

    def send_reply(self, text, tweetId):
        payload = {"text": text, "reply": {"in_reply_to_tweet_id": str(tweetId)}}

        response = self.oauth.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )
        return response

    def like_tweet(self, tweetId):
        payload = {"tweet_id": tweetId}

        response = self.oauth.post(
            "https://api.twitter.com/2/users/{}/likes".format(id), json=payload
        )
        return response

    def read_mentions(self, last_read=config.lastID):

        response = self.oauth.get(
            "https://api.twitter.com/2/users/1517829484505796609/mentions?since_id={}".format(last_read)
        )
        # to read response text: response.json()['data'][n]['id' or 'text']
        return response


# api = tweetAPI(consumer_key, consumer_secret)
# response = api.read_mentions()

# if response.status_code != 200 and response.status_code != 201:
#     raise Exception(
#         "Request returned an error: {} {}".format(response.status_code, response.text)
#     )

# print("Response code: {}".format(response.status_code))


import json
import tweepy
from os import environ

APIKEY = environ['Consumer_Key']
APISECRET = environ['Consumer_Secret']
OAUTHTOKEN = environ['Access_Key']
OAUTHTOKENSECRET = environ['Access_Secret']

class MyStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        self.me = api.me()

    def on_status(self, tweet):
        tweetInfo = json.loads(json.dumps(tweet._json))

        # Duplicate prevention on retweet of original tweet
        if 'retweeted_status' in tweetInfo:
            return

        # BLACC Publicize message
        replyContent = "We're BLACC - The Black Coder Community, a safe space for black people to exchange knowledge and be exposed to new technologies. If you’re looking to join a community exemplifying Black excellence and pushing the needle within tech, click the link below! blacc.xyz/discord"

        # Reply to the tweet
        api.update_status(status=replyContent, in_reply_to_status_id=tweetInfo['id'],
                          auto_populate_reply_metadata=True)
        # Like the tweet
        if not tweet.favorited:
            try:
                tweet.favorite()
            except Exception as e:
                print("Error: " + str(e))

        # Retweet the tweet
        if not tweet.retweeted:
            # Retweet, since we have not retweeted it yet
            try:
                tweet.retweet()
            except Exception as e:
                print("Error: " + str(e))
    def on_error(self, status):
        if status == 420:
            print("Error detected: " + str(status) + "\nClosing and reconnecting the Stream...")
            return False


# Authenticate to Twitter
auth = tweepy.OAuthHandler(APIKEY,APISECRET)
auth.set_access_token(OAUTHTOKEN,OAUTHTOKENSECRET)

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True)
tweets_listener = MyStreamListener(api)
stream = tweepy.Stream(api.auth, tweets_listener)
stream.filter(track=["#blacktechtwitter","#blackintech","#blackcoders","#blacktechpipeline","#blackdesigners","#blackwomenintech"],is_async=True)

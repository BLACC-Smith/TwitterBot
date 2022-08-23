import json
import tweepy
from time import *
from os import environ
from profanity_check import predict

consumer_key = environ['Consumer_Key']
consumer_secret = environ['Consumer_Secret']
access_token = environ['Access_Key']
access_token_secret = environ['Access_Secret']
moderator_id = environ['moderator_id']

class MyStreamClient(tweepy.Stream):

    def on_status(self, tweet):
        tweetInfo = json.loads(json.dumps(tweet._json))
        
        ## Guard clause for retweets
        if 'retweeted_status' in tweetInfo or tweetInfo['is_quote_status']:
            return
        
        ## Guard clause for possibly sensitive tweets
        if 'possibly_sensitive' in tweetInfo and tweetInfo['possibly_sensitive']:
            return
        
        ## Guard clause for tweets with more than 3 hashtags
        if len(tweetInfo['entities']['hashtags']) > 3:
            print("Tweet with more than 3 hashtags detected. Ignoring...")
            return

        ## Guard clause for extended tweets with more than 5 hashtags
        if 'extended_tweet' in tweetInfo and len(tweetInfo['extended_tweet']['entities']['hashtags']) > 5:
            print("Extended tweet with more than 5 hashtags detected. Ignoring...")
            return

        predict_score = predict([tweetInfo['text']])
        if predict_score:
            message = 'Detected a sensitive tweet here: https://twitter.com/twitter/statuses/' + str(tweetInfo['id_str'])
            api.send_direct_message(recipient_id=moderator_id, text=message)
            return

        ## Like the tweet
        if not tweet.favorited:
            try:
                api.create_favorite(id=tweetInfo['id'])
            except Exception as e:
                print("Error liking tweet because: " + str(e))

        ## Retweet the tweet
        if not tweet.retweeted:
            try:
                api.retweet(id=tweetInfo['id'])
            except Exception as e:
                print("Error retweeting tweet because: " + str(e))

    def on_error(self, status):
        if status == 420:
            print("Error detected: " + str(status) + "\nClosing and reconnecting the Stream...")
            # Wait 15 min before reconnecting
            sleep(900)
            return False
        else:
            print("Error detected: " + str(status))

auth = tweepy.OAuthHandler(consumer_key, consumer_secret, access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

stream = MyStreamClient(consumer_key, consumer_secret, access_token, access_token_secret)
stream.filter(track=["#blacktechtwitter"], filter_level='low')

import tweepy
import server.config

# retrieve twitter keys
consumer_key = config.C_KEY
consumer_secret = config.C_SECRET
access_token = config.A_T
access_token_secret = config.A_T_S

# set twitter api keys
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# post graph on twitter and get id
def post_graph(tweet_content):
    id = api.update_status_with_media(tweet_content,"tweettest.png").id
    api.create_favorite(id)
def get_tweets():

    # Import the necessary package to process data in JSON format
    try:
        import json
    except ImportError:
        import simplejson as json

    # Import the necessary methods from "twitter" library
    from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

    # Variables that contains the user credentials to access Twitter API
    ACCESS_TOKEN = '943242967564849154-j7MLiN1FNGEVgxmArd6eA0CCgo0iyLM'
    ACCESS_SECRET = 'tkm0nYc3K4uqJCQzBK3mNL4ORTX6Hdbht7jiVhnPz0nin'
    CONSUMER_KEY = 'JVYxUPrd1TXkAX1sebUgSloiy'
    CONSUMER_SECRET = '9JBmVPK44Mo1wSgbpyZTRa6pIKDgB4HVuSY4C5Bi8S0OsSmR6F'

    oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    # Initiate the connection to Twitter Streaming API
    twitter_stream = TwitterStream(auth=oauth)
    # Get a sample of the public data following through Twitter
    iterator = twitter_stream.statuses.filter(track='China')

    tweets = []
    tweet_count = 20
    for item in iterator:
        tweet_count -= 1
        # print(tweet_count)
        p = json.dumps(item)
        if tweet_count < 0:
            break

        try:
            tweet = json.loads(p)
            # print(tweet)
            if 'text' in tweet:  # only messages contains 'text' field is a tweet
                tweets.append(tweet)

        except:
            # read in a line is not in JSON format (sometimes error occured)
            continue
    # print(tweets)
    return tweets

if __name__ == "__main__":
    get_tweets()

    # Print each tweet in the stream to the screen
    # Here we set it to stop after getting 1000 tweets.
    # You don't have to set it to stop, but can continue running
    # the Twitter API to collect data for days or even longer.
    # tweet_count = 20
    # for tweet in iterator:
    #     tweet_count -= 1
    #     # Twitter Python Tool wraps the data returned by Twitter
    #     # as a TwitterDictResponse object.
    #     # We convert it back to the JSON format to print/score
    #     print json.dumps(tweet)
    #
    #     # The command below will do pretty printing for JSON data, try it out
    #     # print json.dumps(tweet, indent=4)
    #
    #     if tweet_count <= 0:
    #         break
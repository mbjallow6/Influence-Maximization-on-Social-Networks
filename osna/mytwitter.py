"""
Wrapper for Twitter API.
"""
from itertools import cycle
import json
import requests
import sys
import time
import traceback
from TwitterAPI import TwitterAPI
from collections import Counter

RATE_LIMIT_CODES = set([88, 130, 420, 429])

credential = '{"consumer_key": "cqECMZAl3gGUvFGeQDoJrw0Y9", "consumer_secret": "EUh3NDcCmVlnlvPUXiz5mXJXbQvEboD20qqPfo9gPPOhR72zSU", "access_token": "1059539800078868482-X58VyPiTww4aRFfmRvlpvtsszKhixQ", "token_secret": "J25R79B9kWSV3YcDfenVeh4gjgJpGVkI55bfFFPh3ClnR"}'

class Twitter:
    def __init__(self):
        """
        Params:
            credential_file...list of JSON objects containing the four 
            required tokens: consumer_key, consumer_secret, access_token, access_secret
        """
        self.credentials = [json.loads(credential)]
        self.credential_cycler = cycle(self.credentials)
        self.reinit_api()

    def reinit_api(self):
        creds = next(self.credential_cycler)
        sys.stderr.write('switching creds to %s\n' % creds['consumer_key'])
        self.twapi = TwitterAPI(creds['consumer_key'],
                                    creds['consumer_secret'],
                                    creds['access_token'],
                                    creds['token_secret'])
    def request(self, endpoint, params):
        while True:
            try:
                response = self.twapi.request(endpoint, params)
                if response.status_code in RATE_LIMIT_CODES:
                    for _ in range(len(self.credentials)-1):
                        self.reinit_api()
                        response = self.twapi.request(endpoint, params)
                        if response.status_code not in RATE_LIMIT_CODES:
                            return response
                    sys.stderr.write('sleeping for 15 minutes...\n')
                    time.sleep(910) # sleep for 15 minutes # FIXME: read the required wait time.
                    return self.request(endpoint, params)
                else:
                    return response
            except requests.exceptions.Timeout:
             # handle requests.exceptions.ConnectionError Read timed out.
                print("Timeout occurred. Retrying...")
                time.sleep(5)
                self.reinit_api()
                
    def _get_followers(self, identifier_field, identifier, limit=1e10):
        return self._paged_request('followers/ids',
                                    {identifier_field: identifier,
                                    'count': 5000,
                                    'stringify_ids': True},
                                    limit)
    
    def _get_users(self, identifier_field, identifier, limit=1e10):
        request = self.request('users/lookup', {identifier_field: identifier})
        #request = robust_request(twitter, "users/lookup" , {'screen_name': screen_names})
        users = [ r for r in request]
        #users = [{'id': r['id'], 'name': r['name'], 'screen_name' : r['screen_name'],  'followers_count': r['followers_count'], 'friends_count': r['friends_count'], 'statuses_count' : r['statuses_count']} for r in request]
        return users
    
    def _get_friends(self, identifier_field, identifier, limit=1e10):
        return self._paged_request('friends/ids', {identifier_field: identifier, 'count': 5000, 'stringify_ids': True}, limit)
    
    def add_followers(self, users):
        for u in users:
            temp = self._get_followers('screen_name', u['screen_name'], 5000)
            u.update({'followers': temp})
            
    def _paged_request(self, endpoint, params, limit):
        results = []
        cursor = -1
        while len(results) <= limit:
            try:
                response = self.request(endpoint, params)
                print(response)
                if response.status_code != 200: 
                    sys.stderr.write('Skipping bad request: %s\n' % response.text)
                    return results
                else:
                    result = json.loads(response.text)
                    print(result['next_cursor'])
                    items = [r for r in response]
                    if len(items) == 0:
                        return results
                    else:
                        sys.stderr.write('fetched %d more results for %s\n' % 
                            (len(items), params['screen_name'] if 'screen_name' in params else params['user_id']))
                        time.sleep(1)
                        results.extend(items)
                    params['cursor'] = result['next_cursor']
            except Exception as e:
                sys.stderr.write('Error: %s\nskipping...\n' % e)
                sys.stderr.write(traceback.format_exc())
                return results
        return results 
    
    def _get_tweets(self, identifier_field, identifier, limit=1e10):
        max_id = None
        tweets = []
        while len(tweets) < limit:
            try:
                params = {identifier_field: identifier, 'count': 200,
                            'max_id': max_id, 'tweet_mode': 'extended', 'trim_user': 0}
                if max_id:
                    params['max_id'] = max_id
                response = self.request('statuses/user_timeline', params)
                if response.status_code == 200:  # success
                    items = [t for t in response]
                    if len(items) > 0:
                        sys.stderr.write('fetched %d more tweets for %s\n' % (len(items), identifier))
                        tweets.extend(items)
                    else:
                        return tweets
                    max_id = min(t['id'] for t in response) - 1
                else:
                    sys.stderr.write('Skipping bad user: %s\n' % response.text)
                    return tweets
            except Exception as e:
                sys.stderr.write('Error: %s\nskipping...\n' % e)
                sys.stderr.write(traceback.format_exc() + '\n')
                return tweets
        #return tweets 
        res = [(r['id'], r['retweet_count']) for r in tweets]
        sorted_res = sorted(res, key = lambda x: -x[1])
        tweets = sorted_res[:25] #top 25 tweets
        return tweets
    
    def _add_tweets(self, users):
        for u in users:
            temp = self._get_tweets('screen_name', u['screen_name'], 200)
            u.update({'tweets': temp})
            
            
    def get_retweet_ids(self, identifier_field, identifier, limit=1e10):
        retweets = []
        cursor = -1
        while len(retweets) <= limit:
            params = {identifier_field: identifier}
            response = self.request('statuses/retweeters/ids', params)
            if response.status_code != 200: 
                sys.stderr.write('Skipping bad request: %s\n' % response.text)
                return results
            else:
                result = json.loads(response.text)
                items = [r for r in response]
                if len(items) == 0:
                    return retweets
                else:
                    sys.stderr.write('fetched %d more results for %s\n' % 
                    (len(items), params['screen_name'] if 'screen_name' in params else params['id']))
                    time.sleep(1)
                    retweets.extend(items)
                params['cursor'] = result['next_cursor']
                
                
        return retweets  

    def add_retweet_ids(self, users):
        for u in users:
            result = []
            for tweets in u['tweets']:
                temp = self.get_retweet_ids('id', tweets[0],5)
                result.extend(temp)
            counter_retweet = Counter(result)
            u.update({'retweet_counts': counter_retweet})     
                
    def influence_factor(self, users):
        influence_factor = {}
        total_tweets_author = len(users['tweets'])
        #print(users['retweet_counts'])
        for keys in users['retweet_counts']:
            retweet_by_follower = users['retweet_counts'][keys]
            influence_factor[keys] = (retweet_by_follower / total_tweets_author)
            
        users.update({'influence_factor': influence_factor})
        
    def add_influence_factor(self, users):
        for u in users:
            temp = self.influence_factor(u)
            
            
    def get_retweet_followers(self, json_filename):    
        with open(json_filename) as filein:
            input_json = json.load(filein)
        
        retweet_followers_list = []
        for retweet_id in input_json:
            for followers_id in retweet_id['retweet_counts']:
                if retweet_id['retweet_counts'][followers_id] > 1:
                    retweet_followers_list.append(followers_id)
                
        return retweet_followers_list

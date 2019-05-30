from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404
from claims.models import Claim
from claims.views import view_home, return_get_request_to_user
from comments.views import is_valid_url
from logger.views import save_log_message
from tweets.models import Tweet
from datetime import datetime
from django.utils import timezone
import json
import csv


# This function takes care of a request to add a new tweet to a claim in the website
def add_tweet(tweet_info):
    valid_tweet, err_msg = check_if_tweet_is_valid(tweet_info)
    if not valid_tweet:
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    build_tweet(tweet_info['claim_id'],
                tweet_info['tweet_link'])


# This function adds a new tweet to a claim in the website
def build_tweet(claim_id, tweet_link):
    tweet = Tweet(
        claim_id=claim_id,
        tweet_link=tweet_link,
    )
    tweet.save()


# This function checks if a given tweet is valid, i.e. the tweet has all the fields with the correct format.
# The function returns true in case the tweet is valid, otherwise false and an error
def check_if_tweet_is_valid(tweet_info):
    err = ''
    if 'claim_id' not in tweet_info or not tweet_info['claim_id']:
        err += 'Missing value for claim id'
    elif 'tweet_link' not in tweet_info or not tweet_info['tweet_link']:
        err += 'Missing value for tweet link'
    elif not is_valid_url(tweet_info['tweet_link']):
        err += 'Invalid value for tweet link'
    elif len(Claim.objects.filter(id=tweet_info['claim_id'])) == 0:
        err += 'Claim ' + str(tweet_info['claim_id']) + 'does not exist'
    if len(err) > 0:
        return False, err
    return True, err


# This function deletes a tweet from the website
def delete_tweet(request):
    if not request.user.is_superuser or request.method != "POST":
        raise PermissionDenied
    from claims.views import view_claim
    valid_delete_tweet, err_msg = check_if_delete_tweet_is_valid(request)
    if not valid_delete_tweet:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a tweet. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    tweet = get_object_or_404(Tweet, id=request.POST.get('tweet_id'))
    claim_id = tweet.claim_id
    Tweet.objects.filter(id=request.POST.get('tweet_id')).delete()
    save_log_message(request.user.id, request.user.username,
                     'Deleting a tweet with id ' + str(request.POST.get('tweet_id')), True)
    return view_claim(return_get_request_to_user(request.user), claim_id)


# This function checks if the given fields for deleting a tweet are valid,
# i.e. the request has all the fields with the correct format.
# The function returns true in case the given fields are valid, otherwise false and an error
def check_if_delete_tweet_is_valid(request):
    err = ''
    if not request.POST.get('tweet_id'):
        err += 'Missing value for tweet id'
    elif len(Tweet.objects.filter(id=request.POST.get('tweet_id'))) == 0:
        err += 'Tweet with id ' + str(request.user.id) + ' does not exist'
    if len(err) > 0:
        return False, err
    return True, err


# This function returns a csv which contains all the details of the tweets in the website
def export_to_csv(request):
    if not request.user.is_superuser or request.method != "POST":
        save_log_message(request.user.id, request.user.username,
                         'Exporting website tweets to a csv. Error: user does not have permissions')
        raise PermissionDenied
    csv_fields = request.POST.dict()
    valid_csv_fields, err_msg = check_if_csv_fields_are_valid(csv_fields)
    if not valid_csv_fields:
        save_log_message(request.user.id, request.user.username,
                         'Exporting website tweets to a csv. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    fields_to_export = request.POST.getlist('fields_to_export[]')
    date_start = datetime.strptime(csv_fields['date_start'], '%d/%m/%Y').date()
    date_end = datetime.strptime(csv_fields['date_end'], '%d/%m/%Y').date()
    valid_fields_list, err_msg = check_if_fields_list_valid(fields_to_export)
    if not valid_fields_list:
        save_log_message(request.user.id, request.user.username,
                         'Exporting website tweets to a csv. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    df_tweets = create_df_for_tweets(fields_to_export, date_start, date_end)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tweets.csv"'
    writer = csv.writer(response)
    writer.writerow(fields_to_export)
    for index, row in df_tweets.iterrows():
        tweet_info = []
        for col in df_tweets:
            tweet_info.append(row[col])
        writer.writerow(tweet_info)
    save_log_message(request.user.id, request.user.username,
                     'Exporting website tweets to a csv', True)
    return response


# This function checks if given csv fields are valid,
# i.e. the csv fields have all the fields with the correct format.
# The function returns true in case csv fields are valid, otherwise false and an error
def check_if_csv_fields_are_valid(csv_fields):
    from comments.views import convert_date_format
    err = ''
    if 'fields_to_export[]' not in csv_fields:
        err += 'Missing values for fields'
    elif 'date_start' not in csv_fields:
        err += 'Missing value for date start'
    elif 'date_end' not in csv_fields:
        err += 'Missing value for date end'
    else:
        err = convert_date_format(csv_fields, 'date_start')
        if len(err) == 0:
            err = convert_date_format(csv_fields, 'date_end')
    if len(err) > 0:
        return False, err
    return True, err


# This function checks if exported fields are valid.
# The function returns true in case they are valid, otherwise false and an error
def check_if_fields_list_valid(fields_to_export):
    err = ''
    valid_fields_to_export = ["Claim", "Tweet Link"]
    for field in fields_to_export:
        if field not in valid_fields_to_export:
            err += 'Field ' + str(field) + ' is not valid'
            return False, err
    return True, ''


# This function creates a df which contains all the details of the tweets in the website
def create_df_for_tweets(fields_to_export, date_start, date_end):
    import pandas as pd
    df_tweets = pd.DataFrame(columns=['Claim Id', 'Claim', 'Tweet Link', 'Date'])
    claims_ids, claims, tweets_links, dates = ([] for i in range(4))
    for tweet in Tweet.objects.all():
        claims_ids.append(tweet.claim.id)
        claims.append(tweet.claim.claim)
        tweets_links.append(tweet.tweet_link)
        dates.append(tweet.timestamp.date())
    df_tweets['Claim Id'] = claims_ids
    df_tweets['Claim'] = claims
    df_tweets['Tweet Link'] = tweets_links
    df_tweets['Date'] = dates
    df_tweets = df_tweets[(df_tweets['Date'] >= date_start) &
                          (df_tweets['Date'] <= date_end)]
    fields_to_export.insert(0, 'Claim Id')
    df_tweets = df_tweets[fields_to_export]
    return df_tweets


# This function return a HTML page for exporting website tweets to a csv file
def export_tweets_page(request):
    if not request.user.is_superuser or request.method != 'GET':
        raise PermissionDenied
    return render(request, 'tweets/export_tweets_page.html')


# This function saves all the user's tweets (from the request) in the system
def download_tweets_for_claims(request):
    if not request.user.is_authenticated:  # TAP user
        if not request.POST.get('username') or not request.POST.get('password') or not \
                authenticate(request, username=request.POST.get('username'), password=request.POST.get('password')):
            raise PermissionDenied
        request.user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
    if not request.user.is_superuser or request.method != "POST" or 'csv_file' not in request.FILES:
        raise PermissionDenied
    tweets = request.FILES['csv_file'].read().decode('utf-8-sig')
    if [header.lower().strip() for header in tweets.split('\n')[0].split(',')] != \
            ['claim id', 'tweet link']:
        raise Http404("Error - invalid header file")
    for tweet in tweets.split('\n')[1:]:
        if tweet:
            tweet_fields = tweet.split(',')
            claim = get_object_or_404(Claim, id=tweet_fields[0])
            if claim:
                build_tweet(claim.id, tweet_fields[1])
                save_log_message(request.user.id, request.user.username, 'Adding a new tweet', True)
    return view_home(return_get_request_to_user(request.user))


# This function checks for latest tweets relating to a given claim
def check_tweets_for_claim_in_twitter(request):
    import tweepy
    from tweepy import OAuthHandler
    from FactCheckingAggregation import settings
    from claims.views import view_claim, return_get_request_to_user
    if request.method != 'POST':
        raise PermissionDenied
    claim_info = request.POST.copy()
    valid_claim, err_msg = check_claim_before_extracting_tweets(claim_info)
    if not valid_claim:
        save_log_message(request.user.id, request.user.username,
                         'Extracting tweets for a claim. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    tweets = Tweet.objects.filter(claim_id=claim_info['claim_id']).order_by('-id')
    if len(tweets) == 0 or (timezone.now() - tweets.first().timestamp).days > 1:
        claim = Claim.objects.filter(id=claim_info['claim_id']).first()
        if not claim.tags:
            keywords = ' AND '.join(claim.claim.split())
        else:
            keywords = ' AND '.join(claim.tags.split(','))
        auth = OAuthHandler(settings.twitter_consumer_key, settings.twitter_consumer_secret)
        auth.set_access_token(settings.twitter_access_token, settings.twitter_access_secret)
        api = tweepy.API(auth)
        try:
            tweets = api.search(q=keywords,
                                count=10,
                                result_type='recent',
                                lang="en")
            if len(tweets) > 0:
                for tweet in tweets:
                    tweet_link = 'https://twitter.com/{}/status/{}'.format(tweet.user.screen_name, tweet.id)
                    if len(Tweet.objects.filter(tweet_link=tweet_link)) == 0:
                        build_tweet(claim.id, tweet_link)
                save_log_message(request.user.id, request.user.username,
                                 'Extracting tweets for a claim with id ' + str(claim.id), True)
                return view_claim(return_get_request_to_user(request.user), claim.id)
            err_msg = 'No tweets found according to claim\'s tags (keywords):\n' + claim.tags
        except tweepy.TweepError as e:
            err_msg = 'Can\'t search for latest tweets right now. Please try again later.'
    else:
        err_msg = 'Can\'t search for latest tweets right now. Please try again later.'
    return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)


# def get_tweets_for_claim(claim_id):
#     from tweets.models import Tweet
#     from users.models import User
#     tweets = Tweet.objects.filter(claim_id=claim_id).order_by('-id')
#     if len(tweets) == 0 or (timezone.now() - tweets.first().timestamp).days > 1:
#         request = HttpRequest()
#         request.user = User.objects.filter(is_superuser=True).order_by('+id').first()
#         request.method = 'POST'
#         request.POST['claim_id'] = claim_id
#         check_tweets_for_claim_in_twitter(request)
#     return Tweet.objects.filter(claim_id=claim_id).order_by('-id')


# This function checks if the given fields for extracting tweets for a claim are valid,
# i.e. the fields are with the correct format.
# The function returns true in case the fields are valid, otherwise false and an error
def check_claim_before_extracting_tweets(claim_info):
    err = ''
    if 'claim_id' not in claim_info or not claim_info['claim_id']:
        err += 'Missing value for claim id'
    elif len(Claim.objects.filter(id=claim_info['claim_id'])) == 0:
        err += 'Claim ' + str(claim_info['claim_id']) + ' does not exist'
    if len(err) > 0:
        return False, err
    return True, err

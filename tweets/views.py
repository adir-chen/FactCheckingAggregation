from django.contrib.auth import authenticate
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from claims.models import Claim
from claims.views import view_home, view_claim, is_english_input, return_get_request_to_user
from logger.views import save_log_message
from tweets.models import Tweet
from datetime import datetime
from users.views import check_if_user_exists_by_user_id
import csv


# This function takes care of a request to add a new tweet to a claim in the website
def add_tweet(request):
    if not request.user.is_authenticated or request.method != "POST":
        raise Http404("Permission denied")
    tweet_info = request.POST.copy()
    tweet_info['user_id'] = request.user.id
    tweet_info['is_superuser'] = request.user.is_superuser
    valid_tweet, err_msg = check_if_tweet_is_valid(tweet_info)
    if not valid_tweet:
        save_log_message(request.user.id, request.user.username,
                         'Adding a new tweet on claim with id ' +
                         str(request.POST.get("claim_id")) + '. Error: ' + err_msg)
        raise Exception(err_msg)
    build_tweet(tweet_info['claim_id'],
                tweet_info['user_id'],
                tweet_info['tweet_link'],
                tweet_info['author'],
                int(tweet_info['author_rank']))
    save_log_message(request.user.id, request.user.username,
                     'Adding a new tweet on claim with id ' + str(request.POST.get("claim_id")), True)
    return view_claim(return_get_request_to_user(request.user), request.POST.get('claim_id'))


# This function adds a new tweet to a claim in the website
def build_tweet(claim_id, user_id, tweet_link, author, author_rank):
    tweet = Tweet(
        claim_id=claim_id,
        user_id=user_id,
        tweet_link=tweet_link,
        author=author,
        author_rank=author_rank
    )
    tweet.save()


# This function checks if a given tweet is valid, i.e. the tweet has all the fields with the correct format.
# The function returns true in case the tweet is valid, otherwise false and an error
def check_if_tweet_is_valid(tweet_info):
    err = ''
    if 'claim_id' not in tweet_info or not tweet_info['claim_id']:
        err += 'Missing value for claim id'
    elif 'user_id' not in tweet_info or not tweet_info['user_id']:
        err += 'Missing value for user id'
    elif 'is_superuser' not in tweet_info:
        err += 'Missing value for user type'
    elif 'tweet_link' not in tweet_info or not tweet_info['tweet_link']:
        err += 'Missing value for tweet link'
    elif 'author' not in tweet_info or not tweet_info['author']:
        err += 'Missing value for author'
    elif 'author_rank' not in tweet_info or not tweet_info['author_rank']:
        err += 'Missing value for author rank'
    elif not tweet_info['author_rank'].isdigit():
        err += 'Incorrect format for author rank (integer)'
    elif not (1 <= int(tweet_info['author_rank']) <= 100):
        err += 'Author rank should be between 1 - 100'
    elif len(Claim.objects.filter(id=tweet_info['claim_id'])) == 0:
        err += 'Claim ' + str(tweet_info['claim_id']) + 'does not exist'
    elif not check_if_user_exists_by_user_id(tweet_info['user_id']):
        err += 'User with id ' + str(tweet_info['user_id']) + ' does not exist'
    elif not tweet_info['is_superuser'] and len(Tweet.objects.filter(claim_id=tweet_info['claim_id'], user_id=tweet_info['user_id'])) > 0:
        err += 'You can only tweet once on a claim'
    elif not is_english_input(tweet_info['author']):
        err += 'Input should be in the English language'
    if len(err) > 0:
        return False, err
    return True, err


# This function edits a tweet in the website
def edit_tweet(request):
    if not request.user.is_authenticated or request.method != "POST":
        raise Http404("Permission denied")
    new_tweet_fields = request.POST.dict()
    new_tweet_fields['user_id'] = request.user.id
    new_tweet_fields['is_superuser'] = request.user.is_superuser
    valid_new_tweet, err_msg = check_tweet_new_fields(new_tweet_fields)
    if not valid_new_tweet:
        save_log_message(request.user.id, request.user.username,
                         'Editing a tweet with id ' + str(request.POST.get('tweet_id')) +
                         '. Error: ' + err_msg)
        raise Exception(err_msg)
    Tweet.objects.filter(id=new_tweet_fields['tweet_id']).update(
        tweet_link=new_tweet_fields['tweet_link'],
        author=new_tweet_fields['author'],
        author_rank=new_tweet_fields['author_rank'])
    claim_id = Tweet.objects.filter(id=new_tweet_fields['tweet_id']).first().claim_id
    save_log_message(request.user.id, request.user.username,
                     'Editing a tweet with id ' + str(request.POST.get('tweet_id')), True)
    return view_claim(return_get_request_to_user(request.user), claim_id)


# This function checks if the given new fields for a tweet are valid,
# i.e. the tweet has all the fields with the correct format.
# The function returns true in case the tweet's new fields are valid, otherwise false and an error
def check_tweet_new_fields(new_tweet_fields):
    err = ''
    max_minutes_to_edit_tweet = 5
    # if 'label' not in new_tweet_fields or not new_tweet_fields['label']:
    #     new_tweet_fields['label'] = ''
    if 'user_id' not in new_tweet_fields or not new_tweet_fields['user_id']:
        err += 'Missing value for user id'
    elif 'is_superuser' not in new_tweet_fields:
        err += 'Missing value for user type'
    elif 'tweet_id' not in new_tweet_fields or not new_tweet_fields['tweet_id']:
        err += 'Missing value for tweet id'
    elif 'tweet_link' not in new_tweet_fields or not new_tweet_fields['tweet_link']:
        err += 'Missing value for tweet link'
    elif 'author' not in new_tweet_fields or not new_tweet_fields['author']:
        err += 'Missing value for tweet author'
    elif 'author_rank' not in new_tweet_fields or not new_tweet_fields['author_rank']:
        err += 'Missing value for author rank'
    elif not new_tweet_fields['author_rank'].isdigit():
        err += 'Incorrect format for author rank (integer)'
    elif not (1 <= int(new_tweet_fields['author_rank']) <= 100):
        err += 'Author rank should be between 1 - 100'
    elif not check_if_user_exists_by_user_id(new_tweet_fields['user_id']):
        err += 'User with id ' + str(new_tweet_fields['user_id']) + ' does not exist'
    elif len(Tweet.objects.filter(id=new_tweet_fields['tweet_id'])) == 0:
        err += 'Tweet with id ' + str(new_tweet_fields['tweet_id']) + ' does not exist'
    elif (not new_tweet_fields['is_superuser']) and len(Tweet.objects.filter(id=new_tweet_fields['tweet_id'], user_id=new_tweet_fields['user_id'])) == 0:
        err += 'Tweet with id ' + str(new_tweet_fields['tweet_id']) + ' does not belong to user with id ' + \
               str(new_tweet_fields['user_id'])
    elif (not new_tweet_fields['is_superuser']) and (timezone.now() - Tweet.objects.filter(id=new_tweet_fields['tweet_id']).first().timestamp).total_seconds() \
            / 60 > max_minutes_to_edit_tweet:
        err += 'You can no longer edit your tweet'
    elif not is_english_input(new_tweet_fields['author']):
        err += 'Input should be in the English language'
    if len(err) > 0:
        return False, err
    return True, err


# This function deletes a tweet from the website
def delete_tweet(request):
    if not request.user.is_authenticated or request.method != "POST":
        raise Http404("Permission denied")
    from claims.views import view_claim
    from users.views import update_reputation_for_user
    valid_delete_tweet, err_msg = check_if_delete_tweet_is_valid(request)
    if not valid_delete_tweet:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a tweet. Error: ' + err_msg)
        raise Exception(err_msg)
    tweet = get_object_or_404(Tweet, id=request.POST.get('tweet_id'))
    claim_id = tweet.claim_id
    update_reputation_for_user(tweet.user_id, False, tweet.up_votes.count())
    update_reputation_for_user(tweet.user_id, True, tweet.down_votes.count())
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
    elif not check_if_user_exists_by_user_id(request.user.id):
        err += 'User with id ' + str(request.user.id) + ' does not exist'
    elif not request.user.is_superuser and len(Tweet.objects.filter(id=request.POST.get('tweet_id'), user=request.user.id)) == 0:
        err += 'Tweet with id ' + str(request.POST.get('tweet_id')) + ' does not belong to user with id ' + \
               str(request.user.id)
    if len(err) > 0:
        return False, err
    return True, err


# This function increases a tweet's vote by 1
def up_vote(request):
    if not request.user.is_authenticated or request.method != "POST":
        raise Http404("Permission denied")
    from claims.views import view_claim
    from users.views import update_reputation_for_user
    vote_fields = request.POST.dict()
    vote_fields['user_id'] = request.user.id
    valid_vote, err_msg = check_if_vote_is_valid(vote_fields)
    if not valid_vote:
        save_log_message(request.user.id, request.user.username,
                         'Up voting a tweet. Error: ' + err_msg)
        raise Exception(err_msg)
    tweet = get_object_or_404(Tweet, id=request.POST.get('tweet_id'))
    if tweet.up_votes.filter(id=request.user.id).exists():
        tweet.up_votes.remove(request.user.id)
        update_reputation_for_user(tweet.user_id, False, 1)
    else:
        tweet.up_votes.add(request.user.id)
        update_reputation_for_user(tweet.user_id, True, 1)
        if tweet.down_votes.filter(id=request.user.id).exists():
            tweet.down_votes.remove(request.user.id)
            update_reputation_for_user(tweet.user_id, True, 1)
    save_log_message(request.user.id, request.user.username, 'Up voting a tweet with id '
                     + str(request.POST.get('tweet_id')), True)
    return view_claim(return_get_request_to_user(request.user), tweet.claim_id)


# This function decreases a tweet's vote by 1
def down_vote(request):
    if not request.user.is_authenticated or request.method != "POST":
        raise Http404("Permission denied")
    from claims.views import view_claim, return_get_request_to_user
    from users.views import update_reputation_for_user
    vote_fields = request.POST.dict()
    vote_fields['user_id'] = request.user.id
    valid_vote, err_msg = check_if_vote_is_valid(vote_fields)
    if not valid_vote:
        save_log_message(request.user.id, request.user.username,
                         'Down voting a tweet. Error: ' + err_msg)
        raise Exception(err_msg)
    tweet = get_object_or_404(Tweet, id=request.POST.get('tweet_id'))
    if tweet.down_votes.filter(id=request.user.id).exists():
        tweet.down_votes.remove(request.user.id)
        update_reputation_for_user(tweet.user_id, True, 1)
    else:
        tweet.down_votes.add(request.user.id)
        update_reputation_for_user(tweet.user_id, False, 1)
        if tweet.up_votes.filter(id=request.user.id).exists():
            tweet.up_votes.remove(request.user.id)
            update_reputation_for_user(tweet.user_id, False, 1)
    save_log_message(request.user.id, request.user.username,
                     'Down voting a tweet with id ' + str(request.POST.get('tweet_id')), True)
    return view_claim(return_get_request_to_user(request.user), tweet.claim_id)


# This function checks if a given vote for a tweet is valid, i.e. the vote has all the fields with the correct format.
# The function returns true in case the vote is valid, otherwise false and an error
def check_if_vote_is_valid(vote_fields):
    err = ''
    max_minutes_to_vote_tweet = 5
    if 'user_id' not in vote_fields or not vote_fields['user_id']:
        err += 'Missing value for user id'
    elif not check_if_user_exists_by_user_id(vote_fields['user_id']):
        err += 'User with id ' + str(vote_fields['user_id']) + ' does not exist'
    elif 'tweet_id' not in vote_fields or not vote_fields['tweet_id']:
        err += 'Missing value for tweet id'
    elif len(Tweet.objects.filter(id=vote_fields['tweet_id'])) == 0:
        err += 'Tweet with id ' + str(vote_fields['tweet_id']) + ' does not exist'
    elif (timezone.now() - Tweet.objects.filter(id=vote_fields['tweet_id']).first().timestamp).total_seconds() \
             / 60 <= max_minutes_to_vote_tweet:
        err += 'You can no vote this tweet yet. This tweet has just been added, ' \
               'therefore you will be able to vote on it in a few minutes.'
    if len(err) > 0:
        return False, err
    return True, err


# This function sets user's label (True, False or Unknown) to a tweet according to his claim
def set_user_label_to_tweet(request):
    if not request.user.is_authenticated or request.method != "POST":
        raise Http404("Permission denied")
    tweet_info = request.POST.dict()
    tweet_info['user_id'] = request.user.id
    tweet_info['is_superuser'] = request.user.is_superuser
    tweet_info['claim_id'] = Tweet.objects.filter(id=tweet_info['tweet_id']).first().claim_id
    valid_tweet_label, err_msg = check_if_tweet_label_is_valid(tweet_info)
    if not valid_tweet_label:
        save_log_message(request.user.id, request.user.username,
                         'Labeling a tweet on claim with id ' +
                         str(tweet_info['claim_id']) + '. Error: ' + err_msg)
        raise Exception(err_msg)
    Tweet.objects.filter(id=tweet_info['tweet_id']).update(label=tweet_info['label'])
    save_log_message(request.user.id, request.user.username,
                     'Labeling a tweet on claim with id ' + str(tweet_info['claim_id']), True)
    return view_claim(return_get_request_to_user(request.user), tweet_info['claim_id'])


# This function checks if a given label for a tweet is valid,
# i.e. the tweet's label has all the fields with the correct format.
# The function returns true in case the tweet's label is valid, otherwise false and an error
def check_if_tweet_label_is_valid(tweet_info):
    err = ''
    if 'claim_id' not in tweet_info or not tweet_info['claim_id']:
        err += 'Missing value for claim id'
    elif 'user_id' not in tweet_info or not tweet_info['user_id']:
        err += 'Missing value for user id'
    elif 'is_superuser' not in tweet_info:
        err += 'Missing value for user type'
    elif 'tweet_id' not in tweet_info or not tweet_info['tweet_id']:
        err += 'Missing value for tweet id'
    elif 'label' not in tweet_info or not tweet_info['label']:
        err += 'Missing value for label'
    elif len(Claim.objects.filter(id=tweet_info['claim_id'])) == 0:
        err += 'Claim ' + str(tweet_info['claim_id']) + 'does not exist'
    elif not check_if_user_exists_by_user_id(tweet_info['user_id']):
        err += 'User with id ' + str(tweet_info['user_id']) + ' does not exist'
    elif not tweet_info['is_superuser'] and len(Claim.objects.filter(id=tweet_info['claim_id'], user_id=tweet_info['user_id'])) == 0:
        err += 'Claim with id ' + str(tweet_info['claim_id']) + ' does not belong to user with id ' + str(tweet_info['user_id'])
    if len(err) > 0:
        return False, err
    return True, err


# This function returns a csv which contains all the details of the tweets in the website
def export_to_csv(request):
    if not request.user.is_superuser or request.method != "POST":
        save_log_message(request.user.id, request.user.username,
                         'Exporting website tweets to a csv. Error: user does not have permissions')
        raise Http404("Permission denied")
    csv_fields = request.POST.dict()
    valid_csv_fields, err_msg = check_if_csv_fields_are_valid(csv_fields)
    if not valid_csv_fields:
        save_log_message(request.user.id, request.user.username,
                         'Exporting website tweets to a csv. Error: ' + err_msg)
        raise Exception(err_msg)
    fields_to_export = request.POST.getlist('fields_to_export[]')
    date_start = datetime.strptime(csv_fields['date_start'], '%d/%m/%Y').date()
    date_end = datetime.strptime(csv_fields['date_end'], '%d/%m/%Y').date()
    valid_fields_list, err_msg = check_if_fields_list_valid(fields_to_export)
    if not valid_fields_list:
        save_log_message(request.user.id, request.user.username,
                         'Exporting website tweets to a csv. Error: ' + err_msg)
        raise Exception(err_msg)
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
    valid_fields_to_export = ["Claim", "Tweet Link", "Author", "Author Rank", "Label"]
    for field in fields_to_export:
        if field not in valid_fields_to_export:
            err += 'Field ' + str(field) + ' is not valid'
            return False, err
    return True, ''


# This function creates a df which contains all the details of the tweets in the website
def create_df_for_tweets(fields_to_export, date_start, date_end):
    import pandas as pd
    df_tweets = pd.DataFrame(columns=['User Id', 'Claim', 'Tweet Link', 'Author', 'Author Rank', 'Label'])
    users_ids, claims_ids, claims, tweets_links, authors, authors_ranks, labels, dates= ([] for i in range(8))
    for tweet in Tweet.objects.all():
        users_ids.append(tweet.user_id)
        claims_ids.append(tweet.claim.id)
        claims.append(tweet.claim.claim)
        tweets_links.append(tweet.tweet_link)
        authors.append(tweet.author)
        authors_ranks.append(tweet.author_rank)
        labels.append(tweet.label)
        dates.append(tweet.timestamp.date())
    df_tweets['User Id'] = users_ids
    df_tweets['Claim Id'] = claims_ids
    df_tweets['Claim'] = claims
    df_tweets['Tweet Link'] = tweets_links
    df_tweets['Author'] = authors
    df_tweets['Author Rank'] = authors_ranks
    df_tweets['Label'] = labels
    df_tweets['Date'] = dates
    df_tweets = df_tweets[(df_tweets['Date'] >= date_start) &
                          (df_tweets['Date'] <= date_end)]
    fields_to_export.insert(0, 'Claim Id')
    df_tweets = df_tweets[fields_to_export]
    return df_tweets


# This function return a HTML page for adding a new claim to the website
def export_tweets_page(request):
    if not request.user.is_authenticated or request.method != 'GET':
        raise Http404("Permission denied")
    return render(request, 'tweets/export_tweets_page.html')


# This function saves all the user's tweets (from the request) in the system
def download_tweets_for_claims(request):
    if not request.user.is_authenticated:  # TAP user
        if not request.POST.get('username') or not request.POST.get('password') or not \
                authenticate(request, username=request.POST.get('username'), password=request.POST.get('password')):
            raise Http404("Permission denied")
        request.user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
    if not request.user.is_superuser or request.method != "POST" or 'csv_file' not in request.FILES:
        raise Http404("Permission denied")
    tweets = request.FILES['csv_file'].read().decode('utf-8')
    if [header.lower().strip().replace(u'\ufeff', '') for header in tweets.split('\n')[0].split(',')] != \
            ['claim id', 'tweet link', 'author', 'author rank']:
        raise Http404("Permission denied")
    for tweet in tweets.split('\n')[1:]:
        if tweet:
            tweet_fields = tweet.split(',')
            claim = get_object_or_404(Claim, id=tweet_fields[0])
            if claim:
                build_tweet(claim.id, request.user.id, tweet_fields[1], tweet_fields[2], int(float(tweet_fields[3]) * 100))
    return view_home(return_get_request_to_user(request.user))
from django.contrib.auth import authenticate
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from claims.models import Claim
from logger.views import save_log_message
from tweets.models import Tweet
from users.views import check_if_user_exists_by_user_id


def download_tweets_page(request):
    return render(request, 'tweets/post_csv.html')


def download_tweets_for_claims(request):
    if not request.user.is_authenticated:  # TAP user
        if not request.POST.get('username') or not request.POST.get('password') or not \
                authenticate(request, username=request.POST.get('username'), password=request.POST.get('password')):
            raise Http404("Permission denied")
        request.user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
    if not request.user.is_superuser or request.method != "POST" or 'csv_file' not in request.FILES:
        raise Http404("Permission denied")
    tweets = request.FILES['csv_file'].read().decode('utf-8')
    for tweet in tweets.split('\n')[1:]:
        tweet_fields = tweet.split(',')
        claim = get_object_or_404(Claim, id=tweet_fields[0])
        if claim:
            build_tweet(claim.id, request.user.id, tweet_fields[1], tweet_fields[2], tweet_fields[3])


# This function adds a new tweet to a claim in the website
def build_tweet(claim_id, user_id, tweet_link, author, author_rank):
    tweet = Tweet(
        claim_id=claim_id,
        user_id=user_id,
        tweet_link=tweet_link,
        author=author,
        author_rank=author_rank * 100
    )
    tweet.save()


# This function increases a tweet's vote by 1
def up_vote(request):
    from claims.views import return_get_request_to_user
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
                     'Down voting a tweet with id ' + str(request.POST.get('comment_id')), True)
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


# This function deletes a tweet from the website
def delete_tweet(request):
    from claims.views import return_get_request_to_user
    if not request.user.is_authenticated or request.method != "POST":
        raise Http404("Permission denied")
    from claims.views import view_claim
    from users.views import update_reputation_for_user
    valid_delete_tweet, err_msg = check_if_delete_comment_is_valid(request)
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
def check_if_delete_comment_is_valid(request):
    err = ''
    if not request.POST.get('comment_id'):
        err += 'Missing value for claim id'
    elif len(Tweet.objects.filter(id=request.POST.get('tweet_id'))) == 0:
        err += 'Tweet with id ' + str(request.user.id) + ' does not exist'
    elif not check_if_user_exists_by_user_id(request.user.id):
        err += 'User with id ' + str(request.user.id) + ' does not exist'
    elif not request.user.is_superuser and len(Tweet.objects.filter(id=request.POST.get('tweet_id'), user=request.user.id)) == 0:
        err += 'Tweet with id ' + str(request.POST.get('comment_id')) + ' does not belong to user with id ' + \
               str(request.user.id)
    if len(err) > 0:
        return False, err
    return True, err

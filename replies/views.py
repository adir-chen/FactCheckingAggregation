from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from comments.models import Comment
from logger.views import save_log_message
from claims.views import view_claim, is_english_input, return_get_request_to_user
from replies.models import Reply
from users.views import check_if_user_exists_by_user_id
import json


# This function takes care of a request to add a new reply to a comment in the website
def add_reply(request):
    if not request.user.is_authenticated or request.method != "POST":
        raise PermissionDenied
    reply_info = request.POST.copy()
    reply_info['user_id'] = request.user.id
    reply_info['is_superuser'] = request.user.is_superuser
    valid_reply, err_msg = check_if_reply_is_valid(reply_info)
    if not valid_reply:
        save_log_message(request.user.id, request.user.username,
                         'Adding a new reply on comment. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    build_reply(reply_info['comment_id'],
                reply_info['user_id'],
                reply_info['content'])
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    save_log_message(request.user.id, request.user.username,
                     'Adding a new reply on comment with id ' + str(request.POST.get("comment_id")), True)
    return view_claim(return_get_request_to_user(request.user), comment.claim_id)


# This function adds a new reply to a comment in the website
def build_reply(comment_id, user_id, content):
    reply = Reply(
        comment_id=comment_id,
        user_id=user_id,
        content=content,
    )
    reply.save()


# This function checks if a given reply is valid, i.e. the reply has all the fields with the correct format.
# The function returns true in case the reply is valid, otherwise false and an error
def check_if_reply_is_valid(reply_info):
    max_replies = 5
    err = ''
    if 'comment_id' not in reply_info or not reply_info['comment_id']:
        err += 'Missing value for claim id'
    elif 'user_id' not in reply_info or not reply_info['user_id']:
        err += 'Missing value for user id'
    elif 'is_superuser' not in reply_info:
        err += 'Missing value for user type'
    elif 'content' not in reply_info or not reply_info['content']:
        err += 'Missing value for content'
    elif len(Comment.objects.filter(id=reply_info['comment_id'])) == 0:
        err += 'Comment ' + str(reply_info['comment_id']) + ' does not exist'
    elif not check_if_user_exists_by_user_id(reply_info['user_id']):
        err += 'User with id ' + str(reply_info['user_id']) + ' does not exist'
    elif (not reply_info['is_superuser']) and len(Reply.objects.filter(comment_id=reply_info['comment_id'],
                                                                       user_id=reply_info['user_id'])) >= max_replies:
        err += 'Maximum number of replies per comment is ' + str(max_replies)
    elif not is_english_input(reply_info['content']):
        err += 'Input should be in the English language'
    if len(err) > 0:
        return False, err
    return True, err


# This function edits a reply in the website
def edit_reply(request):
    if not request.user.is_authenticated or request.method != "POST":
        raise PermissionDenied
    new_reply_fields = request.POST.dict()
    new_reply_fields['user_id'] = request.user.id
    new_reply_fields['is_superuser'] = request.user.is_superuser
    valid_new_reply, err_msg = check_reply_new_fields(new_reply_fields)
    if not valid_new_reply:
        save_log_message(request.user.id, request.user.username,
                         'Editing a reply. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    Reply.objects.filter(id=new_reply_fields['reply_id']).update(
        content=new_reply_fields['reply_content'])
    claim_id = Reply.objects.filter(id=new_reply_fields['reply_id']).first().comment.claim_id
    save_log_message(request.user.id, request.user.username,
                     'Editing a reply with id ' + str(request.POST.get('reply_id')), True)
    return view_claim(return_get_request_to_user(request.user), claim_id)


# This function checks if the given new fields for a reply are valid,
# i.e. the reply has all the fields with the correct format.
# The function returns true in case the reply's new fields are valid, otherwise false and an error
def check_reply_new_fields(new_reply_fields):
    err = ''
    max_minutes_to_edit_reply = 10
    if 'user_id' not in new_reply_fields or not new_reply_fields['user_id']:
        err += 'Missing value for user id'
    elif 'is_superuser' not in new_reply_fields:
        err += 'Missing value for user type'
    elif 'reply_id' not in new_reply_fields or not new_reply_fields['reply_id']:
        err += 'Missing value for reply id'
    elif 'reply_content' not in new_reply_fields or not new_reply_fields['reply_content']:
        err += 'Missing value for reply content'
    elif not check_if_user_exists_by_user_id(new_reply_fields['user_id']):
        err += 'User with id ' + str(new_reply_fields['user_id']) + ' does not exist'
    elif len(Reply.objects.filter(id=new_reply_fields['reply_id'])) == 0:
        err += 'Reply with id ' + str(new_reply_fields['reply_id']) + ' does not exist'
    elif (not new_reply_fields['is_superuser']) and len(Reply.objects.filter(id=new_reply_fields['reply_id'],
                                                                             user_id=new_reply_fields['user_id'])) == 0:
        err += 'Reply with id ' + str(new_reply_fields['reply_id']) + ' does not belong to user with id ' + \
               str(new_reply_fields['user_id'])
    elif (not new_reply_fields['is_superuser']) and (timezone.now() - Reply.objects.filter(id=new_reply_fields['reply_id']).first().timestamp).total_seconds() \
            / 60 > max_minutes_to_edit_reply:
        err += 'You can no longer edit your reply'
    elif not is_english_input(new_reply_fields['reply_content']):
        err += 'Input should be in the English language'
    if len(err) > 0:
        return False, err
    return True, err


# This function deletes a reply from the website
def delete_reply(request):
    if not request.user.is_authenticated or request.method != "POST":
        raise PermissionDenied
    valid_delete_reply, err_msg = check_if_delete_reply_is_valid(request)
    if not valid_delete_reply:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a reply. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    comment = get_object_or_404(Comment, id=Reply.objects.filter(id=request.POST.get('reply_id')).first().comment_id)
    claim_id = comment.claim_id
    Reply.objects.filter(id=request.POST.get('reply_id')).delete()
    save_log_message(request.user.id, request.user.username,
                     'Deleting a reply with id ' + str(request.POST.get('reply_id')), True)
    return view_claim(return_get_request_to_user(request.user), claim_id)


# This function checks if the given fields for deleting a reply are valid,
# i.e. the request has all the fields with the correct format.
# The function returns true in case the given fields are valid, otherwise false and an error
def check_if_delete_reply_is_valid(request):
    err = ''
    if not request.POST.get('reply_id'):
        err += 'Missing value for reply id'
    elif len(Reply.objects.filter(id=request.POST.get('reply_id'))) == 0:
        err += 'Reply with id ' + str(request.user.id) + ' does not exist'
    elif not check_if_user_exists_by_user_id(request.user.id):
        err += 'User with id ' + str(request.user.id) + ' does not exist'
    elif not request.user.is_superuser and len(Reply.objects.filter(id=request.POST.get('reply_id'),
                                                                    user=request.user.id)) == 0:
        err += 'Reply with id ' + str(request.POST.get('reply_id')) + ' does not belong to user with id ' + \
               str(request.user.id)
    if len(err) > 0:
        return False, err
    return True, err


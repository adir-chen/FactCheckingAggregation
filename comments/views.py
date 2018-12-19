from comments.models import Comment


# add a new comment to a claim in the website.
def add_comment(claim_id, user_id, title, description, url, verdict_date, tags, label):
    tags_arr = tags.split(' ')
    new_tags = ''
    for tag in tags_arr:
        new_tags += tag + ', '
    comment = Comment(
        claim_id = claim_id,
        user_id = user_id,
        title = title,
        description = description,
        url = url,
        verdict_date = verdict_date,
        tags = new_tags,
        label = label,
        pos_votes = 0,
        neg_votes = 0
    )

    try:
        comment.save()
    except Exception as e:
        print('Adding new comment failed - ' + str(e))


def get_all_comments_for_user_id(user_id):
    Comment.objects.filter(user_id=user_id)


def get_all_comments_for_claim_id(claim_id):
    Comment.objects.filter(claim_id=claim_id)


def reset_comments():
    Comment.objects.all().delete()

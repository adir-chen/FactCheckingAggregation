import csv
from comments.models import Comment
from claims.models import Claim
from django.http import HttpResponse


# This function adds a new comment to a claim in the website
def add_comment(claim_id, user_id, title, description, url, verdict_date, tags, label):
    tags_arr = tags.split(' ')
    new_tags = ''
    for tag in tags_arr:
        new_tags += tag + ', '
    new_tags = new_tags[:-2]
    comment = Comment(
        claim_id=claim_id,
        user_id=user_id,
        title=title,
        description=description,
        url=url,
        verdict_date=verdict_date,
        tags=new_tags,
        label=label,
        pos_votes=0,
        neg_votes=0
    )
    comment.save()


# This function returns all the comments for a given user's id
# The function returns all the comments in case they are found, otherwise None
def get_all_comments_for_user_id(user_id):
    result = Comment.objects.filter(user_id=user_id)
    if len(result) > 0:
        return result
    return None


# This function returns all the comments for a given claim's id
# The function returns all the comments in case they are found, otherwise None
def get_all_comments_for_claim_id(claim_id):
    result = Comment.objects.filter(claim_id=claim_id)
    if len(result) > 0:
        return result
    return None


# The function deletes all the comments in the website
def reset_comments():
    Comment.objects.all().delete()


# This function returns the category for a given claim's id
# The function returns claim's category in case it is found, otherwise None
def get_category_for_claim(claim_id):
    result = Claim.objects.filter(id=claim_id)
    if len(result) > 0:
        return result[0].category
    return None


# This function returns a csv which contains all the details of the claims in the website
def export_to_csv():
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="claims.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Description', 'Url', 'Category', 'Verdict_Date', 'Tags', 'Label'])
    for comment in Comment.objects.all():
        writer.writerow([comment.title, comment.description, comment.url, get_category_for_claim(comment.claim_id),
                        comment.verdict_date, comment.tags, comment.label])
    return response

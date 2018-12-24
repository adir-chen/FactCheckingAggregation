import csv
from comments.models import Comment
from claims.models import Claim
from django.http import HttpResponse


# add a new comment to a claim in the website.
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


def get_all_comments_for_user_id(user_id):
    result = Comment.objects.filter(user_id=user_id)
    if len(result) > 0:
        return result
    return None


def get_all_comments_for_claim_id(claim_id):
    result = Comment.objects.filter(claim_id=claim_id)
    if len(result) > 0:
        return result
    return None


def reset_comments():
    Comment.objects.all().delete()


def get_category_for_claim(claim_id):
    result = Claim.objects.filter(id=claim_id)
    if len(result) > 0:
        return result[0].category
    return None


def export_to_csv():
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="claims.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Description', 'Url', 'Category', 'Verdict_Date', 'Tags', 'Label'])
    for comment in Comment.objects.all():
        writer.writerow([comment.title, comment.description, comment.url, get_category_for_claim(comment.claim_id),
                        comment.verdict_date, comment.tags, comment.label])
    return response

import csv
import pandas as pd
# from claims.views import get_category_for_claim
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
    return Comment.objects.filter(user_id=user_id)


def get_all_comments_for_claim_id(claim_id):
    return Comment.objects.filter(claim_id=claim_id)


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
    # df_claims_columns = ['Title', 'Description', 'Url', 'Category', 'Verdict_Date', 'Tags', 'Label']
    # df_claims = pd.DataFrame(columns=df_claims_columns)
    # title, description, url, category, verdict_date, tags, label = ([] for i in range(7))
    for comment in Comment.objects.all():
        writer.writerow([comment.title, comment.description, comment.url, get_category_for_claim(comment.claim_id),
                        comment.verdict_date, comment.tags, comment.label])

    #     title.append(comment.title)
    #     description.append(comment.description)
    #     url.append(comment.url)
    #     category.append(get_category_for_claim(comment.claim_id))
    #     verdict_date.append(comment.verdict_date)
    #     tags.append(comment.tags)
    #     label.append(comment.label)
    # df_claims['Title'] = title
    # df_claims['Description'] = description
    # df_claims['Url'] = url
    # df_claims['Category'] = category
    # df_claims['Verdict_Date'] = verdict_date
    # df_claims['Tags'] = tags
    # df_claims['Label'] = label
    # df_claims.to_csv('claims.csv')
    # return HttpResponse('string')
    return response
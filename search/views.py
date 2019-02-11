from django.shortcuts import render
from claims.models import Claim
from comments.models import Comment
from users.models import UsersImages


def search(request):
    keywords = request.GET.get('search_keywords')
    claim_objs = Claim.objects.filter(claim__icontains=keywords)
    result = {}
    for claim in claim_objs:
        comment_objs = Comment.objects.filter(claim_id=claim.id)
        users_imgs = []
        for comment in comment_objs:
            user_img = UsersImages.objects.filter(user_id=comment.user_id)
            if len(user_img) > 0:
                users_imgs.append(user_img[0].user_img)
        result[claim] = users_imgs
    return render(request, 'search/search.html', {'search_result': result})


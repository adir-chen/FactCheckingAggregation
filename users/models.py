from django.db import models
from django.contrib.auth.models import User
from django.contrib import auth


# This function returns the user image
def get_user_image(self):
    user_img = Users_Images.objects.filter(user=self)
    if len(user_img) == 0:
        user_img = Users_Images.objects.create(user=self)
    else:
        user_img = user_img.first()
    return user_img


def get_user_rep(self):
    user_rep = Users_Reputations.objects.filter(user=self)
    if len(user_rep) == 0:
        user_rep = Users_Reputations.objects.create(user=self)
    else:
        user_rep = user_rep.first()
    return user_rep


def get_scraper(self):
    scraper = Scrapers.objects.filter(scraper=self)
    if len(scraper) == 0:
        return None
    return scraper.first()


def get_notifications(self):
    from notifications.models import Notification
    return Notification.objects.filter(recipient=self)


def get_last_notifications(self):
    from notifications.models import Notification
    num_of_notifications = 5
    return Notification.objects.filter(recipient=self)[:num_of_notifications]


auth.models.User.add_to_class('get_user_image', get_user_image)
auth.models.User.add_to_class('get_user_rep', get_user_rep)
auth.models.User.add_to_class('get_scraper', get_scraper)
auth.models.User.add_to_class('get_notifications', get_notifications)


def upload_to(instance, filename):
    return "images/{}/{}".format(instance.user.id, filename)


class Users_Images(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_img = models.ImageField(upload_to=upload_to, blank=True)

    def image_url(self):
        if self.profile_img and hasattr(self.profile_img, 'url'):
            return self.profile_img.url
        else:
            return 'https://wtfact.ise.bgu.ac.il/media/profile_default_image.jpg'

    def __str__(self):
        return self.user.username


class Users_Reputations(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reputation = models.IntegerField(default=1)

    def get_reputation(self):
        import math
        return math.ceil(self.reputation / 20)

    def __str__(self):
        return self.user.username + ' - ' + str(self.reputation)


class Scrapers(models.Model):
    scraper_name = models.CharField(max_length=50)
    scraper = models.ForeignKey(User, on_delete=models.CASCADE)
    scraper_url = models.CharField(max_length=50)
    true_labels = models.TextField(default='true')
    false_labels = models.TextField(default='false')

    # This function returns all false labels of the given scraper
    def get_false_labels(self):
        false_labels = self.false_labels.split(',')
        if len(false_labels) == 1 and not false_labels[0]:  # without labels
            false_labels = []
        return false_labels

    # This function returns all true labels of the given scraper
    def get_true_labels(self):
        true_labels = self.true_labels.split(',')
        if len(true_labels) == 1 and not true_labels[0]:  # without labels
            true_labels = []
        return true_labels

    def __str__(self):
        return self.scraper_name

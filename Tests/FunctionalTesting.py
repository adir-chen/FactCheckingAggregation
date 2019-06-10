import datetime
import random
import time

from django.contrib.auth.models import User
from django.test import Client
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.keys import Keys
from claims.models import Claim
from comments.models import Comment
from replies.models import Reply
from tweets.models import Tweet
from django.test.utils import override_settings
from django.contrib.staticfiles.templatetags.staticfiles import static


def authenticated_browser(browser, client, live_server_url, user):
    client.force_login(user)
    browser.get(live_server_url)
    cookie = client.cookies['sessionid']
    browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
    browser.refresh()
    return browser


@override_settings(DEBUG=True)
class UITests(StaticLiveServerTestCase):

    def setUp(self):
        self.claim_img = self.live_server_url + static('claims/assets/images/claim_default_image.jpg')
        self.user1 = User.objects.create_user(username="User1", email='user1@gmail.com')
        self.user1.save()
        self.user2 = User.objects.create_user(username="User2", email='user2@gmail.com')
        self.user2.save()
        self.admin = User.objects.create_superuser(username='admin', password='password', email='admin@gmail.com')
        self.admin.save()
        self.claim_1 = Claim(user_id=self.user1.id,
                             claim='claim1',
                             category='category1',
                             tags="tag1,tag2",
                             authenticity_grade=0,
                             image_src=self.claim_img)
        self.claim_1.save()
        self.comment_1 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.claim_1.user_id,
                                 title='title1',
                                 description='description1',
                                 url='http://url1/',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                 system_label='True',
                                 tags='t1,t2')
        self.comment_1.save()
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() - datetime.timedelta(minutes=10))
        self.browser = webdriver.Chrome('Tests/chromedriver.exe')
        self.browser.implicitly_wait(10)
        self.client = Client()

    def tearDown(self):
        self.browser.close()

    def add_tweet(self, user_id):
        tweet_1 = Tweet(claim_id=self.claim_1.id,
                        tweet_link='http://url1/',)
        tweet_1.save()
        time.sleep(1)
        return tweet_1

    def test_guest_navbar_links(self):
        self.browser.get(self.live_server_url)
        self.assertEqual(
            [a.text for a in self.browser.find_element_by_class_name('nav-wrapper').find_elements_by_tag_name('a')],
            ['Home', 'About us', 'Contact us']
        )

    def test_user_navbar_links(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url)
        self.assertEqual(
            [a.text for a in self.browser.find_element_by_class_name('nav-wrapper').find_elements_by_tag_name('a')],
            ['Home', 'About us', 'Contact us', 'Add new claim', 'My profile']
        )

    def test_admin_navbar_links(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.admin)
        browser.get(self.live_server_url)
        self.assertEqual(
            [a.text for a in self.browser.find_element_by_class_name('nav-wrapper').find_elements_by_tag_name('a') if a.text != ''],
            ['Home', 'About us', 'Contact us', 'Add new claim', 'My profile', 'Admin tools']
        )

    def test_click_about_us(self):
        self.browser.get(self.live_server_url)
        about = self.browser.find_element_by_link_text('About us')
        about.click()
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + '/about'
        )

    def test_click_contact_us(self):
        self.browser.get(self.live_server_url)
        about = self.browser.find_element_by_link_text('Contact us')
        about.click()
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + '/contact_us/contact_us_page'
        )

    def test_click_add_new_claim(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        about = browser.find_element_by_link_text('Add new claim')
        about.click()
        self.assertEqual(
            browser.current_url,
            self.live_server_url + '/add_claim_page'
        )

    def test_click_my_profile(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        profile = browser.find_element_by_link_text('My profile')
        profile.click()
        self.assertEqual(
            browser.current_url,
            self.live_server_url + '/users/' + str(self.user1.id)
        )

    def test_user_see_claim_on_home_page(self):
        self.browser.get(self.live_server_url)
        self.assertEqual(
            self.browser.find_element_by_tag_name('h5').text,
            'claim1'
        )

    def test_view_claim(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_class_name('claim_box').find_element_by_class_name('btn').click()
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + '/claim/' + str(self.claim_1.id)
        )
        self.assertEqual(
            self.browser.find_element_by_id('claim_page_title').text,
            self.claim_1.claim
        )
        self.assertEqual(
            self.browser.find_element_by_id('img_src_' + str(self.claim_1.id)).get_attribute('src'),
            self.claim_img
        )
        self.assertEqual(
            self.browser.find_element_by_class_name('claim_details').find_element_by_tag_name('h5').text,
            'Category: ' + self.claim_1.category
        )
        self.assertEqual(
            self.browser.find_element_by_class_name('authenticity_grade').text,
            str(self.claim_1.authenticity_grade) + '%'
        )

    def test_view_comment(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        self.assertEqual(
            browser.find_element_by_class_name('comment_user_image').find_element_by_tag_name('img').get_attribute(
                'src'),
            'https://wtfact.ise.bgu.ac.il/media/profile_default_image.jpg'
        )
        self.assertEqual(
            browser.find_element_by_class_name('comment_user_details').find_element_by_tag_name('a').text,
            self.user1.username
        )
        self.assertEqual(
            browser.find_element_by_id('comment_' + str(self.comment_1.id) + '_verdict_date').text,
            self.comment_1.verdict_date.strftime('%d/%m/%Y')
        )
        self.assertEqual(
            browser.find_element_by_class_name('comment_verdict').text,
            self.comment_1.system_label.upper()
        )
        self.assertEqual(
            browser.find_element_by_class_name('comment_body').find_element_by_tag_name('h5').text,
            self.comment_1.title
        )
        self.assertEqual(
            browser.find_element_by_class_name('comment_body').find_element_by_tag_name('p').text,
            self.comment_1.description
        )
        self.assertEqual(
            browser.find_element_by_id('comment_' + str(self.comment_1.id) + '_footer').find_element_by_tag_name(
                'a').get_attribute('href'),
            self.comment_1.url
        )
        tags = [tag.text for tag in browser.find_elements_by_class_name('tag_link')]
        self.assertEqual(
            tags,
            self.comment_1.tags.split(',')
        )

    def test_view_tweet(self):
        tweet_1 = self.add_tweet(self.claim_1.user_id)
        self.browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        self.assertEqual(
            self.browser.find_element_by_id('tweet_box_' + str(tweet_1.id)).find_element_by_class_name('twitter-tweet').find_element_by_tag_name('a').get_attribute('href'),
            tweet_1.tweet_link
        )

    def test_view_reply(self):
        reply_1 = Reply(user_id=self.user1.id,
                        comment_id=self.comment_1.id,
                        content='content1')
        reply_1.save()
        time.sleep(1)
        self.browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        self.assertEqual(
            self.browser.find_element_by_class_name('reply_img').find_element_by_tag_name('img').get_attribute(
                'src'),
            'https://wtfact.ise.bgu.ac.il/media/profile_default_image.jpg'
        )
        self.assertEqual(
            self.browser.find_element_by_class_name('reply_img').find_element_by_tag_name('a').text,
            reply_1.user.username
        )
        self.assertEqual(
            self.browser.find_element_by_id('reply_' + str(reply_1.id) + '_content').text,
            reply_1.content
        )

    def test_edit_comment(self):
        comment_2 = Comment(claim_id=self.claim_1.id,
                            user_id=self.user2.id,
                            title='title2',
                            description='description2',
                            url='http://url2/',
                            verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                            system_label='True',
                            tags='t3,t4')
        comment_2.save()
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user2)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_edit').click()

        browser.find_element_by_id('comment_' + str(comment_2.id) + '_title').clear()
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_description').clear()
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_reference').clear()
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_tags').clear()

        browser.find_element_by_id('comment_' + str(comment_2.id) + '_title').send_keys('title3')
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_description').send_keys('description3')
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_reference').send_keys('http://google.com/')
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_tags').send_keys('t5')
        year = str(random.randint(2000, 2018))
        month = random.randint(1, 12)
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        day = random.randint(1, 28)
        if day < 10:
            day = '0' + str(day)
        else:
            day = str(day)
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_verdict_date_edit').send_keys(month)
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_verdict_date_edit').send_keys(day)
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_verdict_date_edit').send_keys(Keys.ARROW_RIGHT)
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_verdict_date_edit').send_keys(year)
        browser.find_elements_by_name('comment_' + str(comment_2.id) + '_label')[1].click()  # False
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_save').click()
        time.sleep(2)
        browser.get(browser.current_url)

        self.assertEqual(
            browser.find_element_by_id('comment_' + str(comment_2.id) + '_verdict_date').text,
            day + '/' + month + '/' + year
        )
        self.assertEqual(
            browser.find_elements_by_class_name('comment_verdict')[1].text,
            'FALSE'
        )
        self.assertEqual(
            browser.find_elements_by_class_name('comment_body')[1].find_element_by_tag_name('h5').text,
            'title3'
        )
        self.assertEqual(
            browser.find_elements_by_class_name('comment_body')[1].find_element_by_tag_name('p').text,
            'description3'
        )
        self.assertEqual(
            browser.find_element_by_id('comment_' + str(comment_2.id) + '_footer').find_element_by_tag_name('a').get_attribute('href'),
            'http://google.com/'
        )
        tags = [tag.text for tag in browser.find_element_by_id('comment_' + str(comment_2.id) + '_footer').find_elements_by_class_name('tag_link')]
        self.assertEqual(
            tags,
            ['t5']
        )

    def test_edit_reply(self):
        reply_1 = Reply(user_id=self.user1.id,
                        comment_id=self.comment_1.id,
                        content='content1')
        reply_1.save()
        time.sleep(1)
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        browser.find_element_by_id('reply_' + str(reply_1.id) + '_edit').click()
        browser.find_element_by_id(str(reply_1.id) + '_reply_content_edit').clear()
        browser.find_element_by_id(str(reply_1.id) + '_reply_content_edit').send_keys('content2')
        browser.find_element_by_id('reply_' + str(reply_1.id) + '_save').click()
        time.sleep(2)
        browser.get(browser.current_url)
        self.assertEqual(
            browser.find_element_by_id('reply_' + str(reply_1.id) + '_content').text,
            'content2'
        )

    def test_delete_comment(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        browser.find_element_by_id('comment_' + str(self.comment_1.id) + '_delete').click()
        browser.switch_to_alert().accept()
        time.sleep(2)  # wait for comment to be deleted
        browser.get(self.browser.current_url)
        self.assertEqual(
            len(browser.find_elements_by_class_name('comment_box')),
            1   # only add comment form remains
        )

    def test_delete_reply(self):
        reply_1 = Reply(user_id=self.user1.id,
                        comment_id=self.comment_1.id,
                        content='content1')
        reply_1.save()
        time.sleep(1)
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        browser.find_element_by_id('reply_' + str(reply_1.id) + '_delete').click()
        browser.switch_to_alert().accept()
        time.sleep(2)  # wait for reply to be deleted
        browser.get(self.browser.current_url)
        self.assertEqual(
            len(browser.find_elements_by_class_name('reply_box')),
            0
        )

    def test_delete_tweet_by_admin(self):
        tweet_1 = self.add_tweet(self.user2.id)
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.admin)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        browser.find_element_by_id(str(tweet_1.id) + '_tweet_delete').click()
        browser.switch_to_alert().accept()
        time.sleep(2)  # wait for tweet to be deleted
        browser.get(self.browser.current_url)
        self.assertEqual(
            len(browser.find_elements_by_id('tweet_box_' + str(tweet_1.id))),
            0
        )

    def test_regular_user_cannot_delete_tweet(self):
        tweet_1 = self.add_tweet(self.user2.id)
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user2)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        self.assertEqual(
            len(browser.find_elements_by_id(str(tweet_1.id) + '_tweet_delete')),
            0
        )

    def test_guest_cannot_delete_tweet(self):
        tweet_1 = self.add_tweet(self.user2.id)
        self.browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        self.assertEqual(
            len(self.browser.find_elements_by_id(str(tweet_1.id) + '_tweet_delete')),
            0
        )

    def test_guest_cannot_view_add_tweet_as_reference_button(self):
        tweet_1 = self.add_tweet(self.user2.id)
        self.browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        self.assertEqual(
            len(self.browser.find_elements_by_id(str(tweet_1.id) + '_add_comment_on_tweet)')),
            0
        )

    def test_delete_claim(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        browser.find_element_by_id(str(self.claim_1.id) + '_claim_delete').click()
        browser.switch_to_alert().accept()
        time.sleep(2)   # wait for claim to be deleted
        browser.get(self.live_server_url)
        self.assertEqual(
            len(browser.find_elements_by_class_name('claim_box')),
            0
        )

    def test_user_cannot_edit_other_users_comment(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user2)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        self.assertEqual(
            len(browser.find_elements_by_id('comment_' + str(self.comment_1.id) + '_edit')),
            0
        )

    def test_user_cannot_delete_other_users_comment(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user2)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        self.assertEqual(
            len(browser.find_elements_by_id('comment_' + str(self.comment_1.id) + '_delete')),
            0
        )

    def test_guest_cannot_view_add_comment_form(self):
        self.browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        self.assertEqual(
            len(self.browser.find_elements_by_class_name('comment_box')),
            1
        )

    def test_add_new_claim(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/add_claim_page')

        # fill form
        browser.find_element_by_id('claim').send_keys('claim2')
        browser.find_element_by_id('category').send_keys('category2')
        browser.find_element_by_id('tags').send_keys('tag3,tag4')
        browser.find_element_by_id('image_src').send_keys(self.claim_img)
        browser.find_element_by_id('submit_claim').click()
        time.sleep(4)  # wait for claim to be added

        browser.get(self.live_server_url)
        browser.find_element_by_class_name('claim_box').find_element_by_class_name("btn").click()
        browser.switch_to_alert().accept()

        claim_id = str(browser.current_url).split('/claim/')[1]

        self.assertEqual(
            browser.find_element_by_id('claim_page_title').text,
            'claim2'
        )
        self.assertEqual(
            browser.find_element_by_id('img_src_'+claim_id).get_attribute('src'),
            self.claim_img
        )
        self.assertEqual(
            browser.find_element_by_class_name('claim_details').find_element_by_tag_name('h5').text,
            'Category: category2'
        )
        self.assertEqual(
            browser.find_element_by_class_name('authenticity_grade').text,
            '50%'
        )

    def test_guest_cannot_view_add_new_claim(self):
        self.assertRaises(Exception, self.browser.get(self.live_server_url + '/add_claim_page'))

    def test_add_new_claim_with_comment(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/add_claim_page')

        # fill form
        browser.find_element_by_id('claim').send_keys('claim2')
        browser.find_element_by_id('category').send_keys('category2')
        browser.find_element_by_id('tags').send_keys('tag3,tag4')
        browser.find_element_by_id('image_src').send_keys(self.claim_img)

        # check add comment and add details
        browser.find_element_by_id('add_comment').click()
        browser.find_element_by_id('title').send_keys('title2')
        browser.find_element_by_id('description').send_keys('description2')
        browser.find_element_by_id('url').send_keys('http://google.com/')
        year = str(random.randint(2000, 2018))
        month = random.randint(1, 12)
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        day = random.randint(1, 28)
        if day < 10:
            day = '0' + str(day)
        else:
            day = str(day)
        browser.find_element_by_id('verdict_date').send_keys(month)
        browser.find_element_by_id('verdict_date').send_keys(day)
        browser.find_element_by_id('verdict_date').send_keys(Keys.ARROW_RIGHT)
        browser.find_element_by_id('verdict_date').send_keys(year)
        browser.find_elements_by_name('label')[0].click()
        browser.find_element_by_id('submit_claim').click()
        time.sleep(4)  # wait for claim and comment to be added

        browser.get(self.live_server_url)
        browser.find_element_by_class_name('claim_box').find_element_by_class_name("btn").click()
        browser.switch_to_alert().accept()
        claim_id = str(browser.current_url).split('/claim/')[1]

        self.assertEqual(
            browser.find_element_by_id('claim_page_title').text,
            'claim2'
        )
        self.assertEqual(
            browser.find_element_by_id('img_src_'+claim_id).get_attribute('src'),
            self.claim_img
        )
        self.assertEqual(
            browser.find_element_by_class_name('claim_details').find_element_by_tag_name('h5').text,
            'Category: category2'
        )
        self.assertEqual(
            browser.find_element_by_class_name('authenticity_grade').text,
            '70%'
        )

        # check if comment details are correct
        self.assertEqual(
            browser.find_element_by_class_name('comment_user_image').find_element_by_tag_name('img').get_attribute(
                'src'),
            'https://wtfact.ise.bgu.ac.il/media/profile_default_image.jpg'
        )
        self.assertEqual(
            browser.find_element_by_class_name('comment_user_details').find_element_by_tag_name('a').text,
            self.user1.username
        )
        self.assertEqual(
            browser.find_element_by_class_name('comment_user_details').find_element_by_tag_name('span').text,
            day + '/' + month + '/' + year
        )
        self.assertEqual(
            browser.find_element_by_class_name('comment_verdict').text,
            'TRUE'
        )
        self.assertEqual(
            browser.find_element_by_class_name('comment_body').find_element_by_tag_name('h5').text,
            'title2'
        )
        self.assertEqual(
            browser.find_element_by_class_name('comment_footer').find_element_by_tag_name(
                'a').get_attribute('href'),
            'http://google.com/'
        )
        tags = [tag.text for tag in browser.find_elements_by_class_name('tag_link')]
        self.assertEqual(
            tags,
            ['tag3','tag4']
        )

    def test_add_new_comment(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user2)
        browser.find_element_by_class_name('claim_box').find_element_by_class_name('btn').click()
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_title').send_keys('title2')
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_description').send_keys('description2')
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_url').send_keys('http://google.com/')
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_tags').send_keys('t3,t4')
        year = str(random.randint(2000, 2018))
        month = random.randint(1, 12)
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        day = random.randint(1, 28)
        if day < 10:
            day = '0' + str(day)
        else:
            day = str(day)
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_date').send_keys(month)
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_date').send_keys(day)
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_date').send_keys(Keys.ARROW_RIGHT)
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_date').send_keys(year)
        browser.find_elements_by_name(str(self.claim_1.id) + '_new_comment_label')[1].click() #False
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_save').click()
        time.sleep(20)  # wait for comment to be added
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user2)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))

        # check if comment details are correct
        self.assertEqual(
            browser.find_elements_by_class_name('comment_user_image')[1].find_element_by_tag_name('img').get_attribute(
                'src'),
            'https://wtfact.ise.bgu.ac.il/media/profile_default_image.jpg'
        )
        self.assertEqual(
            browser.find_elements_by_class_name('comment_box')[1].find_element_by_class_name('comment_user_details').find_element_by_tag_name('a').text,
            self.user2.username
        )
        self.assertEqual(
            browser.find_elements_by_class_name('comment_box')[1].find_element_by_class_name('comment_user_details').find_element_by_tag_name('span').text,
            day + '/' + month + '/' + year
        )
        self.assertEqual(
            browser.find_elements_by_class_name('comment_verdict')[1].text,
            'FALSE'
        )
        self.assertEqual(
            browser.find_elements_by_class_name('comment_body')[1].find_element_by_tag_name('h5').text,
            'title2'
        )
        self.assertEqual(
            browser.find_elements_by_class_name('comment_footer')[1].find_element_by_tag_name(
                'a').get_attribute('href'),
            'http://google.com/'
        )
        tags = [tag.text for tag in browser.find_elements_by_class_name('comment_footer')[1].find_elements_by_class_name('tag_link')]
        self.assertEqual(
            tags,
            ['t3', 't4']
        )

    def test_add_new_comment_with_missing_args(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user2)
        browser.find_element_by_class_name('claim_box').find_element_by_class_name('btn').click()
        claim_id = str(browser.current_url).split('/claim/')[1]

        filled = 0
        if random.randint(0, 10) > 5:
            browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_title').send_keys('title2')
            filled += 1
        if random.randint(0, 10) > 5:
            browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_description').send_keys('description2')
            filled += 1
        if filled < 2 and random.randint(0, 10) > 5:
            browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_url').send_keys('http://url2/')
            filled += 1
        time.sleep(1)
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_save').click()
        time.sleep(20)   # wait for page to show the error
        self.assertTrue(
            'Error' in browser.find_element_by_id('error_msg_' + claim_id + '_new_comment').text
        )

    def test_add_new_claim_with_missing_args(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/add_claim_page')

        # fill form
        filled = 0
        if random.randint(0, 10) > 5:
            browser.find_element_by_id('claim').send_keys('claim2')
            filled += 1
        if random.randint(0, 10) > 5:
            browser.find_element_by_id('category').send_keys('category2')
            filled += 1
        if filled < 2 and random.randint(0, 10) > 5:
            browser.find_element_by_id('tags').send_keys('tag3,tag4')
        browser.find_element_by_id('submit_claim').click()
        time.sleep(4)  # wait 4 second for page to show the error
        self.assertTrue(
            'Error' in browser.find_element_by_id('error_msg_add_new_claim').text
        )

    def test_add_new_claim_with_comment_missing_args(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/add_claim_page')

        # fill form
        browser.find_element_by_id('claim').send_keys('claim2')
        browser.find_element_by_id('category').send_keys('category2')
        browser.find_element_by_id('tags').send_keys('tag3,tag4')
        browser.find_element_by_id('image_src').send_keys(self.claim_img)

        # check add comment and add details
        browser.find_element_by_id('add_comment').click()
        filled = 0
        if random.randint(0, 10) > 5:
            browser.find_element_by_id('title').send_keys('title2')
            filled += 1
        if random.randint(0, 10) > 5:
            browser.find_element_by_id('description').send_keys('description2')
            filled += 1
        if filled < 2 and random.randint(0, 10) > 5:
            browser.find_element_by_id('url').send_keys('http://url2/')
        browser.find_element_by_id('submit_claim').click()
        time.sleep(4)  # wait 4 second for page to show the error
        self.assertTrue(
            'Error' in browser.find_element_by_id('error_msg_add_new_claim').text
        )

    def test_vote_up_comment(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        vote_count = int(browser.find_element_by_class_name('vote_count').text)
        browser.find_element_by_class_name('arrow_up').click()
        time.sleep(3)  # wait 3 second for vote_count to update
        self.assertEqual(
            int(browser.find_element_by_class_name('vote_count').text),
            vote_count + 1
        )

    def test_vote_up_comment_twice(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        vote_count = int(browser.find_element_by_class_name('vote_count').text)
        browser.find_element_by_class_name('arrow_up').click()
        time.sleep(3)  # wait 3 second for vote_count to update
        browser.find_element_by_class_name('arrow_up').click()
        time.sleep(7)  # wait 3 second for vote_count to update
        self.assertEqual(
            int(browser.find_element_by_class_name('vote_count').text),
            vote_count
        )

    def test_vote_down_comment(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        vote_count = int(browser.find_element_by_class_name('vote_count').text)
        browser.find_element_by_class_name('arrow_down').click()
        time.sleep(3)  # wait 3 second for vote_count to update
        self.assertEqual(
            int(browser.find_element_by_class_name('vote_count').text),
            vote_count - 1
        )

    def test_vote_down_comment_twice(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        vote_count = int(browser.find_element_by_class_name('vote_count').text)
        browser.find_element_by_class_name('arrow_down').click()
        time.sleep(3)  # wait 3 second for vote_count to update
        browser.find_element_by_class_name('arrow_down').click()
        time.sleep(7)  # wait 3 second for vote_count to update
        self.assertEqual(
            int(browser.find_element_by_class_name('vote_count').text),
            vote_count
        )

    def test_vote_up_then_down_commnet(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        vote_count = int(browser.find_element_by_class_name('vote_count').text)
        browser.find_element_by_class_name('arrow_up').click()
        time.sleep(3)  # wait 3 second for vote_count to update
        browser.find_element_by_class_name('arrow_down').click()
        time.sleep(7)  # wait 3 second for vote_count to update
        self.assertEqual(
            int(browser.find_element_by_class_name('vote_count').text),
            vote_count - 1
        )

    def test_vote_down_then_up_comment(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        vote_count = int(browser.find_element_by_class_name('vote_count').text)
        browser.find_element_by_class_name('arrow_down').click()
        time.sleep(3)  # wait 3 second for vote_count to update
        browser.find_element_by_class_name('arrow_up').click()
        time.sleep(7)  # wait 3 second for vote_count to update
        self.assertEqual(
            int(browser.find_element_by_class_name('vote_count').text),
            vote_count + 1
        )

    def test_vote_disabled_for_guest(self):
        self.browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        self.assertFalse(
            self.browser.find_element_by_class_name('arrow_up').is_enabled()
        )
        self.assertFalse(
            self.browser.find_element_by_class_name('arrow_down').is_enabled()
        )

    def test_new_comment_not_shown_before_10_minutes_passed(self):
        comment_2 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.user2.id,
                                 title='title2',
                                 description='description2',
                                 url='http://url2/',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                 system_label='True',
                                 tags='t3,t4')
        comment_2.save()
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        self.assertEqual(
            len(browser.find_elements_by_class_name('comment_box')),
            2
        )

    def test_search_by_tags(self):
        # add two new claims
        claim_2 = Claim(user_id=self.user1.id,
                             claim='claim2',
                             category='category2',
                             tags="tag3",
                             authenticity_grade=0,
                             image_src=self.claim_img)
        claim_2.save()
        claim_3 = Claim(user_id=self.user1.id,
                        claim='claim3',
                        category='category3',
                        tags="tag4",
                        authenticity_grade=0,
                        image_src=self.claim_img)
        claim_3.save()

        # search for a random claim
        tag_num = random.randint(1, 4)
        search_tag = 'tag'+str(tag_num)
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('search_keywords').send_keys(search_tag)
        self.browser.find_element_by_name('search_keywords').send_keys(Keys.ENTER)
        time.sleep(2)  # wait 2 second for search results
        if tag_num <= 2:
            self.assertEqual(
                self.browser.find_element_by_class_name('claim_box').find_element_by_tag_name('h6').text,
                'claim1'
            )
        else:
            self.assertEqual(
                self.browser.find_element_by_class_name('claim_box').find_element_by_tag_name('h6').text,
                'claim' + str(tag_num-1)
            )

    def test_search_by_claim(self):
        # add two new claims
        claim_2 = Claim(user_id=self.user1.id,
                             claim='claim2',
                             category='category2',
                             tags="tag3",
                             authenticity_grade=0,
                             image_src=self.claim_img)
        claim_2.save()
        claim_3 = Claim(user_id=self.user1.id,
                        claim='claim3',
                        category='category3',
                        tags="tag4",
                        authenticity_grade=0,
                        image_src=self.claim_img)
        claim_3.save()

        # search for a random claim
        search_claim = 'claim'+str(random.randint(1, 3))
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('search_keywords').send_keys(search_claim)
        self.browser.find_element_by_name('search_keywords').send_keys(Keys.ENTER)
        time.sleep(2)  # wait 2 second for search results
        self.assertEqual(
            self.browser.find_element_by_class_name('claim_box').find_element_by_tag_name('h6').text,
            search_claim
        )

    def test_search_common_number(self):
        # add two new claims
        claim_2 = Claim(user_id=self.user1.id,
                             claim='claim2',
                             category='category2',
                             tags="tag3",
                             authenticity_grade=0,
                             image_src=self.claim_img)
        claim_2.save()
        claim_3 = Claim(user_id=self.user1.id,
                        claim='claim3',
                        category='category3',
                        tags="tag4",
                        authenticity_grade=0,
                        image_src=self.claim_img)
        claim_3.save()

        # search for a random claim
        num = random.randint(1, 3)
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('search_keywords').send_keys(str(num))
        self.browser.find_element_by_name('search_keywords').send_keys(Keys.ENTER)
        time.sleep(2)  # wait 2 second for search results
        if num == 1:
            self.assertEqual(
                len(self.browser.find_elements_by_class_name('claim_box')),
                3
            )
            self.assertEqual(
                self.browser.find_element_by_class_name('claim_box').find_element_by_tag_name('h6').text,
                'claim' + str(num)
            )
        else:
            self.assertEqual(
                len(self.browser.find_elements_by_class_name('claim_box')),
                2
            )
            self.assertEqual(
                self.browser.find_elements_by_class_name('claim_box')[0].find_element_by_tag_name('h6').text,
                'claim' + str(num)
            )
            self.assertEqual(
                self.browser.find_elements_by_class_name('claim_box')[1].find_element_by_tag_name('h6').text,
                'claim' + str(num - 1)
            )

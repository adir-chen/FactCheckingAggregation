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


def authenticated_browser(browser, client, live_server_url, user):
    client.force_login(user)
    browser.get(live_server_url)
    cookie = client.cookies['sessionid']
    browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
    browser.refresh()
    return browser


class UITests(StaticLiveServerTestCase):

    def setUp(self):
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
                             image_src='image1')
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
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() - datetime.timedelta(minutes=6))
        self.browser = webdriver.Chrome('Tests/chromedriver.exe')
        self.browser.implicitly_wait(10)
        self.client = Client()

    def tearDown(self):
        self.browser.close()

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
        about = browser.find_element_by_link_text('My profile')
        about.click()
        self.assertEqual(
            browser.current_url,
            self.live_server_url + '/users/'+self.user1.username
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
            self.live_server_url + '/claim/' + self.claim_1.image_src
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
            browser.find_element_by_class_name('comment_user_image').find_element_by_tag_name('img').get_attribute('src'),
            self.live_server_url + '/static/claims/assets/images/profile_default_image.jpg'
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
            browser.find_element_by_id('comment_' + str(self.comment_1.id) + '_footer').find_element_by_tag_name('a').get_attribute('href'),
            self.comment_1.url
        )
        tags = [tag.text for tag in browser.find_elements_by_class_name('tag_link')]
        self.assertEqual(
            tags,
            self.comment_1.tags.split(',')
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
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_reference').send_keys('http://url3/')
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
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_verdict_date_edit').send_keys(day)
        browser.find_element_by_id('comment_' + str(comment_2.id) + '_verdict_date_edit').send_keys(month)
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
            'http://url3/'
        )
        tags = [tag.text for tag in browser.find_element_by_id('comment_' + str(comment_2.id) + '_footer').find_elements_by_class_name('tag_link')]
        self.assertEqual(
            tags,
            ['t5']
        )

    def test_delete_comment(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        browser.find_element_by_id('comment_' + str(self.comment_1.id) + '_delete').click()
        time.sleep(2)  # wait for comment to be deleted
        browser.get(self.browser.current_url)
        self.assertEqual(
            len(browser.find_elements_by_class_name('comment_box')),
            1   # only add comment form remains
        )

    def test_delete_claim(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        browser.find_element_by_id(str(self.claim_1.id) + '_claim_delete').click()
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
        browser.find_element_by_id('image_src').send_keys('image2')
        browser.find_element_by_id('submit_claim').click()
        browser.get(browser.current_url)

        # check if claim is on home page
        browser.get(self.live_server_url)
        self.assertEqual(
            self.browser.find_element_by_tag_name('h5').text,
            'claim2'
        )

        # check if claim details are correct
        browser.find_element_by_class_name('claim_box').find_element_by_class_name('btn').click()
        claim_id = str(browser.current_url).split('/claim/')[1]

        self.assertEqual(
            browser.find_element_by_id('claim_page_title').text,
            'claim2'
        )
        self.assertEqual(
            browser.find_element_by_id('img_src_'+claim_id).get_attribute('src'),
            self.live_server_url + '/claim/image2'
        )
        self.assertEqual(
            browser.find_element_by_class_name('claim_details').find_element_by_tag_name('h5').text,
            'Category: category2'
        )
        self.assertEqual(
            browser.find_element_by_class_name('authenticity_grade').text,
            '0%'
        )

    def test_guest_cannot_view_add_new_claim(self):
        self.browser.get(self.live_server_url + '/add_claim_page')
        self.assertEqual(
            self.browser.find_element_by_tag_name('h1').text,
            # 'Page Not Found | 404' - if Debug=False
            'Not Found'
        )

    def test_add_new_claim_with_comment(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/add_claim_page')

        # fill form
        browser.find_element_by_id('claim').send_keys('claim2')
        browser.find_element_by_id('category').send_keys('category2')
        browser.find_element_by_id('tags').send_keys('tag3,tag4')
        browser.find_element_by_id('image_src').send_keys('image2')

        # check add comment and add details
        browser.find_element_by_id('add_comment').click()
        browser.find_element_by_id('title').send_keys('title2')
        browser.find_element_by_id('description').send_keys('description2')
        browser.find_element_by_id('url').send_keys('http://url2/')
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
        browser.find_element_by_id('verdict_date').send_keys(day)
        browser.find_element_by_id('verdict_date').send_keys(month)
        browser.find_element_by_id('verdict_date').send_keys(Keys.ARROW_RIGHT)
        browser.find_element_by_id('verdict_date').send_keys(year)
        browser.find_elements_by_name('label')[0].click()
        browser.find_element_by_id('submit_claim').click()
        browser.get(browser.current_url)

        # check if claim is on home page
        browser.get(self.live_server_url)
        self.assertEqual(
            self.browser.find_element_by_tag_name('h5').text,
            'claim2'
        )

        # check if claim details are correct
        browser.find_element_by_class_name('claim_box').find_element_by_class_name('btn').click()
        claim_id = str(browser.current_url).split('/claim/')[1]
        self.assertEqual(
            browser.find_element_by_id('claim_page_title').text,
            'claim2'
        )
        self.assertEqual(
            browser.find_element_by_id('img_src_'+claim_id).get_attribute('src'),
            self.live_server_url + '/claim/image2'
        )
        self.assertEqual(
            browser.find_element_by_class_name('claim_details').find_element_by_tag_name('h5').text,
            'Category: category2'
        )
        self.assertEqual(
            browser.find_element_by_class_name('authenticity_grade').text,
            '100%'
        )

        # check if comment details are correct
        self.assertEqual(
            browser.find_element_by_class_name('comment_user_image').find_element_by_tag_name('img').get_attribute(
                'src'),
            self.live_server_url + '/static/claims/assets/images/profile_default_image.jpg'
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
            'http://url2/'
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
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_url').send_keys('http://url2/')
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
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_date').send_keys(day)
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_date').send_keys(month)
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_date').send_keys(Keys.ARROW_RIGHT)
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_date').send_keys(year)
        browser.find_elements_by_name(str(self.claim_1.id) + '_new_comment_label')[1].click() #False
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_save').click()
        browser.get(browser.current_url)

        # check if comment details are correct
        self.assertEqual(
            browser.find_elements_by_class_name('comment_user_image')[1].find_element_by_tag_name('img').get_attribute(
                'src'),
            self.live_server_url + '/static/claims/assets/images/profile_default_image.jpg'
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
            'http://url2/'
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
        browser.find_element_by_id(str(self.claim_1.id) + '_new_comment_save').click()
        time.sleep(2)   # wait 2 second for page to show the error
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
        if random.randint(0, 10) > 5:
            browser.find_element_by_id('tags').send_keys('tag3,tag4')
            filled += 1
        if filled < 3 and random.randint(0, 10) > 5:
            browser.find_element_by_id('image_src').send_keys('image2')
        browser.find_element_by_id('submit_claim').click()
        time.sleep(2)  # wait 2 second for page to show the error
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
        browser.find_element_by_id('image_src').send_keys('image2')

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
        time.sleep(2)  # wait 2 second for page to show the error
        self.assertTrue(
            'Error' in browser.find_element_by_id('error_msg_add_new_claim').text
        )

    def test_vote_up_comment(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        vote_count = int(browser.find_element_by_class_name('vote_count').text)
        browser.find_element_by_class_name('arrow_up').click()
        time.sleep(2)  # wait 2 second for vote_count to update
        self.assertEqual(
            int(browser.find_element_by_class_name('vote_count').text),
            vote_count + 1
        )

    def test_vote_up_comment_twice(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        vote_count = int(browser.find_element_by_class_name('vote_count').text)
        browser.find_element_by_class_name('arrow_up').click()
        time.sleep(2)  # wait 2 second for vote_count to update
        browser.find_element_by_class_name('arrow_up').click()
        time.sleep(2)  # wait 2 second for vote_count to update
        self.assertEqual(
            int(browser.find_element_by_class_name('vote_count').text),
            vote_count
        )

    def test_vote_down_comment(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        vote_count = int(browser.find_element_by_class_name('vote_count').text)
        browser.find_element_by_class_name('arrow_down').click()
        time.sleep(2)  # wait 2 second for vote_count to update
        self.assertEqual(
            int(browser.find_element_by_class_name('vote_count').text),
            vote_count - 1
        )

    def test_vote_down_comment_twice(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        vote_count = int(browser.find_element_by_class_name('vote_count').text)
        browser.find_element_by_class_name('arrow_down').click()
        time.sleep(2)  # wait 2 second for vote_count to update
        browser.find_element_by_class_name('arrow_down').click()
        time.sleep(2)  # wait 2 second for vote_count to update
        self.assertEqual(
            int(browser.find_element_by_class_name('vote_count').text),
            vote_count
        )

    def test_vote_up_then_down(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        vote_count = int(browser.find_element_by_class_name('vote_count').text)
        browser.find_element_by_class_name('arrow_up').click()
        time.sleep(2)  # wait 2 second for vote_count to update
        browser.find_element_by_class_name('arrow_down').click()
        time.sleep(2)  # wait 2 second for vote_count to update
        self.assertEqual(
            int(browser.find_element_by_class_name('vote_count').text),
            vote_count - 1
        )

    def test_vote_down_then_up(self):
        browser = authenticated_browser(self.browser, self.client, self.live_server_url, self.user1)
        browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
        vote_count = int(browser.find_element_by_class_name('vote_count').text)
        browser.find_element_by_class_name('arrow_down').click()
        time.sleep(2)  # wait 2 second for vote_count to update
        browser.find_element_by_class_name('arrow_up').click()
        time.sleep(2)  # wait 2 second for vote_count to update
        self.assertEqual(
            int(browser.find_element_by_class_name('vote_count').text),
            vote_count + 1
        )

    # def test_vote_disabled_for_guest(self):
    #     self.browser.get(self.live_server_url + '/claim/' + str(self.claim_1.id))
    #     self.assertFalse(
    #         self.browser.find_element_by_class_name('arrow_up').is_enabled()
    #     )
    #     self.assertFalse(
    #         self.browser.find_element_by_class_name('arrow_down').is_enabled()
    #     )

    def test_user_cannot_vote_for_new_comment(self):
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
        if random.randint(0, 10) > 5:
            browser.find_elements_by_class_name('arrow_up')[1].click()
        else:
            browser.find_elements_by_class_name('arrow_down')[1].click()
        time.sleep(2)  # wait 2 second for vote_count to update
        self.assertTrue(
            'Error' in browser.find_element_by_id('error_msg_' + str(comment_2.id) + '_comment_vote').text
        )

    def test_search_by_tags(self):
        # add two new claims
        claim_2 = Claim(user_id=self.user1.id,
                             claim='claim2',
                             category='category2',
                             tags="tag3",
                             authenticity_grade=0,
                             image_src='image2')
        claim_2.save()
        claim_3 = Claim(user_id=self.user1.id,
                        claim='claim3',
                        category='category3',
                        tags="tag4",
                        authenticity_grade=0,
                        image_src='image3')
        claim_3.save()

        # search for a random claim
        tag_num = random.randint(1, 4)
        search_tag = 'tag'+str(tag_num)
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('search_keywords').send_keys(search_tag)
        self.browser.find_element_by_class_name('searchbutton').find_element_by_tag_name('button').click()
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
                             image_src='image2')
        claim_2.save()
        claim_3 = Claim(user_id=self.user1.id,
                        claim='claim3',
                        category='category3',
                        tags="tag4",
                        authenticity_grade=0,
                        image_src='image3')
        claim_3.save()

        # search for a random claim
        search_claim = 'claim'+str(random.randint(1, 3))
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('search_keywords').send_keys(search_claim)
        self.browser.find_element_by_class_name('searchbutton').find_element_by_tag_name('button').click()
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
                             image_src='image2')
        claim_2.save()
        claim_3 = Claim(user_id=self.user1.id,
                        claim='claim3',
                        category='category3',
                        tags="tag4",
                        authenticity_grade=0,
                        image_src='image3')
        claim_3.save()

        # search for a random claim
        num = random.randint(1, 3)
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('search_keywords').send_keys(str(num))
        self.browser.find_element_by_class_name('searchbutton').find_element_by_tag_name('button').click()
        time.sleep(2)  # wait 2 second for search results
        if num == 1:
            self.assertEqual(
                len(self.browser.find_elements_by_class_name('claim_box')),
                1
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

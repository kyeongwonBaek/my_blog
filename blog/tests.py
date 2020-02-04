from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post
from django.utils import timezone
from django.contrib.auth.models import User

def create_post(title, content, author):
    blog_post = Post.objects.create(
        title=title,
        content=content,
        created=timezone.now(),
        author=author,
    )

    return blog_post


# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='rara', password='1111')

    def check_navbar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)


    def test_post_list(self):
        # 페이지 정상적으로 나옴
        response=self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        # 타이틀 = 블로그
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title
        self.assertEqual(title.text, 'Blog')
        #네비게이션바에 'Blog', 'About me' 있음
        self.check_navbar(soup)
        # POST가 없을 때 '아직 게시물이 없습니다'
        self.assertEqual(Post.objects.count(), 0)
        self.assertIn('아직 게시물이 없습니다', soup.body.text)

        # POST가 0이 아닐 때 '아직 게시물이 없습니다'가 나오지 않는다
        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,
        )
        self.assertGreater(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        body = soup.body
        self.assertNotIn('아직 게시물이 없습니다', body.text)
        self.assertIn(post_000.title, body.text)

        # read-more btn
        post_000_read_more_btn = body.find('a', id='read-more-post-{}'.format(post_000.pk))
        self.assertEqual(post_000_read_more_btn['href'], post_000.get_absolute_url())


    def test_post_detail(self):
        #첫 페이지 화면
        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,
        )

        self.assertGreater(Post.objects.count(), 0)
        post_000_url = post_000.get_absolute_url()
        self.assertEqual(post_000_url, '/blog/{}/'.format(post_000.pk))

        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)
        # 타이틀
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title

        self.assertEqual(title.text, '{} - Blog'.format(post_000.title))

        # 네비게이션바 -> 'Blog', 'About me'
        self.check_navbar(soup)

        # body에 제목, 저자, 내용 있음
        body = soup.body
        main_div = body.find('div', id='main-div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn(post_000.author.username, main_div.text)
        self.assertIn(post_000.content, main_div.text)






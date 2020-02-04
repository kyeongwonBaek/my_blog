from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post
from django.utils import timezone
from django.contrib.auth.models import User

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='rara', password='1111')

    def test_post_list(self):
        # 페이지 정상적으로 나옴
        response=self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        # 타이틀 = 블로그
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title
        self.assertEqual(title.text, 'Blog')
        #네비게이션바에 'Blog', 'About me' 있음
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)
        # POST가 없을 때 '아직 게시물이 없습니다'
        self.assertEqual(Post.objects.count(), 0)
        self.assertIn('아직 게시물이 없습니다', soup.body.text)

        # POST가 0이 아닐 때 '아직 게시물이 없습니다'가 나오지 않는다
        post_000 = Post.objects.create(
            title='The first post',
            content='Hello World',
            created=timezone.now(),
            author=self.author_000
        )
        self.assertGreater(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        body = soup.body
        self.assertNotIn('아직 게시물이 없습니다', body.text)
        self.assertIn(post_000.title, body.text)





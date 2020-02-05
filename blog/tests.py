from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category, Tag
from django.utils import timezone
from django.contrib.auth.models import User

def create_category(name='life', description=""):
    category, is_created = Category.objects.get_or_create(
        name=name,
        description=description,
    )
    category.slug = category.name.replace('','-').replace('/','')
    category.save()

    return category
def create_tag(name='some_tag'):
    tag, is_created = Tag.objects.get_or_create(
        name=name,
    )
    tag.slug = tag.name.replace('', '-').replace('/', '')
    tag.save()

    return tag

def create_post(title, content, author, category=None):
    blog_post = Post.objects.create(
        title=title,
        content=content,
        created=timezone.now(),
        author=author,
        category=category,
    )

    return blog_post



class TestModel(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='rara', password='1111')

    def test_catergory(self):
        category = create_category()

        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,
            category=category
        )

        self.assertEqual(category.post_set.count(), 1)

    def test_tag(self):
        tag_000 = create_tag(name='bad_girl')
        tag_001 = create_tag(name='bad_guy')

        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,

        )
        post_000.tags.add(tag_000)
        post_000.tags.add(tag_001)
        post_000.save()


        post_001 = create_post(
            title='Hello',
            content='My friends',
            author=self.author_000,

        )

        post_001.tags.add(tag_001)
        post_001.save()

        self.assertEqual(post_000.tags.count(), 2)# post는 여러개의 tag를 가질 수 있다
        self.assertEqual(tag_001.post_set.count(), 2)# 하나의 tag는 여러개의 post에 붙을 수 있다
        # 하나의 tag는 자신을 가진 post들을 불러올 수 있다
        self.assertEqual(tag_001.post_set.first(), post_000)
        self.assertEqual(tag_001.post_set.last(), post_001)
    def test_post(self):
        category = create_category(

        )
        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,
            category=category
        )
        self.assertEqual(category.post_set.count(), 1)

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='rara', password='1111')

    def check_navbar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)
    def check_right_side(self, soup):
        category_card = soup.find('div', id='category-card')
        self.assertIn('미분류 (1)', category_card.text)  ### 미분류(1) 있어야함
        self.assertIn('정치/사회 (1)', category_card.text)  ### 정치/사회(1) 있어야 함


        # 글이 없을 때
    def test_post_list_without_post(self):
        # 페이지 정상적으로 나옴
        response=self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        # 타이틀 = 블로그
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title
        self.assertIn('Blog', title.text)
        #네비게이션바에 'Blog', 'About me' 있음
        self.check_navbar(soup)
        # POST가 없을 때 '아직 게시물이 없습니다'
        self.assertEqual(Post.objects.count(), 0)
        self.assertIn('아직 게시물이 없습니다', soup.body.text)

        # post가 있을 때
    def test_post_list_with_post(self):
        tag_badgirl = create_tag(name='bad_girl')
        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,
            category=create_category(name='정치/사회')
        )
        post_000.tags.add(tag_badgirl)
        post_000.save()

        post_001 = create_post(
            title='The Second post',
            content='Hello World 2',
            author=self.author_000,
        )
        post_001.tags.add(tag_badgirl)
        post_001.save()

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

        #category card에서
        self.check_right_side(soup)
        # 본문에서
        main_div = body.find('div', id='main-div')
        self.assertIn('정치/사회', main_div.text)  ### 첫번째 포스트에는 '정치/사회' 있어야 함
        self.assertIn('미분류', main_div.text)  ### 두번째 포스트에는 '미분류' 있어야 함

        #포스트카드안에 태그가 있어야 함
        post_000_card = main_div.find('div', id='post-card-{}'.format(post_000.pk))
        self.assertIn('#bad_girl', post_000_card.text)# tag가 해당 post의 카드마다 있다


    def test_post_detail(self):
        #첫 페이지 화면
        tag_badgirl = create_tag(name='bad_girl')
        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,
            category=create_category(name='정치/사회')
        )
        post_000.tags.add(tag_badgirl)
        post_000.save()

        post_001 = create_post(
            title='The Second post',
            content='Hello World 2',
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

        # category card에서
        self.check_right_side(soup)

        # 포스트카드안에 태그가 있어야 함
        self.assertIn('#bad_girl', main_div.text)  # tag가 해당 post의 카드마다 있다

    def test_post_list_by_category(self):
        category_politics = create_category(name='정치/사회')
        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,

        )

        post_001 = create_post(
            title='The Second post',
            content='Hello World 2',
            author=self.author_000,
            category=category_politics
        )

        # 첫화면
        response = self.client.get(category_politics.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 타이틀
        # self.assertEqual('Blog -{}'.format(category_politics.name), soup.title.text)
        # 본문
        main_div = soup.find('div', id='main-div')
        self.assertNotIn('미분류', main_div.text)
        self.assertIn(category_politics.name, main_div.text)

    def test_post_list_no_category(self):
        category_politics = create_category(name='정치/사회')
        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,

        )

        post_001 = create_post(
            title='The Second post',
            content='Hello World 2',
            author=self.author_000,
            category=category_politics
        )

        # 첫화면
        response = self.client.get('/blog/category/_none/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 본문
        main_div = soup.find('div', id='main-div')
        self.assertIn('미분류', main_div.text)
        self.assertNotIn(category_politics.name, main_div.text)

    def test_tag_page(self):
        tag_000 = create_tag(name='bad_girl')
        tag_001 = create_tag(name='bad_guy')

        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,

        )
        post_000.tags.add(tag_000)
        post_000.tags.add(tag_001)
        post_000.save()

        post_001 = create_post(
            title='Happy',
            content='My friends',
            author=self.author_000,

        )

        post_001.tags.add(tag_001)
        post_001.save()

        # tag 페이지
        response = self.client.get(tag_000.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')
        blog_h1 = main_div.find('h1', id='blog-list-title')
        # tag 페이지 내부에 있어야 할 것들
        self.assertIn('#{}'.format(tag_000.name), blog_h1.text)
        self.assertIn(post_000.title, main_div.text)
        self.assertNotIn(post_001.title, main_div.text)








from django.test import TestCase, Client

from novels.models import User, Bookshelf, ChosenNovels
from novels.views import exclude_novels, transfer_size
from elasticsearch_dsl import Q


class ExcludeNovelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            email="test_email@example.com",
            password="test_password",
        )
        test_books = ["Book_A", "Book_B", "Book_C"]
        for book in test_books:
            novel = ChosenNovels.objects.create(
                title=book,
                author=f"{book}_author",
                outline=f"{book}_outline",
                url=f"{book}_url",
                category=f"{book}_category",
            )
            Bookshelf.objects.create(
                bookshelf="pending",
                novel_id=novel.id,
                user_id=self.user.id,
            )
    
    def test_func(self):
        results = exclude_novels(self.user.id)
        self.assertEqual(len(results), 3)
        self.assertEqual(results, ["Book_A", "Book_B", "Book_C"])


class TransferSizeTestCase(TestCase):
    def test_2h(self):
        size = "2h"
        range_query = transfer_size(size)
        self.assertEqual(range_query, Q("range", size={"lt": "240"}))
    
    def test_5h(self):
        size = "5h"
        range_query = transfer_size(size)
        self.assertEqual(range_query, Q("range", size={"gte":"240", "lt": "600"}))
    
    def test_10h(self):
        size = "10h"
        range_query = transfer_size(size)
        self.assertEqual(range_query, Q("range", size={"gte":"600", "lt": "1200"}))
    
    def test_20h(self):
        size = "20h"
        range_query = transfer_size(size)
        self.assertEqual(range_query, Q("range", size={"gte":"1200", "lt": "2400"}))
    
    def test_max(self):
        size = "max"
        range_query = transfer_size(size)
        self.assertEqual(range_query, Q("range", size={"gte":"2400"}))

    def test_other(self):
        size = "else"
        range_query = transfer_size(size)
        self.assertEqual(range_query, Q())


class SearchNovelRequestHandlerTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.endpoint = "/novels/search_novel/"
        self.user = User.objects.create(
            username="test_user",
            email="test_email@example.com",
            password="test_password",
        )
    
    def test_not_found(self):
        resp = self.client.get(self.endpoint, {"term": "TEST", "user_id": self.user.id})
        message = resp.json()[0]["message"]
        self.assertEqual(message, "抱歉書庫中尚未有符合條件的作品，目前只接受繁體中文關鍵字，建議檢視您的輸入字詞，年份與閱讀時間設定，移除部分限制再嘗試一次。小提醒：已加入書櫃/黑名單的書籍不會出現在搜尋結果唷。")
    
    def test_found_book(self):
        resp = self.client.get(self.endpoint, {"term": "美食", "user_id": self.user.id})
        results = resp.json()
        self.assertEqual(len(results), 3)
        self.assertEqual(set(results[0].keys()) - {"tags"}, {"title", "author", "outline", "url", "category", "year", "size", "date"})


class BookshelfsRequestHandlerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            email="test_email@example.com",
            password="test_password",
        )
        test_books = ["Book_A", "Book_B", "Book_C"]
        for book in test_books:
            novel = ChosenNovels.objects.create(
                title=book,
                author=f"{book}_author",
                outline=f"{book}_outline",
                url=f"{book}_url",
                category=f"{book}_category",
            )
            Bookshelf.objects.create(
                bookshelf="pending",
                novel_id=novel.id,
                user_id=self.user.id,
            )
        self.client = Client()
        self.endpoint = "/novels/bookshelfs/"
    
    def test_bookshelf_pending(self):
        resp = self.client.get(self.endpoint, {"bookshelf": "pending", "user_id": self.user.id})
        results = resp.json()
        self.assertEqual(len(results["no_folder"]), 3)
        titles = [book["title"] for book in results["no_folder"]]
        self.assertEqual(titles, ["Book_A", "Book_B", "Book_C"])
            



  

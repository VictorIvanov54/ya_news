"""Модуль фикстур для тестов."""
from datetime import datetime, timedelta

import pytest

from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """Фикстура создания объекта пользователя 'Автор'."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура создания объекта пользователя 'Не автор'."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Фикстура логина 'Автора' в клиенте."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Фикстура логина 'Не автора' в клиенте."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Фикстура создания объекта новости."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def all_news():
    """Фикстура создания списка объектов новостей."""
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def news_id(news):
    """Фикстура возвращает ID объекта новости."""
    return (news.id,)


@pytest.fixture
def comment(news, author):
    """Фикстура создания объекта комментария к новости."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Комментарий новый'
    )
    return comment


@pytest.fixture
def news_all_comment(news, not_author):
    """Фикстура создания списка объектов комментариев к новости."""
    now = timezone.now()
    news_all_comment = [
        Comment(
            news=news,
            author=not_author,
            text=f'Комментарий {index}',
            created=now + timedelta(days=index)
        )
        for index in range(5)
    ]
    Comment.objects.bulk_create(news_all_comment)


@pytest.fixture
def comment_id(comment):
    """Фикстура возвращает ID объекта комментария."""
    return (comment.id,)


@pytest.fixture
def comment_form_data(news, author):
    """Фикстура возвращает данные формы объекта комментария."""
    return {
        'news': news,
        'author': author,
        'text': 'Комментарий формы'
    }

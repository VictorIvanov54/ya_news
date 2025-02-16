"""Модуль тестирования логики."""
import pytest

from http import HTTPStatus

from pytest_django.asserts import assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


def test_user_can_create_comment(
        author_client, comment_form_data, news_id
        ):
    """Тест: Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=news_id)
    author_client.post(url, data=comment_form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news == comment_form_data['news']
    assert new_comment.text == comment_form_data['text']
    assert new_comment.author == comment_form_data['author']


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, comment_form_data, news_id
        ):
    """Тест: Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=news_id)
    client.post(url, data=comment_form_data)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author_client, comment_form_data, comment, comment_id
        ):
    """Тест: Авторизованный пользователь
    может редактировать свои комментарии.
    """
    url = reverse('news:edit', args=comment_id)
    author_client.post(url, data=comment_form_data)
    comment.refresh_from_db()
    assert comment.news == comment_form_data['news']
    assert comment.text == comment_form_data['text']
    assert comment.author == comment_form_data['author']


def test_not_author_cant_edit_comment(
        not_author_client, comment_form_data, comment, comment_id
        ):
    """Тест: Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    url = reverse('news:edit', args=comment_id)
    response = not_author_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(pk=comment_id[0])
    assert comment.news == comment_from_db.news
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author


def test_author_can_delete_comment(author_client, comment_id):
    """Тест: Авторизованный пользователь может удалять свои комментарии."""
    url = reverse('news:delete', args=comment_id)
    author_client.post(url)
    assert Comment.objects.count() == 0


def test_not_author_cant_delete_comment(not_author_client, comment_id):
    """Тест: Авторизованный пользователь не может удалять чужие комментарии."""
    url = reverse('news:delete', args=comment_id)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_user_cant_use_bad_words(not_author_client, news_id):
    """Тест: Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=news_id)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = not_author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0

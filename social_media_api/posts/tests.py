from django.urls import reverse
from django.test import override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from posts.models import Post, Comment

REST_OVERRIDES = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 2,  # small for predictable pagination assertions
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

@override_settings(REST_FRAMEWORK=REST_OVERRIDES)
class PostsCommentsAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user1 = User.objects.create_user(
            username="alice", email="alice@example.com", password="pass12345"
        )
        self.user2 = User.objects.create_user(
            username="bob", email="bob@example.com", password="pass12345"
        )

        self.tok1 = Token.objects.create(user=self.user1)
        self.tok2 = Token.objects.create(user=self.user2)

        # Clients
        self.client_anon = APIClient()
        self.client_u1 = APIClient()
        self.client_u1.credentials(HTTP_AUTHORIZATION=f"Token {self.tok1.key}")
        self.client_u2 = APIClient()
        self.client_u2.credentials(HTTP_AUTHORIZATION=f"Token {self.tok2.key}")

        # Some seed data
        self.post1 = Post.objects.create(author=self.user1, title="Hello Django", content="first content")
        self.post2 = Post.objects.create(author=self.user1, title="DRF Tips", content="search me by title")
        self.post3 = Post.objects.create(author=self.user2, title="Random note", content="ordering check")

        self.comment1 = Comment.objects.create(post=self.post1, author=self.user2, content="Nice post!")
        self.comment2 = Comment.objects.create(post=self.post1, author=self.user1, content="Thanks!")
        self.comment3 = Comment.objects.create(post=self.post2, author=self.user1, content="Interesting")

    # ---------- POSTS: READ (unauthenticated allowed) ----------
    def test_posts_list_ok_for_anon(self):
        url = reverse("post-list")
        res = self.client_anon.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("results", res.data)

    def test_posts_retrieve_ok_for_anon(self):
        url = reverse("post-detail", args=[self.post1.id])
        res = self.client_anon.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], self.post1.id)

    # ---------- POSTS: CREATE / UPDATE / DELETE & PERMISSIONS ----------
    def test_post_create_requires_auth(self):
        url = reverse("post-list")
        payload = {"title": "New unauth", "content": "Should fail"}
        res = self.client_anon.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_create_sets_author_to_request_user_and_ignores_payload_author(self):
        url = reverse("post-list")
        payload = {
            "title": "My new post",
            "content": "Body",
            "author": self.user2.id,  # should be ignored by perform_create
        }
        res = self.client_u1.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        new_id = res.data["id"]
        obj = Post.objects.get(id=new_id)
        self.assertEqual(obj.author_id, self.user1.id)  # integrity: cannot spoof author

    def test_post_update_only_owner_can_edit(self):
        url = reverse("post-detail", args=[self.post1.id])

        # Non-owner tries to update
        res = self.client_u2.patch(url, {"title": "Hacked"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Owner updates successfully
        res = self.client_u1.patch(url, {"title": "Updated by owner"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.title, "Updated by owner")

    def test_post_delete_only_owner(self):
        url = reverse("post-detail", args=[self.post2.id])

        # Non-owner delete
        res = self.client_u2.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Owner delete
        res = self.client_u1.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.post2.id).exists())

    # ---------- POSTS: PAGINATION / SEARCH / FILTER / ORDERING ----------
    def test_posts_pagination(self):
        # Create extra posts to exceed PAGE_SIZE=2
        Post.objects.create(author=self.user1, title="Extra 1", content="a")
        Post.objects.create(author=self.user1, title="Extra 2", content="b")

        url = reverse("post-list")
        res = self.client_anon.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)  # PAGE_SIZE
        self.assertIsNotNone(res.data["next"])  # there should be a next page

        res2 = self.client_anon.get(res.data["next"])
        self.assertEqual(res2.status_code, status.HTTP_200_OK)

    def test_posts_search_by_title_or_content(self):
        url = reverse("post-list")
        # Should match post with title "DRF Tips"
        res = self.client_anon.get(url, {"search": "DRF"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [p["id"] for p in res.data["results"]]
        self.assertIn(self.post2.id, ids)

        # Search by content phrase
        res2 = self.client_anon.get(url, {"search": "ordering"})
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        ids2 = [p["id"] for p in res2.data["results"]]
        self.assertIn(self.post3.id, ids2)

    def test_posts_filter_by_author(self):
        url = reverse("post-list")
        res = self.client_anon.get(url, {"author": self.user1.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for item in res.data["results"]:
            # Depending on your serializer, 'author' may be a pk or username.
            # Validate from DB to be robust:
            self.assertEqual(Post.objects.get(id=item["id"]).author_id, self.user1.id)

    def test_posts_ordering_by_created_at(self):
        url = reverse("post-list")
        # ascending (oldest first)
        res = self.client_anon.get(url, {"ordering": "created_at"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        page_ids = [p["id"] for p in res.data["results"]]
        # The first page's first element should be one of the earliest created posts
        earliest = Post.objects.order_by("created_at").first().id
        self.assertIn(earliest, page_ids)

        # descending (newest first)
        res_desc = self.client_anon.get(url, {"ordering": "-created_at"})
        self.assertEqual(res_desc.status_code, status.HTTP_200_OK)
        newest = Post.objects.order_by("-created_at").first().id
        page_ids_desc = [p["id"] for p in res_desc.data["results"]]
        self.assertIn(newest, page_ids_desc)

    # ---------- COMMENTS: READ / CREATE / UPDATE / DELETE ----------
    def test_comments_list_and_filter_by_post(self):
        url = reverse("comment-list")
        res = self.client_anon.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("results", res.data)

        # Filter by post
        res2 = self.client_anon.get(url, {"post": self.post1.id})
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        for item in res2.data["results"]:
            self.assertEqual(Comment.objects.get(id=item["id"]).post_id, self.post1.id)

    def test_comment_create_requires_auth_and_sets_author(self):
        url = reverse("comment-list")

        # Unauthenticated
        res = self.client_anon.post(url, {"post": self.post1.id, "content": "anon try"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticated user1
        res2 = self.client_u1.post(url, {"post": self.post1.id, "content": "legit"}, format="json")
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        c = Comment.objects.get(id=res2.data["id"])
        self.assertEqual(c.author_id, self.user1.id)

    def test_comment_update_delete_permissions(self):
        # comment1 was authored by user2
        detail = reverse("comment-detail", args=[self.comment1.id])

        # Non-owner (user1) cannot modify
        res = self.client_u1.patch(detail, {"content": "edited by non-owner"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Owner (user2) can modify
        res2 = self.client_u2.patch(detail, {"content": "owner edit"}, format="json")
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.comment1.refresh_from_db()
        self.assertEqual(self.comment1.content, "owner edit")

        # Non-owner cannot delete
        res3 = self.client_u1.delete(detail)
        self.assertEqual(res3.status_code, status.HTTP_403_FORBIDDEN)

        # Owner can delete
        res4 = self.client_u2.delete(detail)
        self.assertEqual(res4.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment1.id).exists())

    # ---------- VALIDATION / DATA INTEGRITY ----------
    def test_post_requires_title_and_content(self):
        url = reverse("post-list")
        res = self.client_u1.post(url, {"title": ""}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_requires_valid_post_fk(self):
        url = reverse("comment-list")
        res = self.client_u1.post(url, {"post": 999999, "content": "invalid fk"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_change_post_author_even_if_provided(self):
        # Owner creates a post
        create_res = self.client_u1.post(reverse("post-list"), {"title": "x", "content": "y"}, format="json")
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        pid = create_res.data["id"]

        # Attempt to change author via PATCH as the same owner (should be ignored)
        patch = self.client_u1.patch(reverse("post-detail", args=[pid]), {"author": self.user2.id}, format="json")
        self.assertIn(patch.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
        # Regardless of serializer behavior, DB author must remain user1
        self.assertEqual(Post.objects.get(id=pid).author_id, self.user1.id)

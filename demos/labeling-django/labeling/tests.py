from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Item


class OwnershipTests(TestCase):
    """The load-bearing test for this demo: the
    web-stack-advisor skill's multi-user.md insists data isolation must
    be tested, not just implemented. This is that test, and its FastAPI
    equivalent lives in
    demos/labeling-fastapi-react/api/tests/test_api.py - running the
    same assertion against both stacks is the actual comparison.
    """

    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="pw")
        self.bob = User.objects.create_user(username="bob", password="pw")

        self.alice_item = Item.objects.create(
            text="Ticket assigned to Alice",
            model_label="billing",
            model_score=0.5,
            assigned_to=self.alice,
        )

    def test_reviewer_sees_only_their_own_items_in_queue(self):
        self.client.login(username="alice", password="pw")
        response = self.client.get(reverse("queue"))
        self.assertContains(response, "Ticket assigned to Alice")

        self.client.login(username="bob", password="pw")
        response = self.client.get(reverse("queue"))
        self.assertNotContains(response, "Ticket assigned to Alice")

    def test_reviewer_cannot_open_another_reviewers_item(self):
        # bob requesting alice's item id directly, bypassing his own
        # queue entirely - this is the request the ownership check in
        # labeling/views.py's label_item() has to reject.
        self.client.login(username="bob", password="pw")
        response = self.client.get(reverse("label-item", args=[self.alice_item.id]))
        self.assertEqual(response.status_code, 404)

    def test_owner_can_open_their_own_item(self):
        self.client.login(username="alice", password="pw")
        response = self.client.get(reverse("label-item", args=[self.alice_item.id]))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("queue"))
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('queue')}"
        )


class LabelSubmissionTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="pw")
        self.item = Item.objects.create(
            text="Ticket",
            model_label="technical",
            model_score=0.9,
            assigned_to=self.alice,
        )
        self.client.login(username="alice", password="pw")

    def test_submitting_a_label_saves_it_and_redirects_to_queue(self):
        response = self.client.post(
            reverse("label-item", args=[self.item.id]),
            {"decision": "correct", "corrected_label": "", "note": ""},
        )
        self.assertRedirects(response, reverse("queue"))
        self.assertEqual(self.item.labels.count(), 1)
        self.assertEqual(self.item.labels.first().decision, "correct")

    def test_relabeling_updates_the_existing_label_not_a_second_one(self):
        self.client.post(
            reverse("label-item", args=[self.item.id]),
            {"decision": "correct", "corrected_label": "", "note": ""},
        )
        self.client.post(
            reverse("label-item", args=[self.item.id]),
            {"decision": "incorrect", "corrected_label": "refund", "note": "mislabeled"},
        )
        self.assertEqual(self.item.labels.count(), 1)
        self.assertEqual(self.item.labels.first().decision, "incorrect")

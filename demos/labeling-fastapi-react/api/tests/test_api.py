"""Auth and ownership tests for main.py's routes.

Uses FastAPI's `TestClient` against an isolated, temporary SQLite
database per test (via the `seeded` fixture below) - no live server/port
needed, same in-process approach as
rest-apis-flask/library-crud/tests/test_app.py's Flask test_client().

test_reviewer_cannot_get_another_reviewers_item is the load-bearing one:
its exact counterpart is
demos/labeling-django/labeling/tests.py's
test_reviewer_cannot_open_another_reviewers_item - running the same
assertion against both stacks is the actual comparison this pair of
demos exists to make.
"""

import pytest
from fastapi.testclient import TestClient

from database import make_session_factory
from main import create_app
from models import Item, User
from security import hash_password


class Seeded:
    """Small bag of what the `seeded` fixture below set up, so tests can
    refer to `seeded.client`, `seeded.alice_item_id`, etc. by name
    instead of unpacking a tuple.
    """

    def __init__(self, client: TestClient, alice_item_id: int):
        self.client = client
        self.alice_item_id = alice_item_id


@pytest.fixture
def seeded(tmp_path) -> Seeded:
    db_path = tmp_path / "test.db"
    app = create_app(sqlite_path=db_path)

    # A second session bound to the same temporary file, used only to
    # insert fixture data directly - separate from the session the app
    # itself uses per-request via deps.get_db's override.
    db = make_session_factory(db_path)()
    try:
        alice = User(username="alice", hashed_password=hash_password("pw"), is_admin=False)
        bob = User(username="bob", hashed_password=hash_password("pw"), is_admin=False)
        admin = User(username="admin", hashed_password=hash_password("pw"), is_admin=True)
        db.add_all([alice, bob, admin])
        db.flush()  # assigns ids without a full commit

        alice_item = Item(
            text="Ticket assigned to Alice",
            model_label="billing",
            model_score=0.5,
            assigned_to_id=alice.id,
        )
        db.add(alice_item)
        db.commit()
        alice_item_id = alice_item.id
    finally:
        db.close()

    return Seeded(client=TestClient(app), alice_item_id=alice_item_id)


def auth_headers(client: TestClient, username: str, password: str = "pw") -> dict:
    response = client.post("/auth/login", data={"username": username, "password": password})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---- Auth ----


def test_login_with_correct_credentials_returns_a_token(seeded):
    response = seeded.client.post("/auth/login", data={"username": "alice", "password": "pw"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_with_wrong_password_is_401(seeded):
    response = seeded.client.post(
        "/auth/login", data={"username": "alice", "password": "wrong"}
    )
    assert response.status_code == 401


def test_items_endpoint_without_a_token_is_401(seeded):
    assert seeded.client.get("/items").status_code == 401


# ---- Ownership ----


def test_reviewer_sees_only_their_own_items_in_queue(seeded):
    response = seeded.client.get("/items", headers=auth_headers(seeded.client, "alice"))
    texts = [item["text"] for item in response.json()]
    assert "Ticket assigned to Alice" in texts

    response = seeded.client.get("/items", headers=auth_headers(seeded.client, "bob"))
    texts = [item["text"] for item in response.json()]
    assert "Ticket assigned to Alice" not in texts


def test_reviewer_cannot_get_another_reviewers_item(seeded):
    # bob requesting alice's item id directly, bypassing his own queue
    # entirely - the request deps.py's get_owned_item() has to reject.
    response = seeded.client.get(
        f"/items/{seeded.alice_item_id}", headers=auth_headers(seeded.client, "bob")
    )
    assert response.status_code == 404


def test_owner_can_get_their_own_item(seeded):
    response = seeded.client.get(
        f"/items/{seeded.alice_item_id}", headers=auth_headers(seeded.client, "alice")
    )
    assert response.status_code == 200
    assert response.json()["my_label"] is None


def test_reviewer_cannot_label_another_reviewers_item(seeded):
    response = seeded.client.post(
        f"/items/{seeded.alice_item_id}/label",
        json={"decision": "correct"},
        headers=auth_headers(seeded.client, "bob"),
    )
    assert response.status_code == 404


# ---- Labeling ----


def test_submitting_a_label_saves_it(seeded):
    headers = auth_headers(seeded.client, "alice")
    response = seeded.client.post(
        f"/items/{seeded.alice_item_id}/label",
        json={"decision": "correct"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "correct"

    item = seeded.client.get(f"/items/{seeded.alice_item_id}", headers=headers).json()
    assert item["my_label"]["decision"] == "correct"


def test_relabeling_updates_the_existing_label_not_a_second_one(seeded):
    headers = auth_headers(seeded.client, "alice")
    seeded.client.post(
        f"/items/{seeded.alice_item_id}/label", json={"decision": "correct"}, headers=headers
    )
    seeded.client.post(
        f"/items/{seeded.alice_item_id}/label",
        json={"decision": "incorrect", "corrected_label": "refund"},
        headers=headers,
    )

    item = seeded.client.get(f"/items/{seeded.alice_item_id}", headers=headers).json()
    assert item["my_label"]["decision"] == "incorrect"
    assert item["my_label"]["corrected_label"] == "refund"


def test_submitting_an_invalid_decision_is_422(seeded):
    headers = auth_headers(seeded.client, "alice")
    response = seeded.client.post(
        f"/items/{seeded.alice_item_id}/label",
        json={"decision": "maybe"},
        headers=headers,
    )
    assert response.status_code == 422


# ---- Admin ----


def test_admin_can_list_all_labels(seeded):
    alice_headers = auth_headers(seeded.client, "alice")
    seeded.client.post(
        f"/items/{seeded.alice_item_id}/label", json={"decision": "correct"}, headers=alice_headers
    )

    response = seeded.client.get("/admin/labels", headers=auth_headers(seeded.client, "admin"))
    assert response.status_code == 200
    assert response.json()[0]["reviewer_username"] == "alice"


def test_non_admin_cannot_list_all_labels(seeded):
    response = seeded.client.get("/admin/labels", headers=auth_headers(seeded.client, "alice"))
    assert response.status_code == 403

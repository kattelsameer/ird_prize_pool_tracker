"""API-level settings/networks tests (CLAUDE.md §36, §41).

No coverage existed for this router before this file -- notably the
add/rename/deactivate network flow (§36 "Add/edit/deactivate network
options"), which PATCH /api/settings/networks/{id} (added alongside the
frontend contract-drift fix) newly implements.
"""
import pytest

from tests.data_api_settings import NEW_NETWORK_NAME, UPDATE_SETTINGS_CASES

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")


def test_get_settings_returns_default_flags_and_seeded_networks(client):
    response = client.get("/api/settings")
    assert response.status_code == 200
    body = response.json()

    assert body["notify_new_match"] is True
    assert body["notify_claim_expiring"] is True
    assert body["notify_claim_expired"] is True
    assert body["notify_sync_updates"] is True
    assert body["notify_sync_failures"] is True
    assert isinstance(body["networks"], list)
    assert len(body["networks"]) > 0
    for network in body["networks"]:
        assert set(network.keys()) == {"id", "name", "active"}


@pytest.mark.parametrize("name,payload,field,expected", UPDATE_SETTINGS_CASES)
def test_put_settings_updates_only_provided_flags(client, name, payload, field, expected):
    before = client.get("/api/settings").json()

    response = client.put("/api/settings", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body[field] == expected, name

    # Fields not included in the payload are untouched.
    untouched_fields = [f for f in before if f not in ("networks", field)]
    for other_field in untouched_fields:
        assert body[other_field] == before[other_field], f"{name}: {other_field} changed unexpectedly"


def test_add_network_then_rename_and_deactivate(client):
    created = client.post("/api/settings/networks", json={"name": NEW_NETWORK_NAME}).json()
    assert created["name"] == NEW_NETWORK_NAME
    assert created["active"] is True

    listing = client.get("/api/settings").json()
    assert any(n["id"] == created["id"] for n in listing["networks"])

    renamed = client.patch(f"/api/settings/networks/{created['id']}", json={"name": "ConnectIPS Wallet"})
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "ConnectIPS Wallet"

    deactivated = client.patch(f"/api/settings/networks/{created['id']}", json={"active": False})
    assert deactivated.status_code == 200
    assert deactivated.json()["active"] is False
    # Renaming persisted independently of the later deactivate call.
    assert deactivated.json()["name"] == "ConnectIPS Wallet"


def test_reactivate_network_by_adding_same_name_again(client):
    created = client.post("/api/settings/networks", json={"name": NEW_NETWORK_NAME}).json()
    client.patch(f"/api/settings/networks/{created['id']}", json={"active": False})

    reactivated = client.post("/api/settings/networks", json={"name": NEW_NETWORK_NAME}).json()
    assert reactivated["id"] == created["id"]
    assert reactivated["active"] is True


def test_update_unknown_network_404(client):
    response = client.patch("/api/settings/networks/does-not-exist", json={"active": False})
    assert response.status_code == 404

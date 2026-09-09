import pytest

from database.db import init_db
from services.ticket_service import (
    create_ticket,
    get_all_tickets,
    get_ticket,
    update_ticket,
    delete_ticket,
    search_tickets,
)


@pytest.fixture
def test_database(monkeypatch, tmp_path):
    """Create a temporary database for testing."""

    database_path = tmp_path / "test_helpdesk.db"

    monkeypatch.setattr(
        "config.DATABASE_PATH",
        str(database_path),
    )

    monkeypatch.setattr(
        "database.db.DATABASE_PATH",
        str(database_path),
    )

    init_db()

    yield


def test_create_ticket(test_database):
    ticket_id = create_ticket(
        "Laptop not working",
        "Laptop does not turn on.",
        "Hardware",
        "High",
        "Open",
        "John",
    )

    assert ticket_id == 1

    ticket = get_ticket(ticket_id)

    assert ticket["title"] == "Laptop not working"
    assert ticket["priority"] == "High"
    assert ticket["status"] == "Open"


def test_retrieve_tickets(test_database):
    create_ticket(
        "Email issue",
        "Unable to send email.",
        "Software",
        "Medium",
        "Open",
        "John",
    )

    create_ticket(
        "Network issue",
        "Internet is not working.",
        "Network",
        "Immediate",
        "In Progress",
        "Sarah",
    )

    tickets = get_all_tickets()

    assert len(tickets) == 2


def test_update_ticket(test_database):
    ticket_id = create_ticket(
        "Printer issue",
        "Printer is not printing.",
        "Hardware",
        "Low",
        "Open",
        "John",
    )

    update_ticket(
        ticket_id,
        "Printer issue - Updated",
        "Printer requires maintenance.",
        "High",
        "In Progress",
        "Sarah",
    )

    ticket = get_ticket(ticket_id)

    assert ticket["title"] == "Printer issue - Updated"
    assert ticket["priority"] == "High"
    assert ticket["status"] == "In Progress"
    assert ticket["assigned_to"] == "Sarah"


def test_delete_ticket(test_database):
    ticket_id = create_ticket(
        "Test ticket",
        "Ticket for deletion test.",
        "Other",
        "Low",
        "Open",
        "John",
    )

    delete_ticket(ticket_id)

    with pytest.raises(ValueError, match="Ticket not found"):
        get_ticket(ticket_id)


def test_search_and_filter(test_database):
    create_ticket(
        "VPN issue",
        "VPN is not connecting.",
        "Network",
        "High",
        "In Progress",
        "John",
    )

    create_ticket(
        "Mouse issue",
        "Mouse is not working.",
        "Hardware",
        "Low",
        "Open",
        "Sarah",
    )

    results = search_tickets(
        priority="High",
        status="In Progress",
    )

    assert len(results) == 1
    assert results[0]["title"] == "VPN issue"


def test_invalid_input(test_database):
    with pytest.raises(ValueError, match="Title is required"):
        create_ticket(
            "",
            "Some description",
            "Hardware",
            "High",
            "Open",
            "John",
        )


def test_invalid_ticket_id(test_database):
    with pytest.raises(ValueError, match="Invalid ticket ID"):
        get_ticket(-1)


def test_update_non_existing_ticket(test_database):
    with pytest.raises(ValueError, match="Ticket not found"):
        update_ticket(
            999,
            "Title",
            "Description",
            "High",
            "Open",
            "John",
        )


def test_delete_non_existing_ticket(test_database):
    with pytest.raises(ValueError, match="Ticket not found"):
        delete_ticket(999)
from datetime import datetime

from database.db import get_connection


# Allowed ticket priorities
PRIORITIES = [
    "Low",
    "Medium",
    "High",
    "Immediate",
    "Critical",
]


# Allowed ticket statuses
STATUSES = [
    "Open",
    "In Progress",
    "Resolved",
    "Closed",
    "Hold",
]


# Allowed ticket categories
CATEGORIES = [
    "Hardware",
    "Software",
    "Network",
    "Access",
    "Other",
]


def validate_ticket_data(
    title,
    description,
    category,
    priority,
    status,
    assigned_to,
):
    """Validate ticket information."""

    errors = []

    if not title or not title.strip():
        errors.append("Title is required.")

    if not description or not description.strip():
        errors.append("Description is required.")

    if not category or not category.strip():
        errors.append("Category is required.")
    elif category not in CATEGORIES:
        errors.append("Invalid category selected.")

    if not priority or priority not in PRIORITIES:
        errors.append("Invalid priority selected.")

    if not status or status not in STATUSES:
        errors.append("Invalid status selected.")

    if not assigned_to or not assigned_to.strip():
        errors.append("Assigned To is required.")

    return errors


def create_ticket(
    title,
    description,
    category,
    priority,
    status,
    assigned_to,
):
    """Create a new ticket."""

    errors = validate_ticket_data(
        title,
        description,
        category,
        priority,
        status,
        assigned_to,
    )

    if errors:
        raise ValueError(" ".join(errors))

    created_date = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO tickets (
                title,
                description,
                category,
                priority,
                status,
                created_date,
                assigned_to
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title.strip(),
                description.strip(),
                category,
                priority,
                status,
                created_date,
                assigned_to.strip(),
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def get_all_tickets():
    """Retrieve all tickets."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT *
            FROM tickets
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()

    finally:
        connection.close()


def get_ticket(ticket_id):
    """Retrieve one ticket by ID."""

    if not isinstance(ticket_id, int) or ticket_id <= 0:
        raise ValueError("Invalid ticket ID.")

    connection = get_connection()

    try:
        ticket = connection.execute(
            """
            SELECT *
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,),
        ).fetchone()

        if ticket is None:
            raise ValueError("Ticket not found.")

        return ticket

    finally:
        connection.close()


def update_ticket(
    ticket_id,
    title,
    description,
    priority,
    status,
    assigned_to,
):
    """Update an existing ticket."""

    if not isinstance(ticket_id, int) or ticket_id <= 0:
        raise ValueError("Invalid ticket ID.")

    connection = get_connection()

    try:
        existing_ticket = connection.execute(
            """
            SELECT *
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,),
        ).fetchone()

        if existing_ticket is None:
            raise ValueError("Ticket not found.")

        errors = []

        if not title or not title.strip():
            errors.append("Title is required.")

        if not description or not description.strip():
            errors.append("Description is required.")

        if not priority or priority not in PRIORITIES:
            errors.append("Invalid priority selected.")

        if not status or status not in STATUSES:
            errors.append("Invalid status selected.")

        if not assigned_to or not assigned_to.strip():
            errors.append("Assigned To is required.")

        if errors:
            raise ValueError(" ".join(errors))

        connection.execute(
            """
            UPDATE tickets
            SET
                title = ?,
                description = ?,
                priority = ?,
                status = ?,
                assigned_to = ?
            WHERE id = ?
            """,
            (
                title.strip(),
                description.strip(),
                priority,
                status,
                assigned_to.strip(),
                ticket_id,
            ),
        )

        connection.commit()

    finally:
        connection.close()


def delete_ticket(ticket_id):
    """Delete a ticket."""

    if not isinstance(ticket_id, int) or ticket_id <= 0:
        raise ValueError("Invalid ticket ID.")

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM tickets
            WHERE id = ?
            """,
            (ticket_id,),
        )

        if cursor.rowcount == 0:
            raise ValueError("Ticket not found.")

        connection.commit()

    finally:
        connection.close()


def search_tickets(
    ticket_id=None,
    title=None,
    priority=None,
    status=None,
    category=None,
):
    """Search and filter tickets."""

    connection = get_connection()

    try:
        query = """
            SELECT *
            FROM tickets
            WHERE 1 = 1
        """

        parameters = []

        # Filter by Ticket ID
        if ticket_id:

            try:
                ticket_id = int(ticket_id)

            except (TypeError, ValueError):
                raise ValueError(
                    "Ticket ID must be a valid number."
                )

            if ticket_id <= 0:
                raise ValueError(
                    "Ticket ID must be greater than zero."
                )

            query += " AND id = ?"
            parameters.append(ticket_id)

        # Filter by title
        if title and title.strip():

            query += " AND title LIKE ?"

            parameters.append(
                f"%{title.strip()}%"
            )

        # Filter by priority
        if priority:

            if priority not in PRIORITIES:
                raise ValueError(
                    "Invalid priority selected."
                )

            query += " AND priority = ?"
            parameters.append(priority)

        # Filter by status
        if status:

            if status not in STATUSES:
                raise ValueError(
                    "Invalid status selected."
                )

            query += " AND status = ?"
            parameters.append(status)

        # Filter by category
        if category:

            if category not in CATEGORIES:
                raise ValueError(
                    "Invalid category selected."
                )

            query += " AND category = ?"
            parameters.append(category)

        query += " ORDER BY id DESC"

        cursor = connection.execute(
            query,
            parameters,
        )

        return cursor.fetchall()

    finally:
        connection.close()


def get_dashboard_stats():
    """Calculate ticket statistics from the database."""

    connection = get_connection()

    try:

        # Total tickets
        total = connection.execute(
            """
            SELECT COUNT(*)
            FROM tickets
            """
        ).fetchone()[0]


        # Open tickets
        open_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM tickets
            WHERE status = ?
            """,
            ("Open",),
        ).fetchone()[0]


        # In Progress tickets
        in_progress = connection.execute(
            """
            SELECT COUNT(*)
            FROM tickets
            WHERE status = ?
            """,
            ("In Progress",),
        ).fetchone()[0]


        # Resolved tickets
        resolved = connection.execute(
            """
            SELECT COUNT(*)
            FROM tickets
            WHERE status = ?
            """,
            ("Resolved",),
        ).fetchone()[0]


        # Closed tickets
        closed = connection.execute(
            """
            SELECT COUNT(*)
            FROM tickets
            WHERE status = ?
            """,
            ("Closed",),
        ).fetchone()[0]


        # Hold tickets
        hold = connection.execute(
            """
            SELECT COUNT(*)
            FROM tickets
            WHERE status = ?
            """,
            ("Hold",),
        ).fetchone()[0]


        # Immediate priority tickets
        immediate = connection.execute(
            """
            SELECT COUNT(*)
            FROM tickets
            WHERE priority = ?
            """,
            ("Immediate",),
        ).fetchone()[0]


        # Critical priority tickets
        critical = connection.execute(
            """
            SELECT COUNT(*)
            FROM tickets
            WHERE priority = ?
            """,
            ("Critical",),
        ).fetchone()[0]


        # Return all dashboard statistics
        return {
            "total": total,
            "open": open_count,
            "in_progress": in_progress,
            "resolved": resolved,
            "closed": closed,
            "hold": hold,
            "immediate": immediate,
            "critical": critical,
        }

    finally:
        connection.close()
        
def export_tickets():
    """Retrieve all tickets for CSV export."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT
                id,
                title,
                description,
                category,
                priority,
                status,
                created_date,
                assigned_to
            FROM tickets
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()

    finally:
        connection.close()
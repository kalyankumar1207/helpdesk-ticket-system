from flask import Flask, render_template, request, redirect, url_for, flash

from config import SECRET_KEY
from database.db import init_db
from services.ticket_service import (
    CATEGORIES,
    PRIORITIES,
    STATUSES,
    create_ticket,
    delete_ticket,
    get_all_tickets,
    get_dashboard_stats,
    get_ticket,
    search_tickets,
    update_ticket,
)


app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY


# Create the database table when the application starts.
init_db()


@app.route("/")
def dashboard():
    """Display the dashboard with ticket statistics."""

    stats = get_dashboard_stats()

    return render_template(
        "dashboard.html",
        stats=stats,
    )


@app.route("/tickets")
def tickets():
    """Display tickets with optional search and filters."""

    ticket_id = request.args.get("ticket_id", "").strip()
    title = request.args.get("title", "").strip()
    priority = request.args.get("priority", "").strip()
    status = request.args.get("status", "").strip()
    category = request.args.get("category", "").strip()

    try:
        filtered_tickets = search_tickets(
            ticket_id=ticket_id or None,
            title=title or None,
            priority=priority or None,
            status=status or None,
            category=category or None,
        )

    except ValueError as error:
        flash(str(error), "danger")
        filtered_tickets = get_all_tickets()

    return render_template(
        "tickets.html",
        tickets=filtered_tickets,
        priorities=PRIORITIES,
        statuses=STATUSES,
        categories=CATEGORIES,
        selected_ticket_id=ticket_id,
        selected_title=title,
        selected_priority=priority,
        selected_status=status,
        selected_category=category,
    )


@app.route("/tickets/create", methods=["GET", "POST"])
def create_ticket_page():
    """Display and process the create-ticket form."""

    if request.method == "POST":
        title = request.form.get("title", "")
        description = request.form.get("description", "")
        category = request.form.get("category", "")
        priority = request.form.get("priority", "")
        status = request.form.get("status", "")
        assigned_to = request.form.get("assigned_to", "")

        try:
            ticket_id = create_ticket(
                title=title,
                description=description,
                category=category,
                priority=priority,
                status=status,
                assigned_to=assigned_to,
            )

            flash(
                f"Ticket #{ticket_id} created successfully.",
                "success",
            )

            return redirect(url_for("tickets"))

        except ValueError as error:
            flash(str(error), "danger")

        except Exception:
            flash(
                "An unexpected database error occurred.",
                "danger",
            )

    return render_template(
        "create_ticket.html",
        categories=CATEGORIES,
        priorities=PRIORITIES,
        statuses=STATUSES,
    )


@app.route("/tickets/<int:ticket_id>/edit", methods=["GET", "POST"])
def edit_ticket(ticket_id):
    """Display and process the edit-ticket form."""

    try:
        ticket = get_ticket(ticket_id)

    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("tickets"))

    if request.method == "POST":
        title = request.form.get("title", "")
        description = request.form.get("description", "")
        priority = request.form.get("priority", "")
        status = request.form.get("status", "")
        assigned_to = request.form.get("assigned_to", "")

        try:
            update_ticket(
                ticket_id=ticket_id,
                title=title,
                description=description,
                priority=priority,
                status=status,
                assigned_to=assigned_to,
            )

            flash(
                f"Ticket #{ticket_id} updated successfully.",
                "success",
            )

            return redirect(url_for("tickets"))

        except ValueError as error:
            flash(str(error), "danger")

        except Exception:
            flash(
                "An unexpected database error occurred.",
                "danger",
            )

        # Reload the updated form values after a validation error.
        ticket = {
            "id": ticket_id,
            "title": title,
            "description": description,
            "category": ticket["category"],
            "priority": priority,
            "status": status,
            "created_date": ticket["created_date"],
            "assigned_to": assigned_to,
        }

    return render_template(
        "edit_ticket.html",
        ticket=ticket,
        priorities=PRIORITIES,
        statuses=STATUSES,
    )


@app.route("/tickets/<int:ticket_id>/delete", methods=["POST"])
def delete_ticket_page(ticket_id):
    """Delete a ticket after confirmation."""

    try:
        delete_ticket(ticket_id)

        flash(
            f"Ticket #{ticket_id} deleted successfully.",
            "success",
        )

    except ValueError as error:
        flash(str(error), "danger")

    except Exception:
        flash(
            "An unexpected database error occurred.",
            "danger",
        )

    return redirect(url_for("tickets"))


@app.errorhandler(404)
def page_not_found(error):
    """Handle invalid URLs."""

    return (
        render_template(
            "base.html",
            error_message="The requested page was not found.",
        ),
        404,
    )


@app.errorhandler(500)
def internal_server_error(error):
    """Handle unexpected application errors."""

    return (
        render_template(
            "base.html",
            error_message="An unexpected server error occurred.",
        ),
        500,
    )


# Application entry point
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
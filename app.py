from flask import Flask, render_template, request, redirect, url_for, flash, session

from config import SECRET_KEY
from database.db import init_db

from services.ticket_service import (
    CATEGORIES,
    PRIORITIES,
    STATUSES,
    create_ticket,
    delete_ticket,
    export_tickets,
    get_all_tickets,
    get_dashboard_stats,
    get_ticket,
    search_tickets,
    update_ticket,
)

from services.auth_service import create_user, authenticate_user


app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY


@app.route("/login", methods=["GET", "POST"])
def login():
    """Display and process the login form."""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = authenticate_user(username, password)

        if user:
            session["logged_in"] = True
            session["username"] = user["username"]
            session["role"] = user["role"]

            flash("Login successful.", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Display and process the signup form."""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        try:
            create_user(
                username=username,
                password=password,
                confirm_password=confirm_password,
            )

            flash(
                "Account created successfully. Please login.",
                "success",
            )

            return redirect(url_for("login"))

        except ValueError as error:
            flash(str(error), "danger")

        except Exception:
            flash(
                "An unexpected database error occurred.",
                "danger",
            )

    return render_template("signup.html")


@app.route("/logout")
def logout():
    """Log the user out and clear the session."""

    session.clear()

    flash("You have been logged out successfully.", "success")

    return redirect(url_for("login"))


# Create the database tables when the application starts.
init_db()


@app.route("/")
def dashboard():
    """Display the dashboard with ticket statistics."""

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    stats = get_dashboard_stats()

    return render_template(
        "dashboard.html",
        stats=stats,
    )


@app.route("/tickets")
def tickets():
    """Display tickets with optional search and filters."""

    if not session.get("logged_in"):
        return redirect(url_for("login"))

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


@app.route("/tickets/export")
def export_tickets_page():
    """Export all tickets as a CSV file. Admin only."""

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if session.get("role") != "Admin":
        flash(
            "Access denied. Only Admin users can export tickets.",
            "danger",
        )
        return redirect(url_for("tickets"))

    tickets = export_tickets()

    import csv
    from io import StringIO

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Ticket ID",
        "Title",
        "Description",
        "Category",
        "Priority",
        "Status",
        "Created Date",
        "Assigned To",
    ])

    for ticket in tickets:
        writer.writerow([
            ticket["id"],
            ticket["title"],
            ticket["description"],
            ticket["category"],
            ticket["priority"],
            ticket["status"],
            ticket["created_date"],
            ticket["assigned_to"],
        ])

    response = app.response_class(
        output.getvalue(),
        mimetype="text/csv",
    )

    response.headers["Content-Disposition"] = (
        "attachment; filename=tickets_export.csv"
    )

    return response


@app.route("/tickets/create", methods=["GET", "POST"])
def create_ticket_page():
    """Display and process the create-ticket form."""

    if not session.get("logged_in"):
        return redirect(url_for("login"))

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

    if not session.get("logged_in"):
        return redirect(url_for("login"))

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

    if not session.get("logged_in"):
        return redirect(url_for("tickets"))

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
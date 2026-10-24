import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

import services.create_ticket as ticket_service


class TestTicketService(unittest.TestCase):

    def setUp(self):
        # Create a separate temporary folder for each test.
        self.temp_dir = tempfile.TemporaryDirectory()

        self.base_dir = Path(self.temp_dir.name)

        # Each test uses its own database, not the real project database.
        self.db_path = self.base_dir / "customer.db"

        # Create the database tables and test customer.
        with closing(sqlite3.connect(self.db_path)) as conn:

            # Create the customers table first.
            conn.execute("""
                CREATE TABLE customers (
                    customer_id INTEGER PRIMARY KEY
                )
            """)

            # Add one valid customer for testing.
            conn.execute(
                """
                INSERT INTO customers (customer_id)
                VALUES (?)
                """,
                (1,)
            )

            # Create the support tickets table.
            conn.execute("""
                CREATE TABLE support_tickets (
                    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    issue_title TEXT NOT NULL,
                    issue_description TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

        # Redirect the service to this test's temporary database.
        self.db_path_patch = patch.object(
            ticket_service,
            "DB_PATH",
            self.db_path
        )

        self.db_path_patch.start()

    def tearDown(self):
        # Restore the original database path.
        self.db_path_patch.stop()

        # Close and remove the temporary database.
        self.temp_dir.cleanup()

    def test_create_ticket(self):
        # Create a ticket for a valid customer.
        ticket_id = ticket_service.create_ticket(
            1,
            "Test login issue",
            "Unable to login to my account"
        )

        # Retrieve the newly created ticket.
        ticket = ticket_service.get_ticket(ticket_id)

        self.assertIsNotNone(ticket)
        self.assertEqual(ticket[0], ticket_id)
        self.assertEqual(ticket[1], 1)
        self.assertEqual(ticket[2], "Test login issue")
        self.assertEqual(
            ticket[3],
            "Unable to login to my account"
        )
        self.assertEqual(ticket[4], "Open")

    def test_update_ticket_status(self):
        # Create a ticket first.
        ticket_id = ticket_service.create_ticket(
            1,
            "Test delivery issue",
            "Order has not arrived"
        )

        # Update its status.
        result = ticket_service.update_ticket_status(
            ticket_id,
            "Resolved"
        )

        self.assertTrue(result)

        # Verify that the status was updated.
        ticket = ticket_service.get_ticket(ticket_id)

        self.assertEqual(ticket[4], "Resolved")

    def test_get_customer_tickets(self):
        # Create two tickets for the same customer.
        ticket_service.create_ticket(
            1,
            "First issue",
            "First test description"
        )

        ticket_service.create_ticket(
            1,
            "Second issue",
            "Second test description"
        )

        # Retrieve the customer's tickets.
        tickets = ticket_service.get_customer_tickets(1)

        self.assertEqual(len(tickets), 2)

    def test_get_ticket_not_found(self):
        # This ID does not exist.
        ticket = ticket_service.get_ticket(99999)

        self.assertIsNone(ticket)

    def test_update_missing_ticket(self):
        # Updating a nonexistent ticket should return False.
        result = ticket_service.update_ticket_status(
            99999,
            "Resolved"
        )

        self.assertFalse(result)

    def test_create_invalid_customer(self):
        # Customer 99999 does not exist.
        # The service must raise ValueError instead of creating a ticket.
        with self.assertRaises(ValueError):
            ticket_service.create_ticket(
                99999,
                "Test issue",
                "Testing an invalid customer"
            )


if __name__ == "__main__":
    unittest.main()
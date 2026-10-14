import sqlite3
from pathlib import Path


def create_ticket(customer_id,issue_title,issue_description):
    base_dir = Path(__file__).resolve().parent.parent
    
    db_path = base_dir/ "database" / "customer.db"
    
    conn = sqlite3.connect(db_path)
    
    try :
        cursor = conn.cursor()
        
        cursor.execute(
    """
    INSERT INTO support_tickets
    (customer_id, issue_title,  issue_description , status)
    VALUES(?,?,?,?)
    """,
    (customer_id,issue_title,issue_description,"Open")
        )
        
        ticket_id = cursor.lastrowid
        
        conn.comit()
        
        return ticket_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
        

def get_ticket(ticket_id):
    base_dir = Path(__file__).resolve().parent.parent
    
    db_path = base_dir /"database" /"customer.db"

    conn =sqlite3.connect(db_path)
    
    try :
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM support_tickets WHERE ticket_id = ?",
            (ticket_id,)
            
        )
        ticket = cursor.fetchone()
        return ticket
    
    
        
    finally:
        conn.close()


def update_ticket_status(ticket_id, new_status):
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "database" / "customer.db"

    # Connect to the actual database file
    conn = sqlite3.connect(db_path)

    try:
        cursor = conn.cursor()

        # Update the status of the selected ticket
        cursor.execute(
            "UPDATE support_tickets SET status = ? WHERE ticket_id = ?",
            (new_status, ticket_id)
        )

        # Save the changes to the database
        conn.commit()

        # Return True if a ticket was updated, otherwise False
        return cursor.rowcount > 0

    finally:
        # Always close the database connection
        conn.close()

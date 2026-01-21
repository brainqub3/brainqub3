import sqlite3
import json
from datetime import datetime, timezone

def sync_leads_to_db(leads_data, db_path):
    """
    Sync leads from Zoho CRM API response to SQLite database with history tracking.

    Args:
        leads_data: The JSON response from Zoho CRM API
        db_path: Path to the SQLite database

    Returns:
        dict: Summary of sync operation
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Start sync log entry
    sync_start = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO sync_log (started_at, status)
        VALUES (?, ?)
    """, (sync_start, 'running'))
    sync_id = cursor.lastrowid
    conn.commit()

    inserted_count = 0
    updated_count = 0
    error_count = 0
    errors = []

    try:
        for lead_data in leads_data['data']:
            try:
                lead_id = lead_data['id']

                # Check if lead exists
                cursor.execute("SELECT id, zoho_modified_time FROM leads WHERE id = ?", (lead_id,))
                existing = cursor.fetchone()

                # Prepare description field (store JSON for additional fields)
                additional_data = {
                    'Lead_Status': lead_data.get('Lead_Status'),
                    'Owner': lead_data.get('Owner'),
                    'Created_Time': lead_data.get('Created_Time')
                }

                # Common fields for insert/update
                now = datetime.now(timezone.utc).isoformat()
                fields = {
                    'id': lead_id,
                    'first_name': lead_data.get('First_Name'),
                    'last_name': lead_data.get('Last_Name'),
                    'email': lead_data.get('Email'),
                    'phone': lead_data.get('Phone'),
                    'company': lead_data.get('Company'),
                    'lead_source': lead_data.get('Lead_Source'),
                    'description': json.dumps(additional_data),
                    'created_at': now,
                    'updated_at': now,
                    'zoho_modified_time': lead_data.get('Modified_Time')
                }

                if existing:
                    # Check if data has changed (compare zoho modified time)
                    if existing[1] != fields['zoho_modified_time']:
                        # Update existing lead
                        cursor.execute("""
                            UPDATE leads SET
                                first_name = ?,
                                last_name = ?,
                                email = ?,
                                phone = ?,
                                company = ?,
                                lead_source = ?,
                                description = ?,
                                updated_at = ?,
                                zoho_modified_time = ?
                            WHERE id = ?
                        """, (
                            fields['first_name'],
                            fields['last_name'],
                            fields['email'],
                            fields['phone'],
                            fields['company'],
                            fields['lead_source'],
                            fields['description'],
                            fields['updated_at'],
                            fields['zoho_modified_time'],
                            lead_id
                        ))

                        # Insert history record
                        cursor.execute("""
                            INSERT INTO leads_history (
                                lead_id, first_name, last_name, email, phone,
                                company, lead_source, description,
                                captured_at, change_type
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            lead_id,
                            fields['first_name'],
                            fields['last_name'],
                            fields['email'],
                            fields['phone'],
                            fields['company'],
                            fields['lead_source'],
                            fields['description'],
                            now,
                            'update'
                        ))

                        updated_count += 1
                    # else: No change, skip
                else:
                    # Insert new lead
                    cursor.execute("""
                        INSERT INTO leads (
                            id, first_name, last_name, email, phone,
                            company, lead_source, description,
                            created_at, updated_at, zoho_modified_time
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        lead_id,
                        fields['first_name'],
                        fields['last_name'],
                        fields['email'],
                        fields['phone'],
                        fields['company'],
                        fields['lead_source'],
                        fields['description'],
                        fields['created_at'],
                        fields['updated_at'],
                        fields['zoho_modified_time']
                    ))

                    # Insert history record
                    cursor.execute("""
                        INSERT INTO leads_history (
                            lead_id, first_name, last_name, email, phone,
                            company, lead_source, description,
                            captured_at, change_type
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        lead_id,
                        fields['first_name'],
                        fields['last_name'],
                        fields['email'],
                        fields['phone'],
                        fields['company'],
                        fields['lead_source'],
                        fields['description'],
                        now,
                        'insert'
                    ))

                    inserted_count += 1

            except Exception as e:
                error_count += 1
                errors.append(f"Lead {lead_data.get('id', 'unknown')}: {str(e)}")

        # Update sync log with success
        sync_end = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            UPDATE sync_log SET
                completed_at = ?,
                status = ?,
                records_fetched = ?,
                records_inserted = ?,
                records_updated = ?,
                error_message = ?
            WHERE id = ?
        """, (
            sync_end,
            'completed',
            len(leads_data['data']),
            inserted_count,
            updated_count,
            json.dumps(errors) if errors else None,
            sync_id
        ))

        conn.commit()

        return {
            'sync_id': sync_id,
            'status': 'completed',
            'records_fetched': len(leads_data['data']),
            'records_inserted': inserted_count,
            'records_updated': updated_count,
            'errors': error_count,
            'error_details': errors,
            'started_at': sync_start,
            'completed_at': sync_end
        }

    except Exception as e:
        # Update sync log with failure
        sync_end = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            UPDATE sync_log SET
                completed_at = ?,
                status = ?,
                error_message = ?
            WHERE id = ?
        """, (
            sync_end,
            'failed',
            json.dumps([str(e)]),
            sync_id
        ))
        conn.commit()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Example usage with placeholder data
    # In production, pass the actual Zoho API response to sync_leads_to_db()

    example_response = {
        "data": [
            {
                "id": "000000000000000001",
                "First_Name": "Jane",
                "Last_Name": "Doe",
                "Email": "jane.doe@example.com",
                "Phone": "+1234567890",
                "Company": "Example Corp",
                "Lead_Source": "website",
                "Lead_Status": None,
                "Owner": {
                    "name": "Owner Name",
                    "id": "000000000000000000",
                    "email": "owner@example.com"
                },
                "Created_Time": "2025-01-01T12:00:00+00:00",
                "Modified_Time": "2025-01-01T12:00:00+00:00"
            }
        ],
        "info": {
            "per_page": 200,
            "count": 1,
            "page": 1,
            "more_records": False
        }
    }

    # Update this path to your database location
    db_path = "raw/crm/crm.db"

    result = sync_leads_to_db(example_response, db_path)

    print("=" * 60)
    print("ZOHO CRM SYNC SUMMARY")
    print("=" * 60)
    print(f"Sync ID: {result['sync_id']}")
    print(f"Status: {result['status']}")
    print(f"Records Fetched: {result['records_fetched']}")
    print(f"Records Inserted: {result['records_inserted']}")
    print(f"Records Updated: {result['records_updated']}")
    print(f"Errors: {result['errors']}")
    print(f"Started: {result['started_at']}")
    print(f"Completed: {result['completed_at']}")

    if result['error_details']:
        print("\nError Details:")
        for error in result['error_details']:
            print(f"  - {error}")

    print("=" * 60)

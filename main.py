import os
import time
from datetime import datetime
from PS_scraper import fetch_gen9ou_replays
from PS_json_cleaner import clean_showdown_replay
from db import connectToDB, createDatabase, createTable, insertJSON, printRows

def main():
    # Database configuration (must match db.py)
    HOST = "pokemonshowdowndb.cbiwcoou81sx.us-east-2.rds.amazonaws.com"
    USER = "admin"
    PASSWORD = "PSMVP2025!"
    DATABASE = "pokemonshowdowndb"
    PORT = 3306
    
    # Get current timestamp for logging
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Connect to database
    try:
        print(f"[{timestamp}] Connecting to database...")
        cursor, conn = connectToDB(HOST, USER, PASSWORD, DATABASE, PORT)
        createDatabase(cursor, DATABASE)
        createTable(cursor)
        print(f"[{timestamp}] Successfully connected to database")
    except Exception as e:
        print(f"[{timestamp}] Failed to connect to database: {e}")
        return
    
    # Fetch replays
    replays = fetch_gen9ou_replays()
    
    if not replays:
        print(f"[{timestamp}] No replays found. Exiting.")
        cursor.close()
        conn.close()
        return
    
    print(f"[{timestamp}] Found {len(replays)} replays. Processing...")
    
    # Process each replay
    successful = 0
    failed = 0
    db_successful = 0
    db_failed = 0
    
    for i, replay in enumerate(replays):
        replay_url = replay.get('replay_url')
        if not replay_url:
            print(f"[{timestamp}] Replay {i+1}/{len(replays)}: Missing URL. Skipping.")
            failed += 1
            continue
        
        # Get replay ID from URL
        replay_id = replay_url.split('/')[-1].replace('.json', '')
        
        print(f"[{timestamp}] Processing replay {i+1}/{len(replays)}: {replay_id}")
        
        try:
            # Clean the replay data - now returns data directly
            cleaned_data = clean_showdown_replay(replay_url)
            
            if cleaned_data:
                successful += 1
                print(f"[{timestamp}] ✓ Successfully processed {replay_id}")
                
                # Insert into database directly with the cleaned data
                try:
                    insertJSON(cursor, conn, cleaned_data)
                    db_successful += 1
                    print(f"[{timestamp}] ✓ Successfully uploaded {replay_id} to database")
                except Exception as e:
                    db_failed += 1
                    print(f"[{timestamp}] ✗ Failed to upload {replay_id} to database: {e}")
            else:
                failed += 1
                print(f"[{timestamp}] ✗ Failed to process {replay_id}")
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(1)
            
        except Exception as e:
            failed += 1
            print(f"[{timestamp}] ✗ Error processing {replay_id}: {str(e)}")
    
    # Print database contents (optional)
    print("\nCurrent database contents:")
    printRows(cursor)
    
    # Close database connection
    cursor.close()
    conn.close()
    
    # Print summary
    print(f"\n[{timestamp}] Processing complete")
    print(f"Total replays: {len(replays)}")
    print(f"Successfully processed: {successful}")
    print(f"Failed processing: {failed}")
    print(f"Successfully uploaded to DB: {db_successful}")
    print(f"Failed DB uploads: {db_failed}")

if __name__ == "__main__":
    main()
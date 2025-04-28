import os
import json
import time
from datetime import datetime
from PS_scraper import fetch_gen9ou_replays
from PS_json_cleaner import clean_showdown_replay

def main():
    # Create output directories if they don't exist
    clean_dir = os.path.join("data", "clean")
    os.makedirs(clean_dir, exist_ok=True)
    
    # Get current timestamp for logging
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Fetch replays
    replays = fetch_gen9ou_replays()
    
    if not replays:
        print(f"[{timestamp}] No replays found. Exiting.")
        return
    
    print(f"[{timestamp}] Found {len(replays)} replays. Processing...")
    
    # Process each replay
    successful = 0
    failed = 0
    
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
            output_file = os.path.join(clean_dir, f"{replay_id}_clean.json")
            result = clean_showdown_replay(replay_url, output_file)
            
            if result:
                successful += 1
                print(f"[{timestamp}] ✓ Successfully processed {replay_id}")
            else:
                failed += 1
                print(f"[{timestamp}] ✗ Failed to process {replay_id}")
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(1)
            
        except Exception as e:
            failed += 1
            print(f"[{timestamp}] ✗ Error processing {replay_id}: {str(e)}")
    
    # Print summary
    print(f"\n[{timestamp}] Processing complete")
    print(f"Total replays: {len(replays)}")
    print(f"Successfully processed: {successful}")
    print(f"Failed: {failed}")

"""if __name__ == "__main__":"""

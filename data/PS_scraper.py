import requests
import json
import os
from datetime import datetime
import time

def fetch_gen9ou_replays(page=1, limit=50):
    """
    Fetch recent Gen 9 OU replays from Pokemon Showdown
    
    Args:
        page: Page number (starts at 1)
        limit: Maximum number of replays to fetch per page
        
    Returns:
        List of replay data with only the fields we care about
    """
    url = f"https://replay.pokemonshowdown.com/search.json?format=gen9ou&page={page}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            print(f"No replays found on page {page}")
            return []
            
        
        # Process the data to only include the fields we want
        processed_data = []
        for replay in data:
            replay_id = replay.get('id')
            players = replay.get('players', [])
            rating = replay.get('rating')
            
            if replay_id and players:
                replay_url = f"https://replay.pokemonshowdown.com/{replay_id}.json"
                
                processed_data.append({
                    'players': players,
                    'rating': rating,
                    'replay_url': replay_url
                })
        
        # If we have more results than the limit, trim the list
        if len(processed_data) > limit:
            processed_data = processed_data[:limit]
            
        # Check if we should fetch more pages
        has_more_pages = len(data) > 50
        
        if has_more_pages and page < 3:  # Limit to 3 pages
            next_page_data = fetch_gen9ou_replays(page + 1, limit)
            processed_data.extend(next_page_data)
            
        return processed_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching replays: {e}")
        return []
    
if __name__ == "__main__":
    while True:
        replays = fetch_gen9ou_replays()
        print(replays)
        print('########')
        # TODO: connect to DB and save replays
        # Wait for 15 minutes
        time.sleep(15 * 60)

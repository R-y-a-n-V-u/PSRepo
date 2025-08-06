import os
import time
import json
from datetime import datetime
from PS_scraper import fetch_gen9ou_replays
from PS_json_cleaner import clean_showdown_replay
from POVConverter import convert_replay_for_rl_training


replays = fetch_gen9ou_replays(page=1, limit=10)


# Print the first replay's info
if replays:
    first_replay = replays[0]
    print(f"Players: {first_replay['players']}")
    print(f"Rating: {first_replay['rating']}")
    print(f"Replay URL: {first_replay['replay_url']}")


    # Example replay URL
    replay_url = "https://replay.pokemonshowdown.com/smogtours-gen5ou-59402.json"
    
    # Clean the replay first
    cleaned_data = clean_showdown_replay(replay_url)
    
    if cleaned_data:
        # Convert to first-person perspectives
        first_person_data = convert_replay_for_rl_training(cleaned_data)
        
        # Save the converted data
        for player_name, player_data in first_person_data.items():
            filename = f"{cleaned_data['id']}_{player_name}_fp.json"
            with open(filename, 'w') as f:
                json.dump(player_data, f, indent=2)
            print(f"Saved first-person data for {player_name} to {filename}")
    else:
        print("Failed to clean replay data")
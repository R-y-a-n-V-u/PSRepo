import json
import re
import sys
import requests

def clean_showdown_replay(url):
    """
    Download and clean a Pokemon Showdown replay JSON

    Args:
        url: URL of the replay JSON
    Returns:
        Cleaned replay data as a dictionary
    """
    # Download the JSON
    print(f"Downloading from: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        replay_data = response.json()

        # Extract basic info
        cleaned_data = {
            'id': replay_data.get('id', ''),
            'format': replay_data.get('format', ''),
            'players': replay_data.get('players', []),
        }

        # Clean the log if it exists
        if 'log' in replay_data:
            # Clean and format the log
            clean_log = clean_battle_log(replay_data['log'])
            turn_data = format_as_turns(clean_log)
            cleaned_data.update(turn_data)

        print(f"Successfully cleaned replay {cleaned_data['id']}")
        return cleaned_data

    except Exception as e:
        print(f"Error: {e}")
        return None

def clean_battle_log(log):
    """Clean the battle log by removing chat and timestamps"""
    # Split the log into lines
    lines = log.split('\n')

    # Define what to keep
    keep_patterns = [
        r'^\|switch\|',          # Pokemon switches
        r'^\|move\|',            # Move usage
        r'^\|turn\|',            # Turn markers
        r'^\|-damage\|',         # Damage dealt
        r'^\|-heal\|',           # Healing
        r'^\|-supereffective\|', # Super effective hits
        r'^\|-resisted\|',       # Resisted hits
        r'^\|-immune\|',         # Immunity
        r'^\|faint\|',           # Fainting
        r'^\|-status\|',         # Status conditions
        r'^\|-ability\|',        # Ability activations
        r'^\|-enditem\|',        # Items being consumed
        r'^\|-item\|',           # Items being revealed
        r'^\|start\|',           # Battle start
        r'^\|player\|',          # Player information
        r'^\|teamsize\|',        # Team size
        r'^\|gen\|',             # Generation info
        r'^\|tier\|',            # Tier/format info
        r'^\|win\|',             # Winner info
        r'^\|drag\|',            # Forced switches
        r'^\|replace\|',         # Pokemon replacement
        r'^\|-activate\|',       # Ability/move activations
        r'^\|-weather\|',        # Weather changes
        r'^\|-fieldstart\|',     # Field effects starting
        r'^\|-fieldend\|',       # Field effects ending
        r'^\|-sidestart\|',      # Side effects starting
        r'^\|-sideend\|',        # Side effects ending
        r'^\|-crit\|',           # Critical hits
        r'^\|-miss\|',           # Missed moves
        r'^\|-fail\|',           # Failed moves
        r'^\|-prepare\|',        # Move preparation
        r'^\|-boost\|',          # Stat boosts
        r'^\|-unboost\|',        # Stat decreases
        r'^\|-clearallboost\|',  # Clear all stat changes
        r'^\|-mega\|',           # Mega evolutions
        r'^\|-primal\|',         # Primal reversions
        r'^\|-terastallize\|'    # Terastallizing
    ]

    # Define what to explicitly remove
    remove_patterns = [
        r'^\|t:\|',              # Timestamps
        r'^\|c\|',               # Chat messages
        r'^\|j\|',               # Join messages
        r'^\|l\|',               # Leave messages
        r'^\|upkeep\|',          # Upkeep messages
        r'^\|\|',                # Empty pipes
        r'^\|gametype\|',        # Game type (already in format)
        r'^\|rated\|',           # Rated marker
        r'^\|rule\|',            # Rules (already in format)
        r'^\|inactive\|',        # Inactivity warnings
        r'^\|inactiveoff\|',     # Inactivity timer off
        r'^\|html\|',            # HTML messages
        r'^\|raw\|',             # Raw HTML messages
        r'^\|uhtml\|',           # User HTML
        r'^\|uhtmlchange\|',     # User HTML changes
        r'^\|clearpoke\|',       # Clear Pokemon
        r'^\|poke\|',            # Pokemon in team
        r'^\|request\|',         # Request data
        r'^\|error\|',           # Error messages
        r'^\|popup\|',           # Popup messages
        r'^\|queryresponse\|',   # Query responses
        r'^\|spectator\|',       # Spectator count
        r'^\|choice\|'           # Choice information
    ]

    # Combine patterns
    combined_keep = '|'.join(keep_patterns)
    keep_pattern = re.compile(combined_keep)

    combined_remove = '|'.join(remove_patterns)
    remove_pattern = re.compile(combined_remove)

    # Filter the lines
    cleaned_lines = []

    for line in lines:
        # Skip empty lines
        if not line:
            continue

        # Skip lines that match remove patterns
        if remove_pattern.match(line):
            continue

        # Keep lines that match keep patterns
        if keep_pattern.match(line):
            cleaned_lines.append(line)
        # Also include initialization lines that might not have a pipe prefix
        elif line.startswith('|'):
            # This catches other important battle logs that might not be in our patterns
            cleaned_lines.append(line)

    # Join the cleaned lines back into a log
    return '\n'.join(cleaned_lines)

def format_as_turns(cleaned_log):
    """Format the cleaned log as structured turn data"""
    lines = cleaned_log.split('\n')

    # Initialize variables
    turns = {}
    current_turn = 0  # Start with initialization (turn 0)
    pre_battle = []

    # Process lines
    for line in lines:
        # Check if this is a turn marker
        turn_match = re.match(r'^\|turn\|(\d+)$', line)
        if turn_match:
            current_turn = int(turn_match.group(1))
            if current_turn not in turns:
                turns[current_turn] = []
        elif line.startswith('|start') or line.startswith('|player') or line.startswith('|teamsize') or line.startswith('|gen') or line.startswith('|tier'):
            # These are pre-battle initialization
            pre_battle.append(line)
        elif current_turn in turns:
            # Add this line to the current turn
            turns[current_turn].append(line)
        else:
            # If we haven't hit a turn marker yet, add to pre-battle
            pre_battle.append(line)

    # Structure the data
    return {
        'pre_battle': pre_battle,
        'turns': turns,
    }
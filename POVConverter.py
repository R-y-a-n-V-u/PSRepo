import json
import re
import copy
from typing import Dict, List, Any, Optional

class FirstPersonConverter:
    """
    Convert Pokemon Showdown replay data from spectator view to first-person view
    for reinforcement learning training.
    """
    
    def __init__(self):
        self.player_perspectives = {}
        
    def convert_replay_to_first_person(self, cleaned_replay: Dict) -> Dict[str, Dict]:
        """
        Convert a cleaned replay into first-person perspectives for each player
        
        Args:
            cleaned_replay: Cleaned replay data from the cleaner
            
        Returns:
            Dictionary with player names as keys and their first-person view as values
        """
        players = cleaned_replay.get('players', [])
        if len(players) != 2:
            raise ValueError("Expected exactly 2 players")
            
        # Initialize perspectives for each player
        perspectives = {}
        for i, player in enumerate(players):
            player_id = f"p{i+1}"
            perspectives[player] = {
                'player_name': player,
                'player_id': player_id,
                'opponent_name': players[1-i],
                'opponent_id': f"p{2-i}",
                'format': cleaned_replay.get('format', ''),
                'replay_id': cleaned_replay.get('id', ''),
                'pre_battle': self._convert_pre_battle_to_first_person(
                    cleaned_replay.get('pre_battle', []), player_id
                ),
                'turns': {},
                'game_state': self._initialize_game_state(),
                'action_history': [],
                'observations': []
            }
            
        # Convert each turn
        turns = cleaned_replay.get('turns', {})
        for turn_num, turn_actions in turns.items():
            for player in players:
                player_id = f"p{players.index(player)+1}"
                perspectives[player]['turns'][turn_num] = self._convert_turn_to_first_person(
                    turn_actions, player_id, turn_num
                )
                
        return perspectives
    
    def _initialize_game_state(self) -> Dict:
        """Initialize the game state tracking"""
        return {
            'my_team': {},
            'opponent_team': {},
            'my_active_pokemon': None,
            'opponent_active_pokemon': None,
            'field_conditions': {},
            'weather': None,
            'my_side_conditions': {},
            'opponent_side_conditions': {},
            'turn_number': 0
        }
    
    def _convert_pre_battle_to_first_person(self, pre_battle: List[str], player_id: str) -> List[Dict]:
        """Convert pre-battle information to first-person perspective"""
        fp_pre_battle = []
        
        for line in pre_battle:
            if line.startswith('|player|'):
                # |player|p1|PlayerName|avatar
                parts = line.split('|')
                if len(parts) >= 4:
                    line_player_id = parts[2]
                    player_name = parts[3]
                    
                    if line_player_id == player_id:
                        fp_pre_battle.append({
                            'type': 'player_info',
                            'perspective': 'self',
                            'data': {'name': player_name, 'id': line_player_id}
                        })
                    else:
                        fp_pre_battle.append({
                            'type': 'player_info',
                            'perspective': 'opponent',
                            'data': {'name': player_name, 'id': line_player_id}
                        })
                        
            elif line.startswith('|teamsize|'):
                # |teamsize|p1|6
                parts = line.split('|')
                if len(parts) >= 4:
                    line_player_id = parts[2]
                    team_size = int(parts[3])
                    
                    perspective = 'self' if line_player_id == player_id else 'opponent'
                    fp_pre_battle.append({
                        'type': 'team_size',
                        'perspective': perspective,
                        'data': {'team_size': team_size}
                    })
                    
            else:
                # Keep other pre-battle info as is
                fp_pre_battle.append({
                    'type': 'game_info',
                    'perspective': 'neutral',
                    'data': {'raw': line}
                })
                
        return fp_pre_battle
    
    def _convert_turn_to_first_person(self, turn_actions: List[str], player_id: str, turn_num: int) -> Dict:
        """Convert a turn's actions to first-person perspective"""
        fp_turn = {
            'turn_number': turn_num,
            'my_actions': [],
            'opponent_actions': [],
            'game_events': [],
            'state_changes': [],
            'observations': []
        }
        
        for action in turn_actions:
            fp_action = self._convert_action_to_first_person(action, player_id)
            if fp_action:
                # Categorize the action
                perspective = fp_action.get('perspective', 'neutral')
                
                if perspective == 'self':
                    fp_turn['my_actions'].append(fp_action)
                elif perspective == 'opponent':
                    fp_turn['opponent_actions'].append(fp_action)
                else:
                    fp_turn['game_events'].append(fp_action)
                    
                # Always add to observations for RL training
                fp_turn['observations'].append(fp_action)
                
        return fp_turn
    
    def _convert_action_to_first_person(self, action: str, player_id: str) -> Optional[Dict]:
        """Convert a single action line to first-person perspective"""
        if not action.startswith('|'):
            return None
            
        parts = action.split('|')
        action_type = parts[1] if len(parts) > 1 else ''
        
        # Handle different action types
        if action_type == 'move':
            return self._handle_move_action(parts, player_id)
        elif action_type == 'switch':
            return self._handle_switch_action(parts, player_id)
        elif action_type == 'drag':
            return self._handle_drag_action(parts, player_id)
        elif action_type == 'faint':
            return self._handle_faint_action(parts, player_id)
        elif action_type.startswith('-'):
            return self._handle_battle_effect(parts, player_id)
        else:
            return self._handle_generic_action(parts, player_id)
    
    def _handle_move_action(self, parts: List[str], player_id: str) -> Dict:
        """Handle move actions: |move|p1a: Charizard|Flamethrower|p2a: Blastoise"""
        if len(parts) < 4:
            return {'type': 'move', 'perspective': 'neutral', 'data': {'raw': '|'.join(parts)}}
            
        user = parts[2]
        move = parts[3]
        target = parts[4] if len(parts) > 4 else None
        
        user_player = self._extract_player_from_position(user)
        perspective = 'self' if user_player == player_id else 'opponent'
        
        move_data = {
            'type': 'move',
            'perspective': perspective,
            'data': {
                'user': user,
                'move': move,
                'target': target,
                'user_pokemon': self._extract_pokemon_name(user),
                'target_pokemon': self._extract_pokemon_name(target) if target else None
            }
        }
        
        return move_data
    
    def _handle_switch_action(self, parts: List[str], player_id: str) -> Dict:
        """Handle switch actions: |switch|p1a: Charizard|Charizard, L50, M|100/100"""
        if len(parts) < 4:
            return {'type': 'switch', 'perspective': 'neutral', 'data': {'raw': '|'.join(parts)}}
            
        position = parts[2]
        pokemon_info = parts[3]
        hp_info = parts[4] if len(parts) > 4 else None
        
        switching_player = self._extract_player_from_position(position)
        perspective = 'self' if switching_player == player_id else 'opponent'
        
        return {
            'type': 'switch',
            'perspective': perspective,
            'data': {
                'position': position,
                'pokemon_info': pokemon_info,
                'hp_info': hp_info,
                'pokemon_name': self._extract_pokemon_name_from_info(pokemon_info)
            }
        }
    
    def _handle_drag_action(self, parts: List[str], player_id: str) -> Dict:
        """Handle forced switch actions"""
        return self._handle_switch_action(parts, player_id)  # Same structure as switch
    
    def _handle_faint_action(self, parts: List[str], player_id: str) -> Dict:
        """Handle fainting: |faint|p1a: Charizard"""
        if len(parts) < 3:
            return {'type': 'faint', 'perspective': 'neutral', 'data': {'raw': '|'.join(parts)}}
            
        position = parts[2]
        fainting_player = self._extract_player_from_position(position)
        perspective = 'self' if fainting_player == player_id else 'opponent'
        
        return {
            'type': 'faint',
            'perspective': perspective,
            'data': {
                'position': position,
                'pokemon_name': self._extract_pokemon_name(position)
            }
        }
    
    def _handle_battle_effect(self, parts: List[str], player_id: str) -> Dict:
        """Handle battle effects like damage, healing, status, etc."""
        effect_type = parts[1][1:]  # Remove the '-' prefix
        
        if len(parts) < 3:
            return {'type': effect_type, 'perspective': 'neutral', 'data': {'raw': '|'.join(parts)}}
        
        target = parts[2]
        target_player = self._extract_player_from_position(target)
        perspective = 'self' if target_player == player_id else 'opponent'
        
        effect_data = {
            'type': effect_type,
            'perspective': perspective,
            'data': {
                'target': target,
                'target_pokemon': self._extract_pokemon_name(target),
                'effect_details': parts[3:] if len(parts) > 3 else []
            }
        }
        
        # Add specific parsing for common effects
        if effect_type == 'damage':
            if len(parts) > 3:
                effect_data['data']['new_hp'] = parts[3]
        elif effect_type == 'heal':
            if len(parts) > 3:
                effect_data['data']['new_hp'] = parts[3]
        elif effect_type == 'status':
            if len(parts) > 3:
                effect_data['data']['status_condition'] = parts[3]
                
        return effect_data
    
    def _handle_generic_action(self, parts: List[str], player_id: str) -> Dict:
        """Handle any other action types"""
        return {
            'type': parts[1] if len(parts) > 1 else 'unknown',
            'perspective': 'neutral',
            'data': {'raw': '|'.join(parts)}
        }
    
    def _extract_player_from_position(self, position: str) -> Optional[str]:
        """Extract player ID from position string like 'p1a: Charizard'"""
        if not position:
            return None
        match = re.match(r'^(p[12])', position)
        return match.group(1) if match else None
    
    def _extract_pokemon_name(self, position: str) -> Optional[str]:
        """Extract Pokemon name from position string"""
        if not position or ':' not in position:
            return None
        return position.split(': ')[1].strip()
    
    def _extract_pokemon_name_from_info(self, pokemon_info: str) -> str:
        """Extract Pokemon name from info string like 'Charizard, L50, M'"""
        if not pokemon_info:
            return ''
        return pokemon_info.split(',')[0].strip()

def convert_replay_for_rl_training(cleaned_replay_data: Dict) -> Dict[str, Dict]:
    """
    Main function to convert cleaned replay data to first-person perspectives
    
    Args:
        cleaned_replay_data: Output from the replay cleaner
        
    Returns:
        Dictionary with player names as keys and their RL training data as values
    """
    converter = FirstPersonConverter()
    return converter.convert_replay_to_first_person(cleaned_replay_data)

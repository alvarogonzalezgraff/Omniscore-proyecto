import re
import json

def parse_backup():
    content = open('backup_utf8.sql', 'r', encoding='utf-8').read()
    
    # Extract matches for league = 5
    matches_chunk = content.split('COPY public.matches (id, league_id, home_team_id, away_team_id, matchday, match_date, home_score, away_score, is_finished) FROM stdin;')[1].split('\\.\n')[0]
    premier_matches = {}
    for line in matches_chunk.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) >= 9 and parts[1] == '5': # league_id = 5
            match_id = parts[0]
            premier_matches[match_id] = {
                'home': parts[2],
                'away': parts[3],
                'h_score': int(parts[6]) if parts[6] != '\\N' else 0,
                'a_score': int(parts[7]) if parts[7] != '\\N' else 0,
                'goals': []
            }
            
    # Extract goals
    goals_chunk = content.split('COPY public.goals (id, match_id, team_id, player_name, minute, assist_player_name, is_own_goal, is_penalty) FROM stdin;')[1].split('\\.\n')[0]
    for line in goals_chunk.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) >= 8:
            match_id = parts[1]
            if match_id in premier_matches:
                premier_matches[match_id]['goals'].append(line)

    duplicates = 0
    for match_id, info in premier_matches.items():
        expected = info['h_score'] + info['a_score']
        actual = len(info['goals'])
        if actual > expected:
            print(f"Match {match_id}: Expected {expected}, Actual {actual}")
            duplicates += (actual - expected)
            
    print(f"Total duplicate goals: {duplicates}")

if __name__ == '__main__':
    parse_backup()

import re
import json

def fix_backup():
    content = open('backup_utf8.sql', 'r', encoding='utf-8').read()
    
    # Track teams
    teams_chunk = content.split('COPY public.teams (id, league_id, name, logo_path) FROM stdin;')[1].split('\\.\n')[0]
    teams = {}
    for line in teams_chunk.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) >= 3:
            teams[parts[0]] = parts[2]
            
    matches_chunk = content.split('COPY public.matches (id, league_id, home_team_id, away_team_id, matchday, match_date, home_score, away_score, is_finished) FROM stdin;')[1].split('\\.\n')[0]
    premier_matches = set()
    for line in matches_chunk.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) >= 9 and parts[1] == '5': # league_id = 5
            premier_matches.add(parts[0])

    inventory_players = {}
    def get_invented_player(team_id):
        if team_id not in inventory_players:
            inventory_players[team_id] = f"Jugador Inventado {teams.get(team_id, team_id)}"
        return inventory_players[team_id]

    def process_table(table_name, columns_str, match_index, team_index, player_indices):
        nonlocal content
        
        split_marker = f"COPY public.{table_name} {columns_str} FROM stdin;\n"
        parts = content.split(split_marker)
        if len(parts) < 2:
            return
            
        table_chunk = parts[1].split('\\.\n')[0]
        
        new_lines = []
        seen = set()
        
        for line in table_chunk.strip().split('\n'):
            fields = line.split('\t')
            if len(fields) <= max(match_index, team_index, *player_indices):
                new_lines.append(line)
                continue
                
            match_id = fields[match_index]
            if match_id in premier_matches:
                team_id = fields[team_index]
                
                # Fix players
                for p_idx in player_indices:
                    player_name = fields[p_idx]
                    if player_name == '\\N' or not player_name.strip() or 'Desconocido' in player_name:
                        fields[p_idx] = get_invented_player(team_id)
                
                # Deduplicate
                # For deduplication, we ignore the primary key (fields[0])
                key = tuple(fields[1:])
                if key in seen:
                    continue
                seen.add(key)
            
            new_lines.append('\t'.join(fields))
            
        new_chunk = '\n'.join(new_lines) + '\n'
        content = parts[0] + split_marker + new_chunk + '\\.\n' + parts[1].split('\\.\n', 1)[1]

    # Process goals: id(0), match_id(1), team_id(2), player_name(3), minute(4), assist(5), is_own(6), is_penalty(7)
    process_table("goals", "(id, match_id, team_id, player_name, minute, assist_player_name, is_own_goal, is_penalty)", 1, 2, [3])
    
    # Process cards: id(0), match_id(1), team_id(2), player_name(3), minute(4), card_type(5), reason(6), description(7)
    process_table("cards", "(id, match_id, team_id, player_name, minute, card_type, reason, description)", 1, 2, [3])
    
    # Process substitutions: id(0), match_id(1), team_id(2), player_in(3), player_out(4), minute(5)
    process_table("substitutions", "(id, match_id, team_id, player_in, player_out, minute)", 1, 2, [3, 4])
    
    # Fix the basketball_leagues empty id crash
    content = content.replace('\n\t', '\n\\N\t') # simplistic fix if empty ID was just a tab at start?
    # actually basketball_leagues empty id was: ``
    content = content.replace('COPY public.basketball_leagues (id, name, country, level) FROM stdin;\n\t', 
                              'COPY public.basketball_leagues (id, name, country, level) FROM stdin;\n\\N\t')

    # Save over original Omniscore db
    open('backup_Omniscore_db.sql', 'w', encoding='utf-8').write(content)
    print("Fixed backup_Omniscore_db.sql")

if __name__ == '__main__':
    fix_backup()

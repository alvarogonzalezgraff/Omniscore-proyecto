import re

def fix_newlines():
    content = open('backup_betwin_db.sql', 'r', encoding='utf-8').read()
    
    # Remove any blank lines before \. in COPY blocks
    content = re.sub(r'\n+\\\.', r'\n\\.', content)
    
    open('backup_betwin_db.sql', 'w', encoding='utf-8').write(content)

if __name__ == '__main__':
    fix_newlines()

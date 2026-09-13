import io
import re
with open('app/main.py', 'r', encoding='utf-8') as f: content = f.read()
content = re.sub(r'[\U00010000-\U0010ffff]', '', content)
content = re.sub(r'[\u2600-\u27bf]', '', content)
with open('app/main.py', 'w', encoding='utf-8') as f: f.write(content)

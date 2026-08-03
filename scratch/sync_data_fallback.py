import json
import re

with open('data/campus_data.json', 'r', encoding='utf-8') as f:
    campus_data = json.load(f)

with open('js/campus_data_fallback.js', 'r', encoding='utf-8') as f:
    content = f.read()

campus_str = json.dumps(campus_data, indent=2)
new_content = re.sub(
    r'window\.FALLBACK_CAMPUS_DATA\s*=\s*\{.*?\};',
    f'window.FALLBACK_CAMPUS_DATA = {campus_str};',
    content,
    flags=re.DOTALL
)

with open('js/campus_data_fallback.js', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Synced FALLBACK_CAMPUS_DATA in js/campus_data_fallback.js!')

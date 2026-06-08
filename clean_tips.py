import re

path = r'C:\VSCodeProjects\copilot-studio-credit-budget-monitor\index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove |Source: ... from data-tip attributes (everything from |Source: to the closing quote)
result, count = re.subn(r'\|Source:[^"]*', '', content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(result)

print(f'Removed {count} Source references from tooltips.')

# Verify none remain
remaining = len(re.findall(r'\|Source:', result))
print(f'Remaining |Source: in tooltips: {remaining}')

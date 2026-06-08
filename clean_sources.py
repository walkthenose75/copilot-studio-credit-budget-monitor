import re

with open(r'C:\VSCodeProjects\copilot-studio-credit-budget-monitor\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

original = content

# Internal source fragments to remove (order matters - longer patterns first)
internal_frags = [
    r'Copilot Credit P3 Overview deck,?\s*slide\s*\d+[-\u2013]?\d*\.?\s*',
    r'P3 Overview deck,?\s*slide\s*\d+[-\u2013]?\d*\.?\s*',
    r'P3 deck,?\s*slides?\s*\d+[-\u2013]?\d*\s*(?:benefits)?\s*',
    r'deck slides?\s*\d+[-\u2013]?\d*,?\s*(?:benefits|Price|Where to Purchase|Purchase/Construct|MACC Eligibility|segment descriptions)?\s*',
    r'P3 Overview deck\.?\s*',
    r'P3 deck\.?\s*',
    r',?\s*see Calculation Log',
    r'Calculation Log',
    r'attached How to Purchase P3 image',
    r'attached Linking your Azure Subscription to your Environment (?:process diagram|image)',
]

def clean_source_body(prefix, body):
    """Remove internal fragments from a Source: body, return prefix+cleaned or empty string."""
    for frag in internal_frags:
        body = re.sub(frag, '', body, flags=re.IGNORECASE)

    # Clean up separators
    body = re.sub(r'^\s*[;,]\s*', '', body)
    body = re.sub(r'\s*[;,]\s*$', '', body)
    body = re.sub(r'[;,]\s*[;,]', ';', body)
    body = re.sub(r'^\s*and\s+', '', body, flags=re.IGNORECASE)
    body = re.sub(r'\s+and\s*$', '', body, flags=re.IGNORECASE)
    body = re.sub(r';\s*and\s+', '; ', body, flags=re.IGNORECASE)
    body = re.sub(r',\s*and\s*$', '', body, flags=re.IGNORECASE)
    body = body.strip(' ;,')

    if not body or body.strip() in ('', '.'):
        return ''
    return prefix + body


# 1) Process data-tip Source references: |Source: ... up to closing "
def replace_datatip_source(m):
    prefix = m.group(1)  # "|Source: "
    body = m.group(2)
    result = clean_source_body('Source: ', body)
    if result:
        return '|' + result
    return ''

content = re.sub(
    r'\|(Source:\s*)(.*?)(?=")',
    replace_datatip_source,
    content
)

# 2) Process <p class="src">Source: ...</p>
def replace_src_p(m):
    before = m.group(1)
    prefix = m.group(2)
    body = m.group(3)
    after = m.group(4)
    result = clean_source_body('Source: ', body)
    if result:
        return before + result + after
    return before + after

content = re.sub(
    r'(<p class="src">)(Source:\s*)(.*?)(\.?\s*</p>)',
    replace_src_p,
    content
)

# 3) Clean up "The deck labels" reference
content = re.sub(
    r'The deck labels the PAYG rate "\$0\.01/message"; the licensing guide states the same rate as \$0\.01 per Copilot Credit \(currency renamed from messages in September 2025\)\.',
    'The licensing guide states the rate as $0.01 per Copilot Credit (currency renamed from messages in September 2025).',
    content
)

# 4) Clean up bigquote Source: P3 Overview deck.
content = re.sub(
    r'\s*Source: P3 Overview deck\.',
    '',
    content
)

# 5) Clean up the flowmap-tip and linkflow-tip that reference "attached ... image"
# These are in data-tip attributes and should have been caught, but let's verify
content = re.sub(
    r'Captured from the attached How to Purchase P3 process diagram\.\s*',
    '',
    content
)
content = re.sub(
    r'Captured from the attached Linking your Azure Subscription to your Environment process diagram\.\s*',
    '',
    content
)

# 6) Remove empty Source: remnants
content = re.sub(r'\|Source:\s*"', '"', content)
content = re.sub(r'Source:\s*\.?\s*</p>', '</p>', content)

# 7) Clean up trailing/leading whitespace issues and double spaces
content = re.sub(r'  +', ' ', content)
content = re.sub(r'\|\s*"', '|"', content)  # empty trailing in data-tip

with open(r'C:\VSCodeProjects\copilot-studio-credit-budget-monitor\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify: count remaining internal references
print("Remaining internal references:")
found_any = False
for p in ['P3 deck', 'P3 Overview deck', 'Calculation Log', 'attached How to Purchase', 'attached Linking', 'deck slide']:
    matches = [(i+1, line.strip()) for i, line in enumerate(content.splitlines()) if re.search(p, line, re.IGNORECASE)]
    if matches:
        found_any = True
        print(f'\n  {p}: {len(matches)} occurrences')
        for ln, text in matches[:3]:
            print(f'    L{ln}: {text[:120]}...')

if not found_any:
    print("  None found - all internal references removed!")

# Summary
import difflib
orig_lines = original.splitlines()
new_lines = content.splitlines()
changes = sum(1 for a, b in zip(orig_lines, new_lines) if a != b)
print(f'\nLines changed: {changes}')

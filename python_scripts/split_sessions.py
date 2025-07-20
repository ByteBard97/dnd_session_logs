import os
import re
from pathlib import Path

# Source and destination directories
QUEST_LOGS_DIR = 'quest_logs'
SITE_SRC_DIR = 'site_src'
LOG_FILE = 'split_sessions.log'

# Updated pattern: match any header that starts with '# Session', optionally followed by a number, and any text after
SESSION_HEADER_PATTERN = re.compile(r'^(# Session(?: [0-9]+)?[^\n]*)', re.MULTILINE)

# Ensure the output directory exists
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def log_write(lines):
    with open(LOG_FILE, 'a', encoding='utf-8') as log:
        for line in lines:
            log.write(line + '\n')

def split_markdown_file(src_path, dest_dir, prefix):
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all session/recap headers
    headers = list(SESSION_HEADER_PATTERN.finditer(content))
    if not headers:
        msg = f"No sessions/recaps found in {src_path}"
        print(msg)
        log_write([msg])
        return

    # Add a dummy end marker for the last section
    header_spans = [h.start() for h in headers] + [len(content)]

    log_lines = [f"Splitting {src_path}:"]
    for i in range(len(headers)):
        start = header_spans[i]
        end = header_spans[i+1]
        section = content[start:end].strip()
        # Extract session/recap number or title for filename
        header_line = headers[i].group(1)
        # Try to extract a session/recap number
        match = re.search(r'Session ?([0-9]+)', header_line)
        if match:
            num = match.group(1)
            out_name = f"{prefix}_session_{num}.md"
        else:
            # Fallback: use a slugified version of the header
            slug = re.sub(r'[^a-zA-Z0-9]+', '_', header_line).strip('_').lower()
            out_name = f"{prefix}_{slug}.md"
        out_path = os.path.join(dest_dir, out_name)
        with open(out_path, 'w', encoding='utf-8') as out_f:
            out_f.write(section + '\n')
        print(f"Wrote {out_path}")
        log_lines.append(f"  -> {out_path}")
    log_write(log_lines)

def main():
    log_write(["\n--- Split run ---\n"])
    for group in os.listdir(QUEST_LOGS_DIR):
        group_dir = os.path.join(QUEST_LOGS_DIR, group)
        if not os.path.isdir(group_dir):
            continue
        # Output directory for this group
        out_group_dir = os.path.join(SITE_SRC_DIR, group)
        ensure_dir(out_group_dir)
        for fname in os.listdir(group_dir):
            if fname.endswith('.md') and (fname.startswith('quest_log') or fname.startswith('session_recap')):
                src_path = os.path.join(group_dir, fname)
                prefix = 'log' if 'quest_log' in fname else 'recap'
                split_markdown_file(src_path, out_group_dir, prefix)

if __name__ == '__main__':
    main() 
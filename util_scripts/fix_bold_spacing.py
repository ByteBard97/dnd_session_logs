import os
import re

def fix_bold_spacing(directory):
    # Add space before bold if not preceded by space or newline
    before_pattern = re.compile(r'(?<![ \n])(\*\*[^\*\n]+\*\*)')
    # Add space after bold if not followed by space or newline
    after_pattern = re.compile(r'(\*\*[^\*\n]+\*\*)(?![ \n])')
    log_lines = []
    for root, _, files in os.walk(directory):
        for fname in files:
            if fname.endswith('.md'):
                path = os.path.join(root, fname)
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                changed = False
                for i, line in enumerate(lines):
                    orig_line = line
                    new_line = before_pattern.sub(r' \1', line)
                    new_line = after_pattern.sub(r'\1 ', new_line)
                    if new_line != orig_line:
                        log_lines.append(f"{path}: line {i+1}: {orig_line.strip()} -> {new_line.strip()}")
                        lines[i] = new_line
                        changed = True
                if changed:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
    if log_lines:
        with open('fix_bold_spacing.log', 'w', encoding='utf-8') as log:
            for line in log_lines:
                log.write(line + '\n')
        print(f"Logged fixes to fix_bold_spacing.log")
    else:
        print("No bold spacing fixes needed.")

if __name__ == '__main__':
    fix_bold_spacing('site_src') 
import os

def fix_blank_lines_after_headings(directory):
    log_lines = []
    for root, _, files in os.walk(directory):
        for fname in files:
            if fname.endswith('.md'):
                path = os.path.join(root, fname)
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                new_lines = []
                i = 0
                changed = False
                while i < len(lines):
                    new_lines.append(lines[i])
                    if lines[i].lstrip().startswith('#'):
                        # If not last line and next line is not blank, insert a blank line
                        if i + 1 < len(lines) and lines[i+1].strip() != '':
                            new_lines.append('\n')
                            log_lines.append(f"{path}: line {i+1}: Added blank line after heading: {lines[i].strip()}")
                            changed = True
                    i += 1
                if changed:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
    if log_lines:
        with open('fix_blank_lines_after_headings.log', 'w', encoding='utf-8') as log:
            for line in log_lines:
                log.write(line + '\n')
        print(f"Logged fixes to fix_blank_lines_after_headings.log")
    else:
        print("No blank line fixes needed.")

if __name__ == '__main__':
    fix_blank_lines_after_headings('site_src') 
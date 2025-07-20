import os
import glob

# The DataviewJS snippet to be added to the bottom of markdown files.
# This snippet dynamically finds the current folder and creates Previous/Next links
# on a single line, like: ← Previous | Next →
DATAVIEW_SNIPPET = """
```dataviewjs
const pages = dv.pages(`"${dv.current().file.folder}"`).sort(p => p.file.name);
const currentIndex = pages.findIndex(p => p.file.path === dv.current().file.path);

let nav_links = [];
if (currentIndex > 0) {
    nav_links.push(`[[${pages[currentIndex - 1].file.path}|← Previous]]`);
}
if (currentIndex < pages.length - 1) {
    nav_links.push(`[[${pages[currentIndex + 1].file.path}|Next →]]`);
}

dv.paragraph(nav_links.join(" | "));
```
"""

# A unique part of the snippet to check for its existence in a file.
# This prevents adding the snippet multiple times to the same file.
SNIPPET_CHECK_STRING = 'const pages = dv.pages(`"${dv.current().file.folder}"`)'

def process_markdown_files(target_directories):
    """
    Finds all markdown files in the target directories and appends the
    DataviewJS snippet if it's not already present.
    """
    modified_files = []
    for directory in target_directories:
        # Use recursive=True to find files in subdirectories, just in case.
        for filepath in glob.glob(os.path.join(directory, '**', '*.md'), recursive=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                if SNIPPET_CHECK_STRING in content:
                    continue

                with open(filepath, 'a', encoding='utf-8') as f:
                    # Add a newline before the snippet for good separation.
                    f.write('\n' + DATAVIEW_SNIPPET)
                
                modified_files.append(filepath)

            except Exception as e:
                print(f"Error processing file {filepath}: {e}")

    return modified_files

if __name__ == "__main__":
    # Define the root directories for session logs and recaps for all campaigns.
    base_dir = "site_src"
    campaigns = ["monday", "wednesday", "friday"]
    content_types = ["logs", "recaps"]
    
    target_dirs = [os.path.join(base_dir, camp, c_type) for camp in campaigns for c_type in content_types if os.path.isdir(os.path.join(base_dir, camp, c_type))]
    
    print("Starting to process markdown files...")
    updated_files = process_markdown_files(target_dirs)
    
    if updated_files:
        print('\nSuccessfully added Previous/Next navigation to the following files:')
        for f in updated_files:
            print(f"- {f}")
    else:
        print('\nNo files needed to be updated. All sequential notes already have navigation.')

    print('\nScript finished.') 
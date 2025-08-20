import os

def list_project_structure(root_dir='site_src', output_file='project_structure.txt'):
    """
    Walks through the specified directory and lists all subdirectories and the
    markdown files within them, writing the result to a text file.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Project structure for directory: {root_dir}\n")
            f.write("=" * 40 + "\n\n")

            # First, list the top-level campaign directories
            campaign_dirs = sorted([d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))])
            
            for campaign in campaign_dirs:
                campaign_path = os.path.join(root_dir, campaign)
                f.write(f"Campaign: {campaign}\n")
                f.write("-" * 20 + "\n")
                
                for dirpath, dirnames, filenames in os.walk(campaign_path):
                    # Exclude common non-content directories
                    dirnames[:] = [d for d in dirnames if d.lower() not in ['images', 'assets', 'downloads']]
                    
                    # Calculate depth for indentation
                    relative_path = os.path.relpath(dirpath, campaign_path)
                    if relative_path == '.':
                        indent = ""
                    else:
                        indent = "  " * (relative_path.count(os.sep) + 1)
                        f.write(f"{'  ' * relative_path.count(os.sep)}Subfolder: {os.path.basename(dirpath)}\n")

                    # List all files in the current directory, sorted alphabetically
                    all_files = sorted([file for file in filenames])
                    
                    if not all_files and not dirnames:
                         if relative_path != '.':
                            f.write(f"{indent}(No files or subfolders)\n")
                    
                    for file in all_files:
                        f.write(f"{indent}- {file}\n")
                f.write("\n")
                
        print(f"Project structure has been written to {output_file}")

    except FileNotFoundError:
        print(f"Error: The directory '{root_dir}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    list_project_structure()

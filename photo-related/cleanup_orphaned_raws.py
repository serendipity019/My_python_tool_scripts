import os
from pathlib import Path

def cleanup_orphaned_raws(folder_path: Path) -> None:
    """
    Find and delete orphaned Canon RAW (.CR3) files that have no corresponding JPG file.

    This function scans a directory recursively for .CR3 files and checks if a matching
    .JPG or .jpg file exists in the same location. Any .CR3 file without a corresponding
    JPG is considered an orphan and is deleted. The function provides progress feedback
    and a summary of the cleanup operation.

    Args:
        folder_path (Path): The path to the directory to scan for orphaned RAW files.
            Can be provided as a string or a Path object.

    Returns:
        None: The function prints output to console but does not return any value.

    Raises:
        None: The function handles file-related exceptions internally and continues
            execution. If the folder doesn't exist, it prints an error message and exits.

    Example:
        >>> from pathlib import Path
        >>> cleanup_orphaned_raws(Path("/path/to/photos/"))
        Scanning folder: /path/to/photos

        Deleting orphaned RAW: IMG_1234.CR3
        Deleting orphaned RAW: IMG_5678.CR3

        Cleanup finished. Removed 2 orphaned .CR3 files. Also 45.67MB has free in the disc.

    Notes:
        - Only .CR3 files are processed (Canon RAW format).
        - The search is case-insensitive for file extensions.
        - Both .JPG and .jpg extensions are checked as valid matches.
        - Deleted space is reported in megabytes (MB).
        - The function uses recursive directory traversal (rglob).
    """
    # Convert string path to a Path object
    target_dir = Path(folder_path)

    if not target_dir.exists():
        print(f"Error: The folder '{folder_path} does not exist.")
        return
    
    print(f"Scanning folder: {target_dir.resolve()}\n")
    deleted_count = 0
    total_bytes_deleted = 0

    # Look for all .CR3 files (case-insensitive)
    for cr3_path in target_dir.rglob('*'):
        if cr3_path.is_file() and cr3_path.suffix.upper() == '.CR3':
            # Create the expected matching JPG path
            jpg_path = cr3_path.with_suffix('.JPG')
            # Also check lowercase .jpg just in case
            jpg_path_lower = cr3_path.with_suffix('.jpg')

            # If neither exists, the CR3 is an orphan
            if not jpg_path.exists() and not jpg_path_lower.exists():
                try:
                    cr3_total_bytes = cr3_path.stat().st_size
                    print(f"Deleting orphaned RAW: {cr3_path.name}")
                    cr3_path.unlink() # This delete the file
                    deleted_count += 1
                    total_bytes_deleted += cr3_total_bytes
                except Exception as e:
                    print(f"failed to delete {cr3_path.name}: {e}")
    
    disc_space = round(total_bytes_deleted/ (1024*1024), 2) 
    
    print(f"\nCleanup finished. Removed {deleted_count} orphaned .CR3 files. Also {disc_space}MB has free in the disc.")

# Replace this with the actual path to your photos folder
folder_to_clean = os.getenv("FOLDER_PATH")
cleanup_orphaned_raws(folder_to_clean)    

# Code for the linux bash Script
"""
#!/bin/bash

# Check if a directory was passed as an argument, otherwise use current directory
TARGET_DIR="${1:-.}"

echo "Scanning for orphaned CR3 files in: $TARGET_DIR"
echo "------------------------------------------------"

count=0

# Loop through all .CR3 files (handles spaces in filenames safely)
find "$TARGET_DIR" -type f -iname "*.cr3" | while read -r cr3_file; do
    # Get the file path without the extension (e.g., /path/to/IMG_001)
    base_path="${cr3_file%.*}"
    
    # Check if neither .JPG nor .jpg version exists
    if [ ! -f "${base_path}.JPG" ] && [ ! -f "${base_path}.jpg" ]; then
        echo "Deleting: $cr3_file"
        rm "$cr3_file"
        ((count++))
    fi
done

echo "------------------------------------------------"
echo "Done! Cleaned up matching RAW files."
"""
"""
To use the Bash script:
Make it executable: chmod +x clean_raws.sh

Run it by passing your target directory: ./clean_raws.sh /path/to/your/photos
"""
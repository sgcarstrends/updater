import os
import subprocess
import tempfile


def main(temp_dir, zip_file):
    package_dir = "python"
    excluded_patterns = [
        "**/__pycache__/*",
        "**/bin/*",
        "**/black*/",
        "**/pip*/*",
        "**/pulumi*/*",
        "**/pytest*/*",
    ]

    # Ensure the 'python' directory exists
    os.makedirs(package_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    print(f"Temporary directory created at: {temp_dir}")
    zip_path = os.path.join(temp_dir, zip_file)

    # Construct the exclusion part of the zip command
    exclusion_args = sum([["-x", pattern] for pattern in excluded_patterns], [])

    # Zip the 'python' directory into the temporary directory
    subprocess.run(
        ["zip", "-r", zip_path, package_dir, *exclusion_args], stdout=subprocess.DEVNULL
    )

    print(f"Zipped content is available at {zip_path}")
    print(f"Zipped content size {os.path.getsize(zip_path)}")


if __name__ == "__main__":
    main(tempfile.TemporaryDirectory().name, "python.zip")

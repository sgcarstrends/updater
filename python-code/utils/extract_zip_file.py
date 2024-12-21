from zipfile import ZipFile


def extract_zip_file(zip_file_path: str, extract_to_path: str) -> str:
    with ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(extract_to_path)
        for entry in zip_ref.infolist():
            if not entry.is_dir():
                return entry.filename
        raise FileNotFoundError(
            f"No file was found in the extracted zip file: {zip_file_path}"
        )

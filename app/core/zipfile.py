import zipfile
from os.path import basename

def compact_file(file_path):
    zip_path = f'{file_path}.zip'
    with zipfile.ZipFile(zip_path, mode="w") as archive:
        archive.write(file_path, basename(file_path))
    return zip_path
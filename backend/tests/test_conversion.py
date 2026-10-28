import pytest
from pathlib import Path
from PIL import Image
from app.services.storage_service import validate_file_magic_number
from app.services.conversion_service import convert_to_jpg

def test_jpg_magic_number(tmp_path: Path):
    jpg_file = tmp_path / "test.jpg"
    img = Image.new("RGB", (100, 100), color="blue")
    img.save(jpg_file, "JPEG")

    assert validate_file_magic_number(jpg_file, "jpg")
    assert validate_file_magic_number(jpg_file, "jpeg")
    assert not validate_file_magic_number(jpg_file, "png")
    assert not validate_file_magic_number(jpg_file, "mp4")

def test_png_magic_number(tmp_path: Path):
    png_file = tmp_path / "test.png"
    img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
    img.save(png_file, "PNG")

    assert validate_file_magic_number(png_file, "png")
    assert not validate_file_magic_number(png_file, "jpg")

def test_convert_png_to_jpg(tmp_path: Path):
    png_file = tmp_path / "source.png"
    jpg_file = tmp_path / "output.jpg"

    img = Image.new("RGBA", (100, 100), color=(0, 255, 0, 255))
    img.save(png_file, "PNG")

    res = convert_to_jpg(png_file, jpg_file)
    assert res.exists()
    assert validate_file_magic_number(res, "jpg")


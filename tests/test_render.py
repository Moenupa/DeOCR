import os.path as osp
import random
import string

import pytest
from PIL import Image

from deocr.loader import md2image, text2md


def generate_random_string(length: int):
    """Generates a random string of specified length using letters and digits."""
    characters = string.ascii_letters + string.digits + " " * 20
    return "".join(random.choice(characters) for _ in range(length))


@pytest.mark.parametrize(
    "context,images,expected",
    [
        (
            "Here is an image: <image>",
            ["http://example.com/image1.png"],
            "Here is an image: ![image](http://example.com/image1.png)",
        ),
        (
            "Multiple images: <image> and <image>",
            [
                {"url": "http://example.com/image2.png", "alt": "Example Image"},
                {"image_path": "/local/path/image3.jpg"},
            ],
            "Multiple images: ![Example Image](http://example.com/image2.png) and ![image](/local/path/image3.jpg)",
        ),
        ("No images here.", [], "No images here."),
    ],
)
def test_text2md(context, images, expected):
    result = text2md(context, images)
    assert result == expected


@pytest.mark.parametrize(
    "text,width,height",
    [
        (generate_random_string(1024), 512, 512),
        (generate_random_string(4096), 1024, 1024),
        (generate_random_string(2048), 512, None),
    ],
)
def test_md2image(text, width, height):
    output_path = f".cache/w{width}_h{height}.png"
    md2image(text, output_path, width=width, height=height, overwrite=True)
    assert osp.exists(output_path)

    # check image size is as expected
    with Image.open(output_path) as img:
        img_width, img_height = img.size
        if width is not None:
            assert img_width == width
        if height is not None:
            assert img_height == height

import os.path as osp

import pytest

from deocr.loader import md2image, text2md


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
    "width,height",
    [
        (512, 512),
        (1024, 768),
        (256, 512),
        (512, None),
    ],
)
def test_md2image(width, height):
    md_text = "hello world"
    output_path = f".cache/w{width}_h{height}.png"
    md2image(md_text, output_path, width=width, height=height)
    assert osp.exists(output_path)

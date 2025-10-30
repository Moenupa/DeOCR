import pytest

from deocr.engine.dataio import get_identifier, text2md


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
def test_text2md(context: str, images: list[dict | str], expected: str):
    result = text2md(context, images)
    assert result == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "Sample text for testing.",
            "47846036f75e9778733fe9416aee3a8e",
        ),
        (
            "Another sample text.",
            "977e3a5f3edae58bf2a272967b4bb47d",
        ),
    ],
)
def test_get_identifier(text: str, expected: str):
    actual = get_identifier(text)
    assert actual == expected

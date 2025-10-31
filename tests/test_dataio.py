import pytest

from deocr.engine.dataio import get_identifier, get_image_path, get_n_images, text2md


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


@pytest.mark.parametrize(
    "image_path,expected",
    [
        ("/path/to/0a1addf0f4d7cd3a633241d8062df321/0000000000-0000000001.jpg", 1),
        (
            ".cache/gsm8k/0a0895539aef442771b941785bcee4ee/0000008200-0000008201.jpg",
            8201,
        ),
    ],
)
def test_get_n_images(image_path: str, expected: int):
    actual = get_n_images(image_path)
    assert actual == expected


@pytest.mark.parametrize(
    "folder,i,total,extension,expected",
    [
        (
            "/path/to/0a1addf0f4d7cd3a633241d8062df321",
            0,
            1,
            "jpg",
            "/path/to/0a1addf0f4d7cd3a633241d8062df321/0000000000-0000000001.jpg",
        ),
        (
            ".cache/gsm8k/0a0895539aef442771b941785bcee4ee",
            8200,
            8201,
            "png",
            ".cache/gsm8k/0a0895539aef442771b941785bcee4ee/0000008200-0000008201.png",
        ),
    ],
)
def test_get_image_path(folder: str, i: int, total: int, extension: str, expected: str):
    actual = get_image_path(folder, i, total, extension)
    assert actual == expected

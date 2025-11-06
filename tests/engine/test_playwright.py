import os.path as osp
import random
import shutil
import string

import pytest
from PIL import Image

from deocr.engine.args import RenderArgs
from deocr.engine.playwright.sync_api import markdown2image, transform


@pytest.fixture
def temp_output_dir():
    d = ".cache/pl_sync/"
    yield d


def cleanup_subfolder(subfolder: str, cleanup: bool):
    if cleanup and osp.exists(subfolder):
        shutil.rmtree(subfolder)


SAMPLE_TEXT = r"""# Heading H1
## H2
### H3

---

- *Italic*  
- **Bold**  
  - ***Bold + Italic***  
- ~~Strikethrough~~  

---

1. First
2. Second
   1. Sub‑first
   2. Sub‑second

---

[OpenAI](https://openai.com) and raw links https://google.com

![Placeholder Image](https://picsum.photos/200 "Alt text")

---

Use the `printf()` function or some math $E=mc^2$.

```python
def hello(name: str) -> None:
    print(f"Hello, {name}!")
```

$$
e^{i\pi} + 1 = 0
$$

---

| Column 1 | Column 2 | Column 3 |
|----------|:--------:|---------:|
| Left     | Center   | Right    |
"""


def generate_random_string(length: int = None) -> str:
    """Generates a random string of specified length using letters and digits."""
    if length is None:
        return SAMPLE_TEXT

    characters = string.ascii_letters + string.digits + " " * 20
    return "".join(random.choice(characters) for _ in range(length))


@pytest.mark.parametrize(
    "text,width,height,css,css_path",
    [
        (generate_random_string(), 512, 512, None, None),
        (generate_random_string(), 1024, 1024, None, "css/custom.css"),
        (
            generate_random_string(),
            512,
            None,
            "p { color: red; font-family: sans-serif; }",
            None,
        ),
    ],
)
def test_md2image(
    text: str,
    width: int,
    height: int,
    css: str,
    css_path: str,
    temp_output_dir: str,
    cleanup: bool,
):
    if css_path is not None:
        assert osp.exists(css_path)

    render_args = RenderArgs(
        pagesize=(width, height),
        css=css,
        css_path=css_path,
        dpi=96,
        savePDF=True,
        saveImage=True,
        save_format="jpeg",
        overwrite=True,
    )

    save_paths = markdown2image(
        text,
        temp_output_dir,
        render_args=render_args,
    )
    for each_image in save_paths:
        assert osp.exists(each_image)

        # check image size is as expected
        with Image.open(each_image) as img:
            actual_width, actual_height = img.size
            if width is not None:
                assert actual_width == width
            if height is not None:
                assert actual_height == height

    subfolder = osp.dirname(save_paths[0])
    if len(save_paths) == 1:
        for i in range(1, len(save_paths)):
            assert osp.dirname(save_paths[i]) == subfolder

    cleanup_subfolder(subfolder, cleanup)


@pytest.mark.parametrize(
    "item",
    [
        generate_random_string(),
        {
            "question": generate_random_string(),
            "answer": "42",
        },
    ],
)
def test_transform(item, temp_output_dir: str, cleanup: bool):
    render_args = RenderArgs(
        pagesize=(512, 512),
        dpi=72,
        savePDF=True,
        saveImage=True,
        save_format="jpeg",
        overwrite=True,
    )

    img_paths = transform(
        item=item,
        cache_dir=temp_output_dir,
        render_args=render_args,
    )

    # check output keys
    assert isinstance(img_paths, tuple)

    # check image paths
    assert len(img_paths) > 0
    for img_path in img_paths:
        assert osp.exists(img_path)

    subfolder = osp.dirname(img_paths[0])
    cleanup_subfolder(subfolder, cleanup)

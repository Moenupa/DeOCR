import os.path as osp
import random
import shutil
import string

import pytest
from PIL import Image

from deocr.engine.args import PDFArgs
from deocr.engine.playwright.sync_api import markdown2image


@pytest.fixture
def temp_output_dir():
    d = ".cache/pl_sync/"
    yield d
    shutil.rmtree(d)


SAMPLE_TEXT = r"""# Heading H1
## H2
### H3

---

- *Italic*  
- **Bold**  
- ***Bold + Italic***  
- ~~Strikethrough~~  

---

- Item 1
  - Sub‑item A
  - Sub‑item B
- Item 2

1. First
2. Second
   1. Sub‑first
   2. Sub‑second

---

[OpenAI](https://openai.com)

![Placeholder Image](https://picsum.photos/200 "Alt text")

---

Use the `printf()` function or some math $E=mc^2$.

```python
def hello(name: str) -> None:
    print(f"Hello, {name}!")
```
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
    text: str, width: int, height: int, css: str, css_path: str, temp_output_dir: str
):
    if css_path is not None:
        assert osp.exists(css_path)

    pdf_args = PDFArgs(pagesize=(width, height))

    save_paths = markdown2image(
        text,
        temp_output_dir,
        pdf_args=pdf_args,
        css=css,
        css_path=css_path,
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

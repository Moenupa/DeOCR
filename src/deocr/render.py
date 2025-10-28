import os
import os.path as osp


def text2md(
    context: str,
    images: list[str | dict] = None,
) -> str:
    # convert context to markdown format, embed images if any
    # use 1 to 1 substitution for <image>

    # first assert num of <image> should equal to len(images)
    num_image_tags = context.count("<image>")
    if images is None:
        images = []
    assert num_image_tags == len(images), (
        f"num of <image> tags ({num_image_tags}) should equal to len(images) ({len(images)})"
    )

    # perform 1 to 1 substitution
    for img in images:
        if isinstance(img, str):
            img_md = f"![image]({img})"
        elif isinstance(img, dict) and "url" in img:
            alt = img.get("alt", "")
            url = img["url"]
            img_md = f"![{alt}]({url})"
        elif isinstance(img, dict) and "image_path" in img:
            img_md = f"![image]({img['image_path']})"
        else:
            raise ValueError(f"Unsupported image type: {type(img)}")
        context = context.replace("<image>", img_md, 1)
    return context


def md2image(
    md_text: str,
    out_path: str,
    height: int = 512,
    width: int = 512,
    css_path: str = None,
    overwrite: bool = False,
) -> None:
    # prepare dirs
    parent_dir = osp.dirname(out_path)
    if not osp.exists(parent_dir):
        os.makedirs(parent_dir)

    from .md2img import sync_api as md2img

    # if exists, treat as ready and do nothing
    if not overwrite and osp.exists(out_path):
        return

    md2img.markdown2image(md_text, out_path, width=width, height=height)

from datasets import (
    # Dataset,
    # DatasetDict,
    # Image,
    load_dataset,
)

# from .render import md2image, text2md


# a dataset wrapper that maps a existing hf dataset to DeOCR format
# i.e. text --text2md-> markdown --md2image-> image
class DeOCRDataset:
    def __init__(self):
        raise NotImplementedError


def load_deocr_dataset(*args, **kwargs) -> DeOCRDataset:
    dataset = load_dataset(*args, **kwargs)
    return DeOCRDataset(dataset)

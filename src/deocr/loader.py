from datasets import (
    Dataset,
    DatasetDict,
    Image,
    load_dataset,
)

from .render import md2image, text2md


# a dataset wrapper that maps a existing hf dataset to DeOCR format
# i.e. text --text2md-> markdown --md2image-> image
class DeOCRDataset:
    def __init__(
        self,
        dataset,
        text_column: str = "text",
        md_column: str = "markdown",
        image_column: str = "image",
    ):
        self._text_col = text_column
        self._md_col = md_column
        self._img_col = image_column
        if isinstance(dataset, DatasetDict):
            self._is_dict = True
            self._dataset = None
            self._splits = {
                name: DeOCRDataset(ds, text_column, md_column, image_column)
                for name, ds in dataset.items()
            }
        elif isinstance(dataset, Dataset):
            self._is_dict = False
            self._dataset = dataset
            self._splits = None
        else:
            raise TypeError(
                "DeOCRDataset expects a datasets.Dataset or datasets.DatasetDict"
            )

    def __len__(self):
        if self._is_dict:
            raise TypeError(
                "Length is undefined for a split dict. Access a split first, e.g., ds['train']."
            )
        return len(self._dataset)

    def __getitem__(self, key):
        # For split dict: return the wrapped split
        if self._is_dict:
            return self._splits[key]

        # For single split: support int, slice, and list/tuple of indices
        if isinstance(key, slice):
            rng = range(*key.indices(len(self)))
            return [self[i] for i in rng]
        if isinstance(key, (list, tuple)):
            return [self[i] for i in key]

        ex = self._dataset[key]
        if self._text_col not in ex:
            raise KeyError(
                f"Expected input dataset to contain a '{self._text_col}' column."
            )
        text = ex[self._text_col]
        md = text2md(text)
        img = md2image(md)
        ex[self._md_col] = md
        ex[self._img_col] = img
        return ex

    def __iter__(self):
        if self._is_dict:
            raise TypeError(
                "Iteration is undefined for a split dict. Iterate over a specific split, e.g., ds['train']."
            )
        for i in range(len(self)):
            yield self[i]

    def keys(self):
        if self._is_dict:
            return self._splits.keys()
        return self._dataset.column_names

    def get_split(self, name: str):
        if not self._is_dict:
            raise ValueError("This is not a split dict.")
        return self._splits[name]

    def as_dataset(self, compute_images: bool = False):
        """
        Materialize the wrapped dataset(s) into Hugging Face Dataset(s) with added columns.
        If compute_images is True, will also compute and cast the image column to datasets.Image feature.
        """
        if self._is_dict:
            return DatasetDict(
                {
                    k: v.as_dataset(compute_images=compute_images)
                    for k, v in self._splits.items()
                }
            )

        def add_md_and_maybe_img(example):
            if self._text_col not in example:
                raise KeyError(f"Expected '{self._text_col}' in example.")
            md = text2md(example[self._text_col])
            example[self._md_col] = md
            if compute_images:
                example[self._img_col] = md2image(md)
            return example

        ds2 = self._dataset.map(add_md_and_maybe_img)
        if compute_images:
            try:
                ds2 = ds2.cast_column(self._img_col, Image())
            except Exception:
                # Best-effort casting; leave as-is if casting fails
                pass
        return ds2

    def __getattr__(self, name):
        # Forward to underlying Dataset when applicable
        if name.startswith("_"):
            raise AttributeError
        if self._is_dict:
            raise AttributeError(
                f"'DeOCRDataset' (split dict) has no attribute '{name}'"
            )
        return getattr(self._dataset, name)

    def __repr__(self):
        if self._is_dict:
            return f"DeOCRDataset(Splits: {', '.join(self._splits.keys())})"
        return f"DeOCRDataset(num_rows={len(self)}, columns={list(self._dataset.column_names)})"


def load_deocr_dataset(*args, **kwargs) -> DeOCRDataset:
    dataset = load_dataset(*args, **kwargs)
    return DeOCRDataset(dataset)

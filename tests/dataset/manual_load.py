import pytest
from datasets import DatasetDict, load_dataset

from deocr.engine.args import RenderArgs
from deocr.load import load_deocr_dataset


@pytest.fixture
def gsm8k_args():
    return "openai/gsm8k", "main"


def test_attrs(gsm8k_args: tuple[str, str]):
    # pairwise compare of attrs
    ds_ref = load_dataset(*gsm8k_args)
    ds = load_deocr_dataset(
        *gsm8k_args,
        feed_columns=("question",),
        deocr_column="question_processed",
        deocr_cache_dir=".cache/gsm8k",
        render_args=RenderArgs(
            pagesize=(512, 512),
            dpi=72,
            savePDF=False,
            extension="jpg",
            overwrite=False,
        ),
    )

    assert isinstance(ds_ref, DatasetDict)
    assert isinstance(ds, DatasetDict)

    # Ensure the same splits exist
    assert set(ds_ref.keys()) == set(ds.keys())

    # and each split's attrs are the same
    ATTRS_TO_CHECK = [
        "num_rows",
    ]
    for split in ds_ref.keys():
        # attrs specified by datasets.DatasetDict
        for attr in ATTRS_TO_CHECK:
            expected = getattr(ds_ref[split], attr)
            actual = getattr(ds[split], attr)
            assert expected == actual, (
                f"mismatch in attr: {split}/{attr} {expected} != {actual}"
            )

    print(ds["test"][0])


def test_first_sample(gsm8k_args: tuple[str, str]):
    ds_ref = load_dataset(*gsm8k_args)
    first_sample_ref = ds_ref["test"][0]
    assert isinstance(first_sample_ref, dict)
    expected = {
        "question": "Janet’s ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?",
        "answer": "Janet sells 16 - 3 - 4 = <<16-3-4=9>>9 duck eggs a day.\nShe makes 9 * 2 = $<<9*2=18>>18 every day at the farmer’s market.\n#### 18",
    }
    assert set(first_sample_ref.keys()) == set(expected.keys())
    for exp_key, exp_val in expected.items():
        assert first_sample_ref[exp_key] == exp_val

    ds = load_deocr_dataset(
        *gsm8k_args,
        feed_columns=("question",),
        deocr_column="question_processed",
        deocr_cache_dir=".cache/gsm8k",
        render_args=RenderArgs(
            pagesize=(512, 512),
            dpi=72,
            savePDF=False,
            extension="jpg",
            overwrite=False,
        ),
    )
    first_sample = ds["test"][0]

    EXPECTED_KEYS_AND_TYPES = {
        # this is a list of paths to the images, generated from the question column
        "question_processed": tuple[str],
        # question column should be dropped
        # but answer column is not fed, so should remain
        "question": str,
        "answer": str,
    }

    # Check expected keys exist and types match
    for key, expected_type in EXPECTED_KEYS_AND_TYPES.items():
        assert key in first_sample, f"missing key: {key}"
        val = first_sample[key]
        # special handling for tuple[str]
        if (
            expected_type is tuple[str]
            or getattr(expected_type, "__origin__", None) is tuple
        ):
            assert isinstance(val, (list, tuple)), f"{key}: {type(val)} != tuple"
            assert len(val) > 0, f"{key} should be non-empty"
            for item in val:
                assert isinstance(item, str), f"items of {key} should be str"
        else:
            assert isinstance(val, expected_type), f"{key} should be {expected_type}"

    # answer should match the original dataset's answer
    assert first_sample["answer"] == first_sample_ref["answer"]


if __name__ == "__main__":
    test_attrs(("openai/gsm8k", "main"))
    test_first_sample(("openai/gsm8k", "main"))

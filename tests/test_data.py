from pathlib import Path

import pytest

from ci_cd_ct_demo import model

DATASETS = Path(__file__).parents[1] / "datasets"


@pytest.mark.parametrize("name", ["train.csv", "holdout.csv"])
def test_dataset_has_enough_rows_and_both_labels(name):
    rows = model.load_rows(DATASETS / name)
    assert len(rows) >= 50
    assert {y for _, y in rows} == {0, 1}

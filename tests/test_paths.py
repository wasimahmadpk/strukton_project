import os

from railai.paths import data_paths


def test_data_root_env_rewrites_thesis_paths(tmp_path):
    root = tmp_path / "Groningen"
    os.environ["STRUKTON_DATA_ROOT"] = str(root)
    os.environ.pop("STRUKTON_COUNTERS", None)
    try:
        paths = data_paths()
    finally:
        os.environ.pop("STRUKTON_DATA_ROOT", None)

    assert str(root) in paths.data_file
    assert paths.data_file.endswith(".time.h5")
    assert paths.seg_file.endswith("_seg.csv")
    assert "F:\\UTDATA3OCT" not in paths.data_file

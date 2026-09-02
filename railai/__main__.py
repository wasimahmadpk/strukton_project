"""``python -m railai`` runs the Groningen pipeline; ``python -m railai gui`` opens the UI."""

import sys


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "gui":
        from ui.RailCMS import main as run_gui
        return run_gui()

    from railai.paths import data_paths
    from railai.pipeline import RailDefects

    obj = RailDefects(1)
    obj.anomaly_detection(
        pprocessed_file=data_paths.data_path[4],
        seg_file=data_paths.data_path[2],
        features="RMS",
        sliding_window=2000,
        sub_sampling=128,
        impurity=0.025,
        num_trees=100,
    )


if __name__ == "__main__":
    main()

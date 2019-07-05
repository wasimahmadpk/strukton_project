from ZOES.zoes_parse import Ze
from pathlib import Path, PurePath
# import re
#import pandas as pd
from jname import Loc, get_jname

class Zedf():
    def __init__(self, file_or_dir, run_name=None):
        path = Path(file_or_dir)
        if path.is_dir() and run_name is not None:
            filename = path.joinpath(run_name + '.ze')
        elif path.is_file():
            if path.name[-len('.ze'):] == '.ze':
                filename = PurePath(path)
            else:
                raise ValueError('Wrong file name given.')
        else:
            raise ValueError('Wrong path given.')
        self.filename = Path(filename).resolve()
        self.load_df()


    def load_df(self):
        Ze.load_col_def()  # default column definitions
        ze = Ze(self.filename)
        ze_df = ze.rec.set_index('refcnt')
        ze_df = ze_df[~ze_df.index.duplicated()]
        self.df = ze_df

    def ze_get(self, cnt, col, tolerance=5000):
        idx = self.df.index.get_loc(cnt, method='nearest', tolerance=tolerance)
        return self.df.iloc[idx][col]
import csv
import numpy as np
import pandas as pd


class DefectSeverity:

    def __init__(self, severity_data, ect_datapath):

        self.severity_data = severity_data
        self.ect_datapath = ect_datapath
        self.ectlist = []
        self.crack_depth_list = []

    def get_trend(self):

        with open(self.ect_datapath) as csv_file:
            csv_reader = csv.reader(csv_file)
            line_count = 0
            for row in csv_reader:
                tempStr = ''.join(row)
                if tempStr.startswith('Overzicht Spoorstaafoppervlaktedefecten (treinmeting)') or len(tempStr) == 0:
                    continue
                elif tempStr.startswith('datum'):
                     print(f'Column names are {", ".join(row)}')
                     line_count += 1
                else:
                     line_count += 1
                     tlist = tempStr.split(";")
                     ttlist = [float(x) for x in tlist if len(x) > 0]
                     self.ect_list.append(ttlist)
            print(f'Processed {line_count} lines in POI file.')
            ect_list = np.array(self.ect_list)

            crack_depth_list = []
            tlist = []
            headcheck = pd.DataFrame()
            for i in range(len(ect_list)):
                km_from, km_to, crack_depth = float(ect_list[i, 3]), float(ect_list[i, 4]), float(ect_list[i, 8])
                tempdf = self.severity_data[self.severity_data['position'] <= km_from & self.severity_data['position' <= km_to]]
                if headcheck.shape[0] > 0:
                    crack_depth_list.append(crack_depth)
                    tlist = tlist + [crack_depth] * headcheck.shape[0]
                    headcheck.append(tempdf)

            headcheck = headcheck.assign(depth=crack_depth_list)
        return headcheck
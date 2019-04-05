import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_excel(r'F:\strukton_project\USECT\US_TOTAL.xlsx')
df = df[(df['UIC foutcode'] == 2223) & (df['Been'] == 'L')]
df_tracks = df.groupby('ObjectOms', as_index=False).count().sort_values('Been', ascending=False).head(10)
toptentracks = df_tracks['ObjectOms'].iloc[0:-1].tolist()
dframe = df[df['ObjectOms'].isin(toptentracks)]
dframe = dframe[dframe['ObjectOms'] != 'LEEG'].sort_values('ObjectOms')
dfsorted = dframe.groupby('ObjectOms', as_index=False).apply(lambda x: x.sort_values(['Datum']))
dfsorted.to_excel(r'F:\strukton_project\USECT\US_TOTAL_PROCESSED.xlsx')

track_name = dfsorted['ObjectOms'].iloc[0]
year_list = []
for idx, row in dfsorted.iterrows():
    # print(idx, row['ObjectOms'], row['Datum'])
    year_list.append(row['Datum'].year)

dfmodified = dfsorted.assign(Year=year_list)
dfgrouped = dfmodified.groupby('ObjectOms', as_index=False)
cols = []

for c in range(len(dfmodified.columns)):
    cols.append(dfmodified.columns[c])
count = 0
for table, group in dfgrouped:
    print('\nCREATE TABLE {}('.format(table))
    print('This is group:', group)
    row_data = []
    data_list = []
    for row, data in group.iterrows():
        print('This is row:', row)
        print('This is data:', data)
        for d in range(len(data)):
                if data[d] == '':
                    row_data.append('')
                else:
                    row_data.append(data[d])

        data_list.append(row_data)
        row_data = []
    count = count + 1
    pdf = pd.DataFrame(data_list, columns=cols)
    gpdf = pdf.groupby('Year', as_index=False)
    row_data = []
    data_list = []
    for table, group in gpdf:
        print('\nCREATE TABLE {}('.format(table))
        row_data = []
        for row, data in group.iterrows():
            for d in range(len(data)):
                row_data.append(data[d])
            data_list.append(row_data)
            row_data = []
        pdftrack = pd.DataFrame(data_list, columns=cols)
        km_position = (np.array(pdf['KilometerVan'].iloc[0:-1].tolist()) + np.array(pdf['KilometerTot'].tolist()))/2
        crack_depth = pdf['US_Classificatie'].iloc[0:-1].tolist()
        plt.figure(count)
        plt.plot(km_position, crack_depth, '*')
    break





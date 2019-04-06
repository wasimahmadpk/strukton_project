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

    tname = pdf['ObjectOms'][0]
    if tname == 'WISSEL 1227/1229A':
        tname = 'WISSEL-1227-1229A'
    elif tname == 'WISSEL 1233B/1245A':
        tname = 'WISSEL-1233B-1245A'
    elif tname == 'WISSEL 1263B/1267A':
        tname = 'WISSEL-1263B-1267A'

    gpdf = pdf.groupby('Year', as_index=False)
    row_data = []
    pxlist = []
    pylist = []
    yrlist = []
    for table, group in gpdf:
        print('\nCREATE TABLE {}('.format(table))
        row_data = []
        data_list = []
        for row, data in group.iterrows():
            for d in range(len(data)):
                row_data.append(data[d])
            data_list.append(row_data)
            row_data = []
        plotlist = []
        pdftrack = pd.DataFrame(data_list, columns=cols)
        km_position = pdftrack['KilometerTot'].tolist()
        crack_depth = pdftrack['US_Classificatie'].tolist()
        year = str(pdftrack['Year'][0])
        plotlist.append(km_position)
        plotlist.append(crack_depth)
        pltlist = [[plotlist[j][i] for j in range(len(plotlist))] for i in range(len(plotlist[0]))]
        pltarr = np.array(pltlist)
        sorted = pltarr[pltarr[:, 0].argsort()]
        pxlist.append(sorted[:, 0])
        pylist.append(sorted[:, 1])
        yrlist.append(year)

        plt.figure(count)
        plt.title('Crack Evolution - ' + tname)
        plt.xlabel('Position (km)')
        plt.ylabel('Crack size (mm)')
        crack_evol, = plt.plot(sorted[:, 0], sorted[:, 1], '*', label=year)
    flatx = [val for sublist in pxlist for val in sublist]
    plt.xticks(flatx)
    plt.legend(loc='upper right')
    plt.savefig(r'F:\strukton_project\USECT\{}.png'.format(tname))
    plt.clf()
    plt.close()






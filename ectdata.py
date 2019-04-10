import pandas as pd
import numpy as np
from numpy import random
import matplotlib.pyplot as plt

# ################## generating different colors for stemp plots ########

def get_spaced_colors(n):
    max_value = 16581375  # 255**3
    interval = int(max_value / n)
    colors = [hex(I)[2:].zfill(6) for I in range(1, max_value, interval)]

    return [(int(i[:2], 16), int(i[2:4], 16), int(i[4:], 16)) for i in colors]

#########################################################################


df = pd.read_excel(r'F:\strukton_project\ECT\ExportFile20190404120229.xls')
df_filtered = df[(df['diepteklasse'] != 'Geen gebrek') & (df['links/r'] == 'Rechts')]
df_tracks = df_filtered.groupby('spoortak', as_index=False).count().sort_values('km van', ascending=False).head(10)
toptentracks = df_tracks['spoortak'].iloc[0:-1].tolist()
dframe = df_filtered[df_filtered['spoortak'].isin(toptentracks)]
dfsorted = dframe.groupby('spoortak', as_index=False).apply(lambda x: x.sort_values(['datum']))

track_name = dfsorted['spoortak'].iloc[0]
year_list = []
for idx, row in dfsorted.iterrows():
    # print(idx, row['ObjectOms'], row['Datum'])
    year_list.append(row['datum'].year)

dfmodified = dfsorted.assign(Year=year_list)

# # Processed file saved to local directory
dfmodified.to_excel(r'F:\strukton_project\ECT\ExportFile20190404120229_Processed.xlsx')

dfgrouped = dfmodified.groupby('spoortak', as_index=False)
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
    tname = pdf['spoortak'][0]

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
        km_tot = pdftrack['km tot'].tolist()
        crack_size = pdftrack['diepteklasse'].tolist()
        km_position = []
        crack_depth = []

        for j in range(len(km_tot)):
            kmval1 = pdftrack['km tot'][j].split(",")
            firstval = float(kmval1[0])
            kmval2 = kmval1[1].split("#")
            secval = float(kmval2[0])
            km_position.append(firstval + secval/1000)

        for k in range(len(crack_size)):
            crack_depth.append(float(pdftrack['diepteklasse'][k][-6]) + float(pdftrack['diepteklasse'][k][-4])/10)

        year = str(pdftrack['Year'][0])
        plotlist.append(km_position)
        plotlist.append(crack_depth)
        pltlist = [[plotlist[j][i] for j in range(len(plotlist))] for i in range(len(plotlist[0]))]
        pltarr = np.array(pltlist)
        sorted = pltarr[pltarr[:, 0].argsort()]
        pxlist.append(sorted[:, 0])
        pylist.append(sorted[:, 1])
        yrlist.append(year)
        xax = sorted[:, 0]
        yax = sorted[:, 1]
#
    flatx = [val for sublist in pxlist for val in sublist]
    # create figure
    plt.figure(count)
    plots = []
    proxies = []
    colors = get_spaced_colors(len(pxlist))
    counter = 0

    for x_var, y_var in zip(pxlist, pylist):
        c = color = random.rand(3)
        markerline, stemlines, baseline = plt.stem(x_var, y_var)
        plots.append((markerline, stemlines, baseline))
        c1 = list(colors[counter])
        counter = counter + 1
        plt.title('Crack Evolution - ' + tname)
        plt.xlabel('Position (km)')
        plt.ylabel('Crack size (mm)')
        plt.ylim(0, 5)

        plt.setp(stemlines, linewidth=2, color=c)  # set stems to random colors
        plt.setp(markerline, 'markerfacecolor')  # make points blue

        # plot proxy artist
        h, = plt.plot(1, 1, color=c, zorder=25-count*5)
        proxies.append(h)
    # hide proxies
    plt.legend(proxies, yrlist, loc='best', numpoints=1)
    plt.xticks(flatx)
    plt.tick_params(axis='x', rotation=80)
    for h in proxies:
        h.set_visible(False)
    plt.savefig(r'F:\strukton_project\ECT\{}.png'.format(tname), dpi=300)
    plt.show()
    plt.clf()
    plt.close()



import pandas as pd

df = pd.read_excel(r'F:\strukton_project\USECT\US_TOTAL.xlsx')
df = df[(df['UIC foutcode'] == 2223) & (df['Been'] == 'L')]
df_tracks = df.groupby('ObjectOms', as_index=False).count().sort_values('Been', ascending=False).head(10)
toptentracks = df_tracks['ObjectOms'].iloc[0:-1].tolist()
dframe = df[df['ObjectOms'].isin(toptentracks)]

# frames = [df1, df2, df3, df4]
# bigdata = pd.concat(frames)

# bdata = bigdata[(bigdata.SpoorNummer == 'FC')]
# train_tonnage_data = bdata.groupby(['Voertuig_materieel_type'])
# train_tonnage_mean = train_tonnage_data['Askwaliteit_aslast_ton'].mean()
# train_speed_in_mean = train_tonnage_data['Trein_snelheid_in'].mean()
# train_speed_out_mean = train_tonnage_data['Trein_snelheid_uit'].mean()
# train_no_axles = train_tonnage_data['Askwaliteit_asnummer'].sum()
#
# cols = []
# data_list = []
#
# for c in range(len(bigdata.columns)):
#     cols.append(bigdata.columns[c])
# count = 0
# for table, group in train_tonnage_data:
#     print('\nCREATE TABLE {}('.format(table))
#     row_data = []
#     for row, data in group.iterrows():
#         for d in range(len(data)):
#             if d == 8:
#                 row_data.append(train_speed_in_mean[count])
#             elif d == 9:
#                 row_data.append(train_speed_out_mean[count])
#             elif d == 11:
#                 row_data.append(train_no_axles[count])
#             elif d == 12:
#                 row_data.append(train_tonnage_mean[count])
#             else:
#                 row_data.append(data[d])
#         break
#     count = count + 1
#     data_list.append(row_data)
#
# pdf = pd.DataFrame(data_list, columns=cols)
dframe.to_excel(r'F:\strukton_project\USECT\US_TOTAL_PROCESSED.xlsx')

import pandas as pd

data = pd.read_excel(r'F:\FMLP\dataset\QV Data locatie Almere_Weesp_v3_01.xlsx')
train_tonnage_data = data.groupby(['Trein_snelheid_in'])
train_tonnage_sum = train_tonnage_data[['Askwaliteit_aslast_ton']].sum()

import pandas as pd
import pycountry
from datetime import date

# portugal = pycountry.countries.get(name='United States')
# print(portugal.alpha_2.lower())

path_data = 'https://raw.githubusercontent.com/Dioguini97/DataView_42/main/Data/'
df_players_info = pd.read_csv(path_data + 'NBA_Players_Info.csv')
height = df_players_info[df_players_info['PERSON_ID'] == 2544]['BIRTHDATE'].values[0]
print(height)
print(date.today().year - int(height[:4]) - ((date.today().month, date.today().day) < (int(height[5:7]), int(height[-2:]))))
print(df_players_info.columns)
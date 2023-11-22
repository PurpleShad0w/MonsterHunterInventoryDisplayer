import os
import pandas as pd
import subprocess
import sys
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
os.chdir(os.path.dirname(sys.argv[0]))


subprocess.call("C:/Program Files/010 Editor/010Editor.exe saves/MH3U -template:templates/MH3U.bt -script:scripts/MH3U.1sc -noui")

df = pd.read_csv('saves/MH3U.csv')
df.drop(['Start','Size','Color','Comment'], axis=1, inplace=True)
df.set_index('Name', inplace=True)

df2 = pd.DataFrame(data={'ID':0,'Name':0,'Total Quantity':0,'Quantity in box':0,'Quantity on hunter':0,'Rarity':0},index=(0,1))
df3 = pd.DataFrame(data={'ID':0,'Type':0,'Name':0,'Level':0,'Quantity':0,'Rarity':0,'Category':0,'Subcategory':0},index=(0,1))

index_inv = df.index.get_loc('struct inventory i[1]')
df_inv = df.iloc[index_inv:index_inv+74]
index_pouch = df.index.get_loc('struct pouch i[2]')
df_pouch = df.iloc[index_pouch:index_pouch+98]
index_chest = df.index.get_loc('struct chest i[3]')
df_chest = df.iloc[index_chest:index_chest+3002]
index_box = df.index.get_loc('struct box i[4]')
df_box = df.iloc[index_box:index_box+12002]
df_inv.reset_index(inplace=True)
df_pouch.reset_index(inplace=True)
df_chest.reset_index(inplace=True)
df_box.reset_index(inplace=True)

for i in range(0,74):
    if 'ID' in df_inv.iloc[i,0]:
        id = df_inv.iloc[i,1]
    if 'count' in df_inv.iloc[i,0]:
        count = df_inv.iloc[i,1]
        s = {'ID':id,'Name':0,'Total Quantity':0,'Quantity in box':0,'Quantity on hunter':int(count),'Rarity':0}
        df2 = df2.append(s,ignore_index=True)

for i in range(0,98):
    if 'ID' in df_pouch.iloc[i,0]:
        id = df_pouch.iloc[i,1]
    if 'count' in df_pouch.iloc[i,0]:
        count = df_pouch.iloc[i,1]
        s = {'ID':id,'Name':0,'Total Quantity':0,'Quantity in box':0,'Quantity on hunter':int(count),'Rarity':0}
        df2 = df2.append(s,ignore_index=True)

for i in range(0,3002):
    if 'ID' in df_chest.iloc[i,0]:
        id = df_chest.iloc[i,1]
    if 'count' in df_chest.iloc[i,0]:
        count = df_chest.iloc[i,1]
        s = {'ID':id,'Name':0,'Total Quantity':0,'Quantity in box':int(count),'Quantity on hunter':0,'Rarity':0}
        df2 = df2.append(s,ignore_index=True)

for i in range(0,12002):
    if 'type' in df_box.iloc[i,0]:
        type = df_box.iloc[i,1]
    if 'level_or_slot_count' in df_box.iloc[i,0]:
        level = df_box.iloc[i,1]
    if 'ID' in df_box.iloc[i,0]:
        id = df_box.iloc[i,1]
        s = {'ID':id,'Type':type,'Name':0,'Level':level,'Quantity':1,'Rarity':0,'Category':0,'Subcategory':0}
        df3 = df3.append(s,ignore_index=True)

df2['Total Quantity'] = df2['Quantity in box'] + df2['Quantity on hunter']

df_dict_items = pd.read_csv('dictionaries/MH3U_items.csv')
df_dict_items.set_index('ID', inplace=True)
df_dict_equipment = pd.read_csv('dictionaries/MH3U_equipment.csv')

for i in range(len(df2)):
    id = df2.iloc[i,0]
    try:
        s = {'ID':id,'Name':df_dict_items.loc[int(float(id)),'Name'],'Total Quantity':0,'Quantity in box':0,'Quantity on hunter':0,'Rarity':df_dict_items.loc[int(float(id)),'Rarity']}
        df2 = df2.append(s,ignore_index=True)
    except KeyError:
        continue

for i in range(len(df3)):
    id = df3.iloc[i,0]
    type = df3.iloc[i,1]
    df_temp = df_dict_equipment[(df_dict_equipment['ID'] == int(float(id))) & (df_dict_equipment['Type'] == int(float(type)))]
    try:
        df_temp.reset_index(inplace=True)
        s = {'ID':id,'Type':type,'Name':df_temp.loc[0,'Name'],'Level':0,'Quantity':0,'Rarity':df_temp.loc[0,'Rarity'],'Category':df_temp.loc[0,'Category'],'Subcategory':df_temp.loc[0,'Subcategory']}
        df3 = df3.append(s,ignore_index=True)
    except KeyError:
        continue

df2 = df2.groupby(df2['ID'],sort=False).aggregate({'Name':'last','Total Quantity':'sum','Quantity in box':'sum','Quantity on hunter':'sum','Rarity':'last'})
df3 = df3.groupby([df3['ID'],df3['Type']],sort=False).aggregate({'Name':'last','Level':'first','Quantity':'sum','Rarity':'last','Category':'last','Subcategory':'last'})

df_items = df2
df_equipment = df3
df_general = pd.DataFrame(data={'Name':0,'Quantity':0,'Level':0,'Rarity':0,'Category':0,'Subcategory':0},index=(0,1))

for i in range(len(df_items)):
    s = {'Name':df_items.iloc[i,1],'Quantity':df_items.iloc[i,2],'Level':0,'Rarity':df_items.iloc[i,5],'Category':'Items','Subcategory':0}
    df_general = df_general.append(s,ignore_index=True)

for i in range(len(df_equipment)):
    s = {'Name':df_equipment.iloc[i,2],'Quantity':df_equipment.iloc[i,4],'Level':df_equipment.iloc[i,3],'Rarity':df_equipment.iloc[i,5],'Category':df_equipment.iloc[i,6],'Subcategory':df_equipment.iloc[i,7]}
    df_general = df_general.append(s,ignore_index=True)

df_general = df_general.groupby(df_general['Name']).aggregate({'Quantity':'sum','Level':'max','Rarity':'max','Category':'first','Subcategory':'first'})
df_general.to_csv(r'outputs/MH3U.csv',encoding='utf-8')
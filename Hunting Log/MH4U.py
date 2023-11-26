import mhef.n3ds
import os
import pandas as pd
import shutil
import struct
import sys
import warnings

from argparse import Namespace

warnings.simplefilter(action='ignore', category=FutureWarning)
os.chdir(os.path.dirname(sys.argv[0]))

offset_hex = ['0x12E5C','0x12E5E','0x12E60','0x12E62','0x12E64','0x12E65']
formats = {1:'B', 2:'H', 4:'I', 8:'Q'}
kills, caps, size_small, size_big, big_crown, small_crown = [None] * 68, [None] * 68, [None] * 68, [None] * 68, [None] * 68, [None] * 68

names = pd.read_csv('database/MH4U.csv')['Monster'].tolist()
monsters = pd.read_csv('database/monsters.csv')

df = pd.DataFrame(data={'ID':0,'Size':0,'Type':0,'Variation':0,'Name':0,'Hunted':0,'Captured':0,'Killed':0,'Big Crown':0,'Small Crown':0,'Largest Size':0,'Smallest Size':0},index=(0,1))

save_path = os.getenv('APPDATA')+'\\Citra\\sdmc\\Nintendo 3DS\\00000000000000000000000000000000\\00000000000000000000000000000000\\title\\00040000\\00126300\\data\\00000001\\user1'
shutil.copyfile(save_path, os.path.join(os.getcwd(), 'saves\\user1'))

args = Namespace(mode='d', inputfile='saves/user1', outputfile='saves/user1.bin')
sc = mhef.n3ds.SavedataCipher(mhef.n3ds.MH4G_NA)
sc.decrypt_file(args.inputfile, args.outputfile)

with open('saves/user1.bin', mode='rb') as file:
    for i in range(len(names)):
        offset = int(offset_hex[0], 16) + i*10
        file.seek(offset)
        kills[i] = struct.unpack(formats[2], file.read(2))[0]
    
        offset = int(offset_hex[1], 16) + i*10
        file.seek(offset)
        caps[i] = struct.unpack(formats[2], file.read(2))[0]

        offset = int(offset_hex[2], 16) + i*10
        file.seek(offset)
        size_big[i] = struct.unpack(formats[2], file.read(2))[0]

        offset = int(offset_hex[3], 16) + i*10
        file.seek(offset)
        size_small[i] = struct.unpack(formats[2], file.read(2))[0]

        offset = int(offset_hex[4], 16) + i*10
        file.seek(offset)
        big_crown[i] = struct.unpack(formats[1], file.read(1))[0]

        offset = int(offset_hex[5], 16) + i*10
        file.seek(offset)
        small_crown[i] = struct.unpack(formats[1], file.read(1))[0]

        hunts = kills[i] + caps[i]
        
        if big_crown[i] == 1:
            big_crown[i] = '🥈' 
        elif big_crown[i] == 2:
            big_crown[i] = '👑'
        else:
            big_crown[i] = ''
        
        if small_crown[i] == 1:
            small_crown[i] = '👑'
        else:
            small_crown[i] = ''

        monster_type = monsters[monsters['Monster'] == names[i]]['Type'].tolist()[0]

        monster_var = monsters[monsters['Monster'] == names[i]]['Variation'].tolist()[0]

        s = pd.Series({'ID':i,'Size':'Large','Type':monster_type,'Variation':monster_var,'Name':names[i],'Hunted':hunts,'Captured':caps[i],'Killed':kills[i],'Big Crown':big_crown[i],'Small Crown':small_crown[i],'Largest Size':size_big[i],'Smallest Size':size_small[i]})
        df = pd.concat([df, s.to_frame().T], ignore_index=True)

df = df[df['Name'] != 0]
df.to_csv(r'logs/MH4U.csv',encoding='utf-8',index=False)
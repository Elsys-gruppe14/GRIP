import serial
from serial.tools import list_ports
import time

# Åpener filen med dataen i og kopierer in i en liste
    # er formatert på måten som gjenntar seg for hvær arm
        # *armkode*: [float(grader rotasjon), float(lende til punt fra armens tupp), tupple(koordinater til punkt), float(stort tall som er resultatet av den relevant modifiserte pytagoragen)]

with open('punktdata.txt', 'r') as f:
    contents = f.readlines()

# isolerer rotasjonene ifra strengene de er en del av
rotasjoner = []
for data in contents:
    rotasjoner.append(float(data.split()[1][1:].replace(',','')))


# printer inhold og rotasjoner til terminaler for de-bugging
print('contents:', contents)
print('\nlengths:', rotasjoner)





##### Her bryter ting sammer og er bare en halvferdig itterasjon av å forstå hvorfor serial ikke funker 

for port in list_ports.comports():
    print(port.hwid)


### Formatet på lenghts er [DL, DR]

ser = serial.Serial('', 9600) # Endre navn til porten som arduinoen kommuniserer på

ser.write(f'{rotasjoner}')

print('done')
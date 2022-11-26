
##### Etablerer ting før noe annet skjer

# Importerer bibliotek
import glob
import math

### Variabler for filsøk
seksjonindikator = ';TYPE:Skirt/Brim\n'
koordinatindikator = 'G1 X'
abortindikator = ';TYPE:External perimeter\n'
hightindikator = ';AFTER_LAYER_CHANGE\n'
highttarget = 4.7

injektat = [';PAUSE_PRINT\n', 'M117 Place affix the holder to the print\n', 'M601\n']

punktliste = []


### Variabler for filtrering av punktene

toleranse = 3 # i mm (hvor langt unna den ideelle linjen punktene kan være, hode på holderen har 3 mm på hver side)
breddeskift = 250 # i mm (konstant for å skifte hvor den ideelle linjen til nedre høyre arm går gjennom nedre høyre hjørne, sett slik at y=0 faller på armens posisjon eller lengden mellom hjørnene i horisontal retning)
høydeskift = 210 # i mm (konstant for å skifte hvor den ideelle linjen til øvre venstre arm går gjennom øver venstre hjørne, sett slik at x=0 faller på armens posisjon eller lengden mellom hjørnene i vertikal retning)

# Etablerer lister av punkter som hver arm kan nå
DL_armpunkter = []
DR_armpunkter = []

armlengde = 43 # i mm hvor lang armen strekker seg innover ifra hjørne

tannhjulradius = 16 # i mm hvor stor  radiusen til tannhjulet er



##### Gjør tekstbehandling

### Henter print-fil og lagrer linje for linje i en liste

with open(glob.glob("*.gcode")[0], 'r') as f:
    contents = f.readlines()

# Forbreder til databehandling

size = len(contents)
found = False

### Leser gjennom listen for å finne
        # 1. koordinater til punkter i det første laget
        # 2. injisere koden slik at printen pauser ved ønsket z-verdi slik at armen kan snike seg inn


# Ittererer gjennom alle linjene i koden
for line in range(size):

    # Sjekker om de kommende koodinatene er de vi er interesert i
    if found == False and contents[line] == seksjonindikator:

        print('Koordinatsektion funnet')

        # Ittererer ifra der koordinatene begynner
        for koord in range(line, size):

            # Sjekker om linjen ineholder koordinater
                # om de gjør det er de på formen:
                # "G1 Xttt.ttt Yttt.ttt Et.ttttt"
                    # der t er et sted som kan være fylt med et siffer (dog trenger ikke)
            if contents[koord][:4] == koordinatindikator:

                # Splitter opp og lagrer koordinatene på linjen
                isokoord = contents[koord].split('Y')

                # Cursed streng-oppsplitting
                punktliste.append((float(isokoord[0][4:].replace(' ','')), float(isokoord[1].split(' ')[0])))

                print('Koordinater funnet:')
                print(isokoord, '\n')
            
            # Finner når vi skal stoppe å hente koordinater
            elif contents[koord] == abortindikator:
                found = True
                print('\n\n\nTypeendring funnet; avbryter koordinatinnsamling\n\n\n')
                break # Bryter ut av koord loop

            else:
                print('Ingen verdier funnet\n')
    
    # Finner det stedet hvor vi skal injisere ekstra G-kode
        # De relevante linjene står på formen:
            # ;AFTER_LAYER_CHANGE
            # ;ttt.ttt
                # hvor t er et sted hvor et tall kan være. mellom linjene er det '\n' tegn
    if found == True and contents[line] == hightindikator and float(contents[line+1][1:3]) >= highttarget: # Sjekker om høyde-endringen er over ønsket verdi

        print('Ønsket høydeendring funet\n')
        print('Injiserer pause-komandoer:')

        # injiserer ønsket G-kode
        for injiseringspos in range(len(injektat)):
            
            contents.insert(line+2+injiseringspos, injektat[injiseringspos])
        
        print('Kode injisert\n\nAvslutter...')
        break # break ut av line-løkken

# Override'er den gamle kode-filen med den modifiserte koden 
with open(glob.glob("*.gcode")[0], 'w') as f:
    contents = ''.join(contents)
    f.write(contents)







##### Behandler dataen

print('\n\n\nIdentifiserer brukbare koordinater\n\n\n')

### Filtrerer punktene slika at det er en liste med punkter som kan nås av den hver arm
    # Bare to er implementert, dog om du kan definere en funksjon som beskriver bevegelsen til armen kan det filtreres

for punkt in punktliste:
    if abs(punkt[0]-punkt[1]) <= toleranse and punkt != (0,0):
        DL_armpunkter.append(punkt)

    if abs(punkt[0]+punkt[1]-breddeskift) <= toleranse and punkt != (0,0):
        DR_armpunkter.append(punkt)

# legger til (0,0) til slutten av listen slik at vi er sikker på  at den ikke er tom
DL_armpunkter.append((0,0))
DR_armpunkter.append((0,0))







print('\n\n\nFinner ekstremalpunktene:\n\n')

# Finner ekstremalpunkt for armen nederst til venstre
def newDownLeft(point):
    return -point[0]**2 - point[1]**2

# setter inn første kandidat til å starte med
downLeft = [0, 0, DL_armpunkter[0], newDownLeft(DL_armpunkter[0])]

for punkt in DL_armpunkter:
   if newDownLeft(punkt) >= downLeft[3] and punkt != (0, 0):
        downLeft = [0, 0, punkt, newDownLeft(punkt)]
    






# Finner ekstremalpunkt for armen nederst til høyre
def newDownRight(point):
    return point[0]**2 - point[1]**2

# setter inn første kandidat til å starte med
downRight = [0, 0, DR_armpunkter[0], newDownRight(DR_armpunkter[0])]

# ittererer gjennom alle punktene armen kan nå og velger den som er nærmest
for punkt in DR_armpunkter:
    if newDownRight(punkt) >= downRight[3] and punkt != (0, 0):
        downRight = [0, 0, punkt, newDownRight(punkt)]






# definerer funksjon for å finne lengden til et punkt med differanse i x- og y-retning
def koordlength(justed_x, justed_y):
    temp = math.sqrt(justed_x**2 + justed_y**2)
    print(temp)
    return temp

# Finner hvor langt hvær arm må bevege seg for å nå de optimale punktene, må også justere med skiftene for alle armene som ikke starter i origo
downLeft[1] = koordlength(downLeft[2][0], downLeft[2][1]) - armlengde

downRight[1] = koordlength(downRight[2][0]-breddeskift, downRight[2][1]) - armlengde 






# definerer funksjon for å finne vinkelen til en sirkelsektor med gitt buelengde og radius
def vinkelmengde(lengde):
    return (180*lengde)/(tannhjulradius*math.pi)

# Finner hvor langt hvær arm må rotere servoen for å nå det optimale punktet 
downLeft[0] = vinkelmengde(downLeft[1])

downRight[0] = vinkelmengde(downRight[1]) 

print(DL_armpunkter)
print(DR_armpunkter)






# Om en liste bare har ett element, ble det aldri lagt til noen punter utover det punktet det begynnte med og det er dermed ingen punkter armen kan nå
if len(DL_armpunkter) == 1:
   downLeft = None

if len(DR_armpunkter) == 1:
    downRight = None


# Skriver de optimale punktene i konsollen med de andre beregningene vi har gjort
print('\nPunktet som er mest ned til venstre er:', downLeft, '\n\nPunktet som er mest ned til høyre er:', downRight)



##### Skriver dataen til en ny fil

with open("punktdata.txt", 'w') as f:
    punktdata = [f'DL: {downLeft}', f'DR: {downRight}']
    
    punktdata = '\n'.join(punktdata)
    f.write(punktdata)
import pandas as pd
import helpers

df = pd.read_csv("data.csv", sep=";")

df["Saldo frachtu (PLN)"] = df["Saldo frachtu (PLN)"].apply(lambda x: int(x.replace(',',''))/100)

start_month = 1
end_month = 12

prowizja = 0.2 # to jest ile procent calego ZYSKU idzie jako prowizja dla pracownikow
wspolczynnik_przechylenia = 0 # !!!! 1 > wsp >= 0 !!!!
# to jest wspolczynnik ktory decyduje o tym jaki procent prowizji idzie od razu do glownego spedytora


df["Data załadunku"] = df["Data załadunku"].apply(lambda x : helpers.check_for_month(x, start_month, end_month))
df = df[df["Data załadunku"] == True]

df_shortened = df[["Data załadunku", "Kto wpisał", "Operator2", "Saldo frachtu (PLN)"]]

lista_ktowpisal = {}

lista_przychody_dla_kogo = {}
lista_zespolow = {}

# #TEST
# for index, row in df_shortened.iterrows():
#     if row["Kto wpisał"] not in lista_ktowpisal:
#         lista_ktowpisal[row["Kto wpisał"]] = 0

#KOSZTA
for index, row in df_shortened.iterrows():
    if row["Kto wpisał"] not in lista_przychody_dla_kogo:
        lista_przychody_dla_kogo[row["Kto wpisał"]] = {}

    # Dodaje dict do listy_przychody_dla_kogo, ktory mowi dla kogo ile osoba zarobila
    if pd.isna(row["Operator2"]):
        #tutaj zarabia dla siebie
        if row["Kto wpisał"] not in lista_przychody_dla_kogo[row["Kto wpisał"]]:
            lista_przychody_dla_kogo[row["Kto wpisał"]][row["Kto wpisał"]] = row["Saldo frachtu (PLN)"]
        else:
            lista_przychody_dla_kogo[row["Kto wpisał"]][row["Kto wpisał"]] += row["Saldo frachtu (PLN)"]
    else:
        #tutaj zarabia dla innych
        if row["Operator2"] not in lista_przychody_dla_kogo[row["Kto wpisał"]]:
            lista_przychody_dla_kogo[row["Kto wpisał"]][row["Operator2"]] = row["Saldo frachtu (PLN)"]
        else:
            lista_przychody_dla_kogo[row["Kto wpisał"]][row["Operator2"]] += row["Saldo frachtu (PLN)"]

#PRZYCHODY
for index, row in df_shortened.iterrows():
    if pd.isna(row["Operator2"]):
        if row["Kto wpisał"] not in lista_zespolow:
            lista_zespolow[row["Kto wpisał"]] = {}
    else:
        if row["Operator2"] not in lista_zespolow:
            lista_zespolow[row["Operator2"]] = {}

    if pd.isna(row["Operator2"]):
        if row["Kto wpisał"] not in lista_zespolow[row["Kto wpisał"]]:
            lista_zespolow[row["Kto wpisał"]][row["Kto wpisał"]] = row["Saldo frachtu (PLN)"]
        else:
            lista_zespolow[row["Kto wpisał"]][row["Kto wpisał"]] += row["Saldo frachtu (PLN)"]
    else:
        if row["Kto wpisał"] not in lista_zespolow[row["Operator2"]]:
            lista_zespolow[row["Operator2"]][row["Kto wpisał"]] = row["Saldo frachtu (PLN)"]
        else:
            lista_zespolow[row["Operator2"]][row["Kto wpisał"]] += row["Saldo frachtu (PLN)"]

# print(lista_ktowpisal, len(lista_ktowpisal), "\n")
print("NA PODSTAWIE TEGO - KOSZTA - czyli kto ile zarobił dla jakiego zespołu")
for pracownik in lista_przychody_dla_kogo:
    print(f"{pracownik}: - ", end="")
    for asystent in lista_przychody_dla_kogo[pracownik]:
        print(f"'{asystent}': {lista_przychody_dla_kogo[pracownik][asystent]:.2f}, ", end="")
    print(" ")
print("\n")

print("NA PODSTAWIE TEGO - PRZYCHODY - czyli w danym zespole kto robił ile")
for pracownik in lista_zespolow:
    print(f"{pracownik}: - ", end="")
    for asystent in lista_zespolow[pracownik]:
        print(f"'{asystent}': {lista_zespolow[pracownik][asystent]:.2f}, ", end="")
    print(" ")
print("\n")

#TUTAJ OBLICZENIA
#WYNAGRODZENIA MIESIECZNE!
bazowe_koszta_pracownikow = {
    "PRACOWNIK1":13100,
    "PRACOWNIK2":13100,
    "PRACOWNIK3":13100,
    "PRACOWNIK4":13100,
    "PRACOWNIK5":13100,
    "PRACOWNIK6":13100,
    "PRACOWNIK17":13100,
}

for pracownik in bazowe_koszta_pracownikow:
    bazowe_koszta_pracownikow[pracownik] *= (end_month - start_month + 1) # DOSTOSOWANIE DO DLUGOSCI OKRESU

sumaryczny_koszt_pracownikow = 0
for pracownik in bazowe_koszta_pracownikow:
    sumaryczny_koszt_pracownikow += bazowe_koszta_pracownikow[pracownik]

#Ile z wyplaty kazdego z pracownikow zabrac za kazdego asystenta
lista_kosztow = {}

for asystent in lista_przychody_dla_kogo:
    lista_kosztow[asystent] = {}

    suma = 0
    for pracownik in lista_przychody_dla_kogo[asystent]:
        suma += lista_przychody_dla_kogo[asystent][pracownik]

    for pracownik in lista_przychody_dla_kogo[asystent]:
        lista_kosztow[asystent][pracownik] = lista_przychody_dla_kogo[asystent][pracownik] / suma * bazowe_koszta_pracownikow[pracownik]

print("KOSZTA - ile z kosztu kazdego z asystentow idzie dla kogo")
for asystent in lista_kosztow:
    print(f"{asystent}: - ", end="")
    for pracownik in lista_kosztow[asystent]:
        print(f"'{pracownik}': {lista_kosztow[asystent][pracownik]:.2f}, ", end="")
    print(" ")
print("\n")

#Ile z wyplaty kazdego pracownika zabrac za asystentow
lista_kosztow_finalna = {}

for asystent in lista_kosztow:
    for pracownik in lista_kosztow[asystent]:
        if pracownik not in lista_kosztow_finalna:
            lista_kosztow_finalna[pracownik] = 0
        lista_kosztow_finalna[pracownik] += lista_kosztow[asystent][pracownik]

sorted_lista_kosztow_finalna = dict(sorted(lista_kosztow_finalna.items(), key=lambda item: item[1])) # BY VALUES
# sorted_lista_kosztow_finalna = dict(sorted(lista_kosztow_finalna.items())) # BY KEYS

print("KOSZTA - ile z wyplaty kazdego pracownika kosztowali asystenci + on sam")
for pracownik in sorted_lista_kosztow_finalna:
    print(f"{pracownik}: {sorted_lista_kosztow_finalna[pracownik]:.2f}") 
print("\n")

#Sumaryczne przychody kazdego z zespolow
lista_przychody = {}

for zespol in lista_zespolow:
    suma = 0
    for asystent in lista_zespolow[zespol]:
        suma += lista_zespolow[zespol][asystent]
    lista_przychody[zespol] = suma

sorted_lista_przychody = dict(sorted(lista_przychody.items(), key=lambda item: item[1])) # BY VALUES
# sorted_lista_przychody = dict(sorted(lista_przychody.items())) # BY KEYS

print("PRZYCHODY - ile zarobil kazdy zespol")
for pracownik in sorted_lista_przychody:
    print(f"{pracownik}: {sorted_lista_przychody[pracownik]:.2f}") 
print("\n")

# KTO JAKI PROCENT DOSTAJE Z PROWIZJI W ZESPOLE
lista_wkladu_asystentow = lista_zespolow

for zespol in lista_wkladu_asystentow:
    for asystent in lista_wkladu_asystentow[zespol]:
        lista_wkladu_asystentow[zespol][asystent] /= lista_przychody[zespol] / 100
        lista_wkladu_asystentow[zespol][asystent] = round(lista_wkladu_asystentow[zespol][asystent],2)

print("ZYSKI - kto jaki procent zysku dostaje w zespole (jeszcze bez przechylenia w strone dowodcy zespolu)")
for pracownik in lista_wkladu_asystentow:
    print(f"{pracownik}: {lista_wkladu_asystentow[pracownik]}") 
print("\n")


#ZYSKI dla kazdego zespolu
lista_zyskow = lista_przychody

for zespol in lista_kosztow_finalna:
    lista_zyskow[zespol] = lista_zyskow[zespol] - lista_kosztow_finalna[zespol]

lista_zyskow = dict(sorted(lista_zyskow.items(), key=lambda item: item[1]))

print("ZYSKI = PRZYCHODY - KOSZTY")
for zespol in lista_zyskow:
    print(f"{zespol}: -  {lista_zyskow[zespol]:.2f}", end="")
    print(" ")
print("\n")

# KTO DOKLADNIE ILE POWINIEN DOSTAC PROWIZJI W ZESPOLE
lista_wyplat_asystentow = lista_wkladu_asystentow

# TO JEST ZYSK DLA FIRMY
zysk_dla_firmy = 0

for pracownik in lista_wyplat_asystentow:
    suma_bez_dowodzacego = 0
    for asystent in lista_wyplat_asystentow[pracownik]:
        if asystent != pracownik:
            lista_wyplat_asystentow[pracownik][asystent] *= wspolczynnik_przechylenia
            suma_bez_dowodzacego += lista_wyplat_asystentow[pracownik][asystent]
    lista_wyplat_asystentow[pracownik][pracownik] = 100 - suma_bez_dowodzacego

for pracownik in lista_wyplat_asystentow:
    for asystent in lista_wyplat_asystentow[pracownik]:
        lista_wyplat_asystentow[pracownik][asystent] *= (lista_zyskow[pracownik] / 100)

print("Lista wyplat / zespol")
for zespol in lista_wyplat_asystentow:
    print(f"{zespol}: - ", end="")
    for asystent in lista_wyplat_asystentow[zespol]:
        print(f"'{asystent}': {lista_wyplat_asystentow[zespol][asystent]:.2f}, ", end="")
    print(" ")
print("\n")


#LISTA WYPLAT NA PRACOWNIKA

lista_wyplat_finalna = {}

for pracownik in lista_wyplat_asystentow:
    for asystent in lista_wyplat_asystentow[pracownik]:
        if asystent not in lista_wyplat_finalna:
            lista_wyplat_finalna[asystent] = lista_wyplat_asystentow[pracownik][asystent]
        else:
            lista_wyplat_finalna[asystent] += lista_wyplat_asystentow[pracownik][asystent]


lista_wyplat_finalna = dict(sorted(lista_wyplat_finalna.items(), key=lambda item: item[1]))
print("Lista zyskow dla kazdego pracownika, do tego jeszcze trzeba zabrac prowizje, dodac podstawowa wyplate i zalepic straty")
for pracownik in lista_wyplat_finalna:
    print(f"{[pracownik]}: {lista_wyplat_finalna[pracownik]:.2f}, ")
print("\n")

for pracownik in lista_wyplat_finalna:
    if lista_wyplat_finalna[pracownik] < 0:
        zysk_dla_firmy += lista_wyplat_finalna[pracownik]
        lista_wyplat_finalna[pracownik] = 0
    else:
        zysk_dla_firmy += lista_wyplat_finalna[pracownik] * (1-prowizja)
        lista_wyplat_finalna[pracownik] *= prowizja

print(f"Lista prowizji dla kazdego pracownika, przy prowizji = {prowizja} i wsp. przechylenia = {wspolczynnik_przechylenia}")
for pracownik in lista_wyplat_finalna:
    print(f"{[pracownik]}: {lista_wyplat_finalna[pracownik]:.2f}, ")
print("\n")

for pracownik in lista_wyplat_finalna:
    lista_wyplat_finalna[pracownik] += bazowe_koszta_pracownikow[pracownik]

lista_wyplat_finalna = dict(sorted(lista_wyplat_finalna.items(), key=lambda item: item[1]))

print(f"Wyplaty dla pracownikow przy prowizji = {prowizja} i wsp. przechylenia = {wspolczynnik_przechylenia}")
for pracownik in lista_wyplat_finalna:
    print(f"{[pracownik]}: {lista_wyplat_finalna[pracownik]:.2f}, ")
print("\n")

print(f"Taki jest zysk dla firmy przy prowizji = {prowizja*100}%\n w miesiącach: {start_month} - {end_month}")
print(f"{zysk_dla_firmy:.2f} zł", "\n")

# MOZE ZROBIC WYKRESY, POKAZAC JAK WYGLADA DLA ROZNYCH WARTOSCI PROWIZJI I WSP PRZECHYLENIA

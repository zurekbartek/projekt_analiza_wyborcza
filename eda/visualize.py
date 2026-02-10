import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent 

class MapaPolski:
    def __init__(self, shp_path, pop_path, przyrost_path, partia):
        self.shp_path = shp_path
        self.pop_path = pop_path
        self.przyrost_path = przyrost_path
        self.mapa = gpd.read_file(shp_path)
        self.partia = partia
    
    def map_poparcie(self):
        column_mapping = {
            "ko": 17,
            "konfederacja": 16,
            "nowa lewica": 14,
            "pis": 15,
            "trzecia droga": 13
        }
        key = self.partia.lower()
        if key not in column_mapping:
            raise ValueError(f"Nieznana partia: {self.partia}. Dostępne opcje: KO, Konfederacja, Nowa Lewica, PiS, Trzecia Droga.")
        col_index = column_mapping[key]
        
        pop_df = pd.read_excel(self.pop_path, dtype={'JPT_KOD_JE': str})
        pop_df = pop_df.iloc[:, [0, col_index]]
        pop_df.columns = ['JPT_KOD_JE', 'Poparcie polityczne']
        pop_df['JPT_KOD_JE'] = pop_df['JPT_KOD_JE'].astype(str).str.zfill(4)
        self.mapa['JPT_KOD_JE'] = self.mapa['JPT_KOD_JE'].astype(str).str.zfill(4)
        pop_df['Poparcie polityczne'] = pop_df['Poparcie polityczne'].astype(str).str.replace(',', '.', regex=False)
        pop_df['Poparcie polityczne'] = pd.to_numeric(pop_df['Poparcie polityczne'], errors='coerce')
        
        gdf = self.mapa.merge(pop_df, on='JPT_KOD_JE', how='left')
        bins = np.linspace(0, 60, 13)
        labels = ['0 do 5', '5 do 10', '10 do 15', '15 do 20', '20 do 25', '25 do 30', '30 do 35', '35 do 40', '40 do 45', '45 do 50', '50 do 55', '55 do 60']
        gdf['Poparcie polityczne przedziały'] = pd.cut(gdf['Poparcie polityczne'], bins=bins, labels=labels)
        
        # Zapisz mapę do pliku
        fig, ax = plt.subplots(figsize=(12, 12))
        gdf.plot(column='Poparcie polityczne przedziały', ax=ax, legend=True, cmap='coolwarm',
                 legend_kwds={'title': f"Poparcie polityczne ({self.partia}) w %", 'bbox_to_anchor': (1, 0.5), 'loc': 'center left', 'borderpad': 1})
        plt.title(f"Mapa poparcia politycznego dla {self.partia}, 2023")
        plt.savefig("poparcie.png")  # Zapisz obraz
        plt.close(fig)  # Zamknij wykres, by nie powodować problemów z pamięcią
    
    def map_przyrost(self):
        przy_df = pd.read_excel(self.przyrost_path)
        przy_df = przy_df.iloc[9:, [1, 18]]
        przy_df.columns = ['JPT_KOD_JE', 'Przyrost naturalny']
        przy_df['JPT_KOD_JE'] = przy_df['JPT_KOD_JE'].astype(str).str.zfill(4)
        self.mapa['JPT_KOD_JE'] = self.mapa['JPT_KOD_JE'].astype(str).str.zfill(4)
        przy_df['Przyrost naturalny'] = pd.to_numeric(przy_df['Przyrost naturalny'], errors='coerce')
        
        gdf = self.mapa.merge(przy_df, on='JPT_KOD_JE', how='left')
        bins = [-np.inf, -20, -15, -13, -10, -8, -5, -3, -1, 0, 1, 2, 3, 4, 5, 7, 8, 9, 11, 12, np.inf]
        labels = ['<-20', '-20 do -15', '-15 do -13', '-13 do -10', '-10 do -8', '-8 do -5', '-5 do -3', '-3 do -1', '-1 do 0', '0 do 1', '1 do 2', '2 do 3', '3 do 4', '4 do 5', '5 do 7', '7 do 8', '8 do 9', '9 do 11', '11 do 12', '>12']
        gdf['Przyrost naturalny przedział'] = pd.cut(gdf['Przyrost naturalny'], bins=bins, labels=labels)
        
        fig, ax = plt.subplots(figsize=(12, 12))
        gdf.plot(column='Przyrost naturalny przedział', ax=ax, legend=True, cmap='coolwarm',
                 legend_kwds={'title': "Przyrost naturalny\nna 1000 mieszkańców", 'bbox_to_anchor': (1, 0.5), 'loc': 'center left', 'borderpad': 1})
        plt.title("Mapa przyrostu naturalnego w gminach, rok 2023")
        plt.savefig("przyrost.png")
        plt.close(fig)
    def map_wygrana_partia(self):
        # Mapa indeksów kolumn -> nazwy partii
        column_mapping = {
            "ko": 17,
            "konfederacja": 16,
            "nowa lewica": 14,
            "pis": 15,
            "trzecia droga": 13
        }

        # Wczytaj dane z Excela
        pop_df = pd.read_excel(self.pop_path, dtype={'JPT_KOD_JE': str})

        # Pobierz kolumnę z kodem + kolumny partii
        cols = [0] + list(column_mapping.values())
        pop_df = pop_df.iloc[:, cols]

        # Nadaj własne nazwy
        pop_df.columns = ['JPT_KOD_JE'] + list(column_mapping.keys())

        # Standaryzacja kodów i konwersja wartości
        pop_df['JPT_KOD_JE'] = pop_df['JPT_KOD_JE'].astype(str).str.zfill(4)
        for partia in column_mapping.keys():
            pop_df[partia] = pop_df[partia].astype(str).str.replace(',', '.', regex=False)
            pop_df[partia] = pd.to_numeric(pop_df[partia], errors='coerce')

        # Znajdź partię z największym poparciem w każdym powiecie
        pop_df['Wygrana partia'] = pop_df[column_mapping.keys()].idxmax(axis=1)

        # Połącz z mapą
        self.mapa['JPT_KOD_JE'] = self.mapa['JPT_KOD_JE'].astype(str).str.zfill(4)
        gdf = self.mapa.merge(pop_df[['JPT_KOD_JE', 'Wygrana partia']], on='JPT_KOD_JE', how='left')

        # Zapisz wynik do obiektu
        self.gdf_wygrana = gdf  

        # Zdefiniuj kolory dla partii
        party_colors = {
            "ko": "blue",
            "pis": "red",
            "konfederacja": "purple",
            "nowa lewica": "pink",
            "trzecia droga": "green"
        }

        # Rysowanie mapy
        fig, ax = plt.subplots(figsize=(12, 12))
        gdf.plot(column='Wygrana partia', ax=ax,
                 color=gdf['Wygrana partia'].map(party_colors), legend=False)

        # Dodanie legendy ręcznej
        from matplotlib.lines import Line2D
        legend_elements = [Line2D([0], [0], marker='o', color='w',
                                  label=party, markerfacecolor=color, markersize=10)
                           for party, color in party_colors.items()]
        ax.legend(handles=legend_elements, title="Wygrana partia",
                  bbox_to_anchor=(1, 0.5), loc='center left')

        plt.title("Mapa zwycięskich partii w powiatach, 2023")
        plt.savefig("wygrana_partia.png", bbox_inches="tight")

        plt.close(fig)


    def map_partia_przyrost(self, partia):
        if not hasattr(self, "gdf_wygrana"):
            raise ValueError("Najpierw uruchom map_wygrana_partia(), żeby obliczyć zwycięskie partie.")

        # Wczytaj dane o przyroście
        przy_df = pd.read_excel(self.przyrost_path)
        przy_df = przy_df.iloc[9:, [1, 18]]
        przy_df.columns = ['JPT_KOD_JE', 'Przyrost naturalny']
        przy_df['JPT_KOD_JE'] = przy_df['JPT_KOD_JE'].astype(str).str.zfill(4)
        przy_df['Przyrost naturalny'] = pd.to_numeric(przy_df['Przyrost naturalny'], errors='coerce')

        # Połącz z wynikami zwycięskich partii
        gdf = self.gdf_wygrana.merge(przy_df, on='JPT_KOD_JE', how='left')

        # Filtrowanie tylko powiatów wybranej partii
        gdf = gdf[gdf['Wygrana partia'] == partia.lower()]

        # Klasyfikacja przyrostu
        def classify(val):
            if pd.isna(val):
                return "brak danych"
            elif val > 0:
                return "dodatni"
            elif val < 0:
                return "ujemny"
            else:
                return "zerowy"

        gdf['Typ przyrostu'] = gdf['Przyrost naturalny'].apply(classify)

        # --- Liczenie procentu dodatnich wśród powiatów tej partii ---
        total = len(gdf[gdf['Typ przyrostu'] != "brak danych"])
        dodatnie = len(gdf[gdf['Typ przyrostu'] == "dodatni"])
        procent_dodatnich = (dodatnie / total * 100) if total > 0 else 0

        # Kolory dla typów
        color_map = {
            "dodatni": "blue",
            "ujemny": "green",
            "zerowy": "grey",
            "brak danych": "lightgrey"
        }

        # Rysowanie mapy
        fig, ax = plt.subplots(figsize=(12, 12))
        gdf.plot(column='Typ przyrostu', ax=ax,
                 color=gdf['Typ przyrostu'].map(color_map), legend=False)

        # Legenda
        from matplotlib.lines import Line2D
        legend_elements = [Line2D([0], [0], marker='o', color='w',
                                  label=label, markerfacecolor=color, markersize=10)
                           for label, color in color_map.items()]
        ax.legend(handles=legend_elements, title=f"Przyrost naturalny\n({partia})",
                  bbox_to_anchor=(1, 0.5), loc='center left')

        plt.title(f"{partia.upper()}, pierwsze miejsce w tych powiatach")
        plt.savefig(f"przyrost_{partia}.png", bbox_inches="tight")
        plt.close(fig)

        # Opcjonalnie zwróć dane statystyczne
        return {"partia": partia, "powiaty_wygrane": total,
                "powiaty_dodatnie": dodatnie, "procent": procent_dodatnich}
    def map_druga_partia(self):
        # Wczytaj dane
        pop_df = pd.read_excel(self.pop_path, dtype={'JPT_KOD_JE': str})
        column_mapping = {
            "ko": 17,
            "konfederacja": 16,
            "nowa lewica": 14,
            "pis": 15,
            "trzecia droga": 13
        }
        cols = [0] + list(column_mapping.values())
        pop_df = pop_df.iloc[:, cols]
        pop_df.columns = ['JPT_KOD_JE'] + list(column_mapping.keys())

        # Standaryzacja
        pop_df['JPT_KOD_JE'] = pop_df['JPT_KOD_JE'].astype(str).str.zfill(4)
        for partia in column_mapping.keys():
            pop_df[partia] = pop_df[partia].astype(str).str.replace(',', '.', regex=False)
            pop_df[partia] = pd.to_numeric(pop_df[partia], errors='coerce')

        # Wyznacz drugą partię
        def druga_partia(row):
            vals = row.dropna().nlargest(2)
            if len(vals) < 2:
                return None
            return vals.index[-1]

        pop_df['Druga partia'] = pop_df[column_mapping.keys()].apply(druga_partia, axis=1)

        # Dopisanie do self.gdf_wygrana (tak samo jak przy 3 miejscu)
        self.gdf_wygrana = self.gdf_wygrana.merge(
            pop_df[['JPT_KOD_JE', 'Druga partia']], on='JPT_KOD_JE', how='left'
        )

        # Kolory
        party_colors = {
            "ko": "blue",
            "pis": "red",
            "konfederacja": "purple",
            "nowa lewica": "pink",
            "trzecia droga": "green"
        }

        # Rysowanie mapy
        fig, ax = plt.subplots(figsize=(12, 12))
        self.gdf_wygrana.plot(
            column='Druga partia',
            ax=ax,
            color=self.gdf_wygrana['Druga partia'].map(party_colors),
            legend=False
        )

        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w',
                label=partia, markerfacecolor=color, markersize=10)
            for partia, color in party_colors.items()
        ]
        ax.legend(handles=legend_elements, title="Druga partia",
                bbox_to_anchor=(1, 0.5), loc='center left')

        plt.title("Mapa drugiej partii w powiatach, 2023")
        plt.savefig("druga_partia.png", bbox_inches="tight")
        plt.close(fig)



    def map_trzecia_partia(self):
        pop_df = pd.read_excel(self.pop_path, dtype={'JPT_KOD_JE': str})

        column_mapping = {
            "ko": 17,
            "konfederacja": 16,
            "nowa lewica": 14,
            "pis": 15,
            "trzecia droga": 13
        }
        cols = [0] + list(column_mapping.values())
        pop_df = pop_df.iloc[:, cols]
        pop_df.columns = ['JPT_KOD_JE'] + list(column_mapping.keys())

        pop_df['JPT_KOD_JE'] = pop_df['JPT_KOD_JE'].astype(str).str.zfill(4)
        for partia in column_mapping.keys():
            pop_df[partia] = pop_df[partia].astype(str).str.replace(',', '.', regex=False)
            pop_df[partia] = pd.to_numeric(pop_df[partia], errors='coerce')

        pop_df['Trzecia partia'] = pop_df[column_mapping.keys()].apply(
            lambda row: row.nlargest(3).index[-1], axis=1
        )

        # dopisanie do gdf_wygrana zamiast tworzenia nowego gdf
        self.gdf_wygrana = self.gdf_wygrana.merge(
            pop_df[['JPT_KOD_JE', 'Trzecia partia']], on='JPT_KOD_JE', how='left'
        )

        # rysowanie mapy
        party_colors = {"ko": "blue", "pis": "red", "konfederacja": "purple",
                        "nowa lewica": "pink", "trzecia droga": "green"}

        fig, ax = plt.subplots(figsize=(12, 12))
        self.gdf_wygrana.plot(column='Trzecia partia', ax=ax,
                            color=self.gdf_wygrana['Trzecia partia'].map(party_colors), legend=False)

        from matplotlib.lines import Line2D
        legend_elements = [Line2D([0], [0], marker='o', color='w',
                                label=partia, markerfacecolor=color, markersize=10)
                        for partia, color in party_colors.items()]
        ax.legend(handles=legend_elements, title="Trzecia partia",
                bbox_to_anchor=(1, 0.5), loc='center left')

        plt.title("Mapa trzeciej partii w powiatach, 2023")
        plt.savefig("trzecia_partia.png", bbox_inches="tight")
        plt.close(fig)



    def map_przyrost_partia_miejsce(self, partia, miejsce=2):
        if miejsce not in [2, 3]:
            raise ValueError("Miejsce musi być 2 lub 3.")

        # Dopasowanie nazw kolumn
        col_map = {2: "Druga partia", 3: "Trzecia partia"}
        col_name = col_map[miejsce]

        if not hasattr(self, "gdf_wygrana"):
            raise ValueError("Najpierw uruchom map_wygrana_partia(), druga/trzecia partia, żeby obliczyć dane.")
        if col_name not in self.gdf_wygrana.columns:
            raise ValueError(f"Brak kolumny {col_name} w danych (uruchom map_{miejsce}_partia()).")

        # Wczytaj dane o przyroście
        przy_df = pd.read_excel(self.przyrost_path)
        przy_df = przy_df.iloc[9:, [1, 18]]
        przy_df.columns = ['JPT_KOD_JE', 'Przyrost naturalny']
        przy_df['JPT_KOD_JE'] = przy_df['JPT_KOD_JE'].astype(str).str.zfill(4)
        przy_df['Przyrost naturalny'] = pd.to_numeric(przy_df['Przyrost naturalny'], errors='coerce')

        # Połącz
        gdf = self.gdf_wygrana.merge(przy_df, on='JPT_KOD_JE', how='left')

        # Filtrowanie dla partii
        gdf = gdf[gdf[col_name].str.lower() == partia.lower()]

        # Klasyfikacja przyrostu
        def classify(val):
            if pd.isna(val): return "brak danych"
            elif val > 0: return "dodatni"
            elif val < 0: return "ujemny"
            else: return "zerowy"

        gdf['Typ przyrostu'] = gdf['Przyrost naturalny'].apply(classify)

        # Statystyki
        total = len(gdf[gdf['Typ przyrostu'] != "brak danych"])
        dodatnie = len(gdf[gdf['Typ przyrostu'] == "dodatni"])
        procent_dodatnich = (dodatnie / total * 100) if total > 0 else 0

        # Kolory
        color_map = {"dodatni": "blue", "ujemny": "green", "zerowy": "grey", "brak danych": "lightgrey"}

        # Rysowanie
        fig, ax = plt.subplots(figsize=(12, 12))
        gdf.plot(column='Typ przyrostu', ax=ax,
                color=gdf['Typ przyrostu'].map(color_map), legend=False)

        from matplotlib.lines import Line2D
        legend_elements = [Line2D([0], [0], marker='o', color='w',
                                label=label, markerfacecolor=color, markersize=10)
                        for label, color in color_map.items()]
        ax.legend(handles=legend_elements, title=f"Przyrost naturalny\n({partia}, {col_name})",
                bbox_to_anchor=(1, 0.5), loc='center left')

        plt.title(f"{partia.upper()} – powiaty na {miejsce} miejscu")
        plt.savefig(f"przyrost_{partia}_miejsce{miejsce}.png", bbox_inches="tight")
        plt.close(fig)

        return {"partia": partia, "miejsce": miejsce, "powiaty": total,
                "powiaty_dodatnie": dodatnie, "procent": procent_dodatnich}



if __name__ == "__main__":
    # Podaj własne ścieżki do plików
    shp_path = ROOT_DIR / "mapa" / "A02_Granice_powiatow.shp"
    pop_path = ROOT_DIR / "mapa" / "wyniki_gl_na_listy_po_powiatach_proc_sejm_utf8.xlsx"
    przyrost_path = ROOT_DIR / "mapa" / "Tabela_III.xls"
    
    mapa = MapaPolski(shp_path, pop_path, przyrost_path, "Nowa lewica")
    
    # Wywołanie metody tworzącej mapę poparcia politycznego dla konkretnej partii
    mapa.map_poparcie() # lub "konfederacja", "Nowa Lewica", "PiS", "Trzecia Droga"
    
    mapa.map_przyrost()
    
    mapa.map_wygrana_partia()


    mapa.map_partia_przyrost("pis")   # pokaże tylko powiaty PISu
    mapa.map_partia_przyrost("ko")    # tylko KO
    stat = mapa.map_partia_przyrost("pis")
    stat2 = mapa.map_partia_przyrost("ko")
    #print(stat)
    #print(stat2)
    mapa.map_druga_partia()
    mapa.map_trzecia_partia()
    mapa.map_przyrost_partia_miejsce("konfederacja", 3)  # pokaże tylko powiaty Konfederacji na 3 miejscu
    mapa.map_przyrost_partia_miejsce("trzecia droga", 3)  # pokaże tylko powiaty Trzeciej Drogi na 2 miejscu
    mapa.map_przyrost_partia_miejsce("ko", 2)  # pokaże tylko powiaty Nowej Lewicy na 2 miejscu
    mapa.map_przyrost_partia_miejsce("trzecia droga", 2)  # pokaże tylko powiaty Trzeciej Drogi na 2 miejscu
    mapa.map_przyrost_partia_miejsce("pis", 2)
    mapa.map_przyrost_partia_miejsce("konfederacja", 2)  # pokaże tylko powiaty Konfederacji na 2 miejscu
    mapa.map_przyrost_partia_miejsce("ko", 3)  # pokaże tylko powiaty KO na 3 miejscu
    mapa.map_przyrost_partia_miejsce("nowa lewica", 3)  # pokaże tylko powiaty Nowej Lewicy na 3 miejscu
    #wyjeb naglowki
   
# 2024-RP-3E-RHEED
Python aplikace pro zpracování obrazových dat z měření RHEED při růstu MBE nebo charakterizaci materiálů a tenkých vrstev

## Autoři
- **Marek Bílý** - Výpočetní algoritmy, teorie
- **Jan Schreiber** - Výpočetní algoritmy, dokumentace
- **Marek Švec** - GUI, dokumentace

_Supervize_
- **Fyzikální ústav AV ČR, v.v.i.**
    -   Ing. Filip Křížek Ph.D. 
    -   Dr. Dominik Kriegner
 
## Dokumentace

Návod pro spuštění a navigaci v prvním okně GUI:

- **Systémové požadavky**  
  - Operační systém - Windows, macOS nebo Linux  
  - Python verze - 3.9 a novější  
  - Python knihovny - PyQt5 nebo PySide6 (instalace knihoven pomocí `pip install qtpy PyQt5`)

- **Instalace**  

    **1. Klonování repozitáře**
    ```
    gc//github.com/gyarab/2024-RP-3E-RHEED.git
    cd 2024-RP-3E-RHEED
    ```
    
    **2. Vytvoření a aktivace virtuálního prostředí**
    ```
    python -m venv venv
    source venv/bin/activate  # Na Windows: venv\Scripts\activate
    ```

    **3. Instalace požadovaných knihoven**
    ```
    pip install -r requirements.txt
    ```
    Pokud requirements.txt neexistuje, nainstalujte knihovny ručně:

    ```
    pip install silx opencv-python PyQt5 numpy h5py matplotlib
    ```

- **Závislosti**  

    Seznam závislostí projektu: [Dependency Graph](https://github.com/gyarab/2024-RP-3E-RHEED/network/dependencies)
  

- **Spuštění**  
  - V terminálu napište `python src/main.py`

- **Návod k použití**
  Program umožňuje buď nahrát již zachycený soubor, nebo spustit kameru pro živý záznam. Před zahájením živého záznamu je ale nutné správně nastavit camera port a další         
  parametry kamery, což se provádí v menu baru. Po načtení souboru nebo spuštění kamery se video zobrazí ve vizualizačním okně.
  Snímky v okně je možné pozastavit nebo posouvat mezi nimi. Vizualizační okno lze dále upravovat pomocí nástrojů v toolbaru, kde je možné ovládat jeho zobrazení a pracovat s 
  dalšími funkcemi, například s histogramem.


  ROI lze přidávat a spravovat v ROI manageru umístěném v pravém horním rohu. Analýza vybraných ROI pak probíhá ve statistickém okně v pravém dolním rohu, kde lze zjistit 
  průměrnou hodnotu intenzity (mean) a využít možnost zobrazení časových průběhů v grafu timeseries plot.



- Prezentace: [`.PPTX`](docs/presentation_5-12)

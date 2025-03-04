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
  - Otevřete si složku GUI v terminálu a napište `python main.py`

- **Navigace**  
  Zatím fungují pouze funkce spojené s obrazci - pomocí tlačítka **"New"** si uživatel vygeneruje nový tvar, spolu s ním se mu pod tlačítkem **"New"** objeví i panel vlastností tohoto tvaru kde je obrázek barvy, název barvy a tlačítko **"analyze"**, toto tlačítko vygeneruje zatím nevyužité okno, do kterého bude v budoucnu umístěn graf spolu s dalšími funkcemi.

  Tvary jsou k dispozici zatím dva: obdélník a kruhová výseč. Na levém panelu se dají měnit hodnoty jejich vlastností a při stisku pravého tlačítka se dá tvar změnit nebo vymazat.


- Prezentace: [`.PPTX`](docs/presentation_5-12)

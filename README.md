# Argus_py

Argus_py es un prototipo de analizador de inteligencia que aplica l\u00f3gica difusa para detectar contradicciones b\u00e1sicas en textos. El sistema extrae afirmaciones sujeto-verbo-objeto mediante spaCy y propaga el efecto de los ataques entre ellas con distintas t-normas.

## Advertencias metodol\u00f3gicas

- El an\u00e1lisis se limita a la estructura ret\u00f3rica; no intenta inferir intenciones ni verificar hechos.
- Las puntuaciones deben interpretarse por separado de los datos originales y de cualquier evaluaci\u00f3n narrativa.

## Instalaci\u00f3n

```bash
pip install spacy rapidfuzz
python -m spacy download en_core_web_sm
```

## Ejecuci\u00f3n

Analizar un archivo de texto y generar un `analysis.json` asociado:

```bash
python argus.py ruta/al/texto.txt --tnorm min
```

El resultado se guarda como `ruta/al/texto.analysis.json`.

Tambi\u00e9n puede invocarse directamente el m\u00f3dulo principal:

```bash
python fls_intel_analyzer.py entrada.txt salida.json --t-norm min
```

## Uso en VS Code

1. Abra la carpeta del proyecto en VS Code mediante **File > Open Folder**.
2. Seleccione un intérprete de Python con los paquetes de `requirements.txt` desde la paleta de comandos (`Ctrl+Shift+P` → **Python: Select Interpreter**).
3. Si existe un archivo `.vscode/launch.json`, ejecute sus configuraciones desde la vista **Run and Debug**.

En la terminal integrada (`Terminal` → `New Terminal`), instale las dependencias y descargue los modelos de spaCy:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```


## Pruebas

Se incluye un texto de ejemplo en `tests/sample_text.txt` y un resultado de referencia en `tests/sample_output.json`.
Para ejecutar la prueba automatizada:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
pytest
```

La prueba genera un JSON con nodos y aristas, verificando que los valores `Aa`, `Ar` y `Au` de cada nodo suman 1.

Para regenerar manualmente el archivo de salida de ejemplo:

```bash
python fls_intel_analyzer.py tests/sample_text.txt tests/sample_output.json
```

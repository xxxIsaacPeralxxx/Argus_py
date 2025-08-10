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


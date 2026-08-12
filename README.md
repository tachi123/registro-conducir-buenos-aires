# Clase B — Quiz del Registro (Marcos Paz)

Simulador de examen teórico para la licencia de conducir Clase B, basado en la
batería oficial de preguntas (IF-2019-33101289-GDEBA-DPPYSVMGGP). Sitio 100%
estático: HTML/CSS/JS + JSON, desplegable en GitHub Pages.

## Modos

- **Quiz**: examen simulado de 40 preguntas (señales ≤ 8, generales ≥ 20,
  auto ≥ 6), con feedback obligatorio después de cada respuesta
  (correcto/incorrecto + fundamento + fuentes) y aprobación con 30/40.
- **Estudio**: navegación del banco completo con filtros por categoría y
  subcategoría; revelado de respuesta con fundamento y fuentes; placeholders
  con link a la página del PDF para preguntas con imagen.
- **Materiales**: 5 fichas-resumen de los materiales de estudio con su peso
  relativo en el examen.

## Arquitectura

```
cuestionario.pdf ──pdftotext──► scripts/extract.py ──► data/_extracted/*.json
                                                 │  (gitignored, regenerable)
        data/authoring/*.json (respuestas autoradas) ▼
        scripts/build_bank.py ──► data/{generales,senales,auto}.json + index.json
        scripts/confidence_report.py ──► data/review-queue.json (gitignored)
        scripts/review_gate.py  ← gate de deploy (falla si falta/vacío el banco)
index.html ──js/app.js──► js/views.js ──► js/quiz-engine.js (muestreo puro ESM)
```

Los archivos `data/{generales,senales,auto}.json` + `data/index.json` +
`data/materials.json` son la fuente de verdad publicada: contienen cada
pregunta con su `correct`, `fundamento`, `sources[]`, `confidence` y
`reviewed`. Las respuestas NO se regeneran desde el PDF — se autoran a mano.

## Desarrollo

```bash
# reconstruir la estructura desde la extracción (solo estructura, no respuestas)
python scripts/extract.py            # lee %TEMP%\opencode\cuestionario.txt
python scripts/build_bank.py         # fusiona extracción + data/authoring
python scripts/confidence_report.py  # genera data/review-queue.json (informativo)

python -m pytest       # pipeline + schema + parity (node)
npx vitest run         # engine + app + views + index
```

## Autorar respuestas (data/authoring)

Cada pregunta del banco necesita `correct`, `fundamento`, `sources[]`,
`confidence` (0–1) y `reviewed`. Regla de confianza: `confidence: 0.9` solo
cuando la respuesta se sigue directamente del material citado (manual, ANSV,
ley 24.449, ley 13.927 o el propio cuestionario). Preguntas con `confidence <
0.9` o sin revisar quedan en `data/review-queue.json` como referencia
informativa para revisión humana (no bloquean el deploy).

## Deploy

GitHub Actions publica el contenido de `main` a GitHub Pages desde la raíz del
repo (`.nojekyll`, referencias relativas `./data/...` — funciona también bajo
subpath `/{org}/{repo}/`). El workflow corre `confidence_report.py` (genera el
queue informativo) + `review_gate.py` antes de publicar: el deploy solo falla
si un archivo de banco (`data/{generales,senales,auto}.json`) falta o está
vacío, o si falta `data/index.json`. Las respuestas con confianza baja quedan
señaladas en el queue para revisión, sin bloquear la publicación.
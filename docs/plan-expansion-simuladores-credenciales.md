# Plan de expansión: simuladores por credencial

Este plan convierte el simulador actual de Clase B en simuladores verificables para cada sección de clase presente en `cuestionario.pdf`. No autoriza publicar perfiles nuevos por analogía: la batería identifica secciones de preguntas, pero no contiene la equivalencia completa con las clases de licencia ni las reglas de evaluación. Cada perfil queda bloqueado hasta la confirmación municipal y provincial indicada.

## Decisión y alcance

| Tema | Estado/decisión |
|---|---|
| Producto actual | Solo `Clase B / Auto`; banco publicado: 579 preguntas (`420` generales, `91` señales, `68` auto). |
| Fuente primaria de preguntas | `cuestionario.pdf`, Anexo I, IF-2019-33101289-GDEBA-DPPYSVMGGP, Dirección Provincial de Política y Seguridad Vial, 228 páginas. No contiene clave de respuestas. |
| Alcance futuro | Todas las secciones específicas de clase identificadas en la batería, más las preguntas comunes requeridas por cada perfil cuando la autoridad lo confirme. |
| Fuera de alcance de este plan | Cambiar código, bancos, OpenSpec, configuración o publicar perfiles sin validación. |
| Regla de seguridad | Una sección no equivale automáticamente a una clase de licencia. No usar las reglas actuales de Clase B para otra credencial. |

## Camino de revisión

1. Validar con Municipio de Marcos Paz qué credenciales evalúa y con qué batería/reglas vigentes.
2. Validar con la Dirección Provincial de Política y Seguridad Vial de la Provincia de Buenos Aires la vigencia del IF, el mapeo sección-clase y la composición/aprobación.
3. Extraer y revisar cada sección confirmada; autorar respuestas con evidencia y revisión experta.
4. Habilitar un perfil por vez con reglas confirmadas, pruebas y revisión de contenido.
5. Publicar en entregas separadas; nunca exponer en UI un perfil no habilitado.

## Inventario extraído de la fuente

**Método reproducible:** `pdftotext -layout cuestionario.pdf` y `scripts/extract.py` con sus rangos `SECTION_MAP`. Los conteos son bloques que el extractor actual reconoce, no una declaración oficial de cantidad de preguntas de examen. Total: **900** bloques: **535** comunes, **75** de Auto y Camioneta, **290** específicos hoy excluidos.

| Perfil/sección candidata | Encabezado exacto en la batería | Rango de extracción (líneas) | Páginas PDF aprox. | Bloques extraídos | Estado actual | Reglas de examen |
|---|---|---:|---:|---:|---|---|
| Común | Preguntas para todas las clases: actores en la via publica; secciones 1 a 14 | 34–6486, secciones discontinuas | 2–156 aprox. | 535 | Usadas para B | La batería no fija cantidad, ponderación ni aprobación. Validar por perfil. |
| Clase B candidata | 1) Preguntas para clase de Auto y Camioneta | 6489–7398 | 157–177 aprox. | 75 | Única específica publicada | La app usa 40, 30/40, señales <=8, generales >=20, auto >=6; son configuración existente, no regla demostrada por el PDF. |
| Tracción a sangre candidata | Preguntas para Traccion a Sangre | 2926–2991 | 63–64 aprox. | 5 | Excluida | No indicada. Confirmar si es una credencial vigente/evaluable en Marcos Paz. |
| Carga candidata | 2) Preguntas para camionetas y vehículos de carga | 7399–7655 | 178–182 aprox. | 25 | Excluida | No indicada. Confirmar clase/s habilitada/s y reglas. |
| Motocicletas candidata | 3) Preguntas para la clase de motos: | 7656–8185 | 183–191 aprox. | 53 | Excluida | No indicada. Confirmar subclases/cilindradas y si comparten o separan examen. |
| Urgencia/emergencia candidata | 4) Preguntas para servicios de urgencia, emergencias y similares | 8186–8469 | 192–196 aprox. | 26 | Excluida | No indicada. Confirmar habilitación y requisitos profesionales. |
| Taxis/remises candidata | 5) Taxis y Remises | 8470–8623 | 197–199 aprox. | 17 | Excluida | No indicada. Confirmar clase y eventual normativa/localidad adicional. |
| Transporte de cargas candidata | 6) Vehículos afectados al transporte de cargas | 8624–9362 | 200–212 aprox. | 78 | Excluida | No indicada. Confirmar clase/s, incluido transporte especial. |
| Camión/casa rodante candidata | 7) Preguntas para Camion sin Acoplado y Casas Rodantes Motorizadas. | 9363–9568 | 213–216 aprox. | 20 | Excluida | No indicada. Confirmar si son un perfil o dos y sus clases legales. |
| Camiones con acoplado candidata | 8) Preguntas para Camiones con acoplado. | 9569–9925 | 217–222 aprox. | 39 | Excluida | No indicada. Confirmar clase/s y composición. |
| Transporte >8 pasajeros candidata | 9) Vehiculos de servicio de transporte de mas de 8 pasajeros | 9926–10180 | 223–228 aprox. | 27 | Excluida | No indicada. Confirmar clase/s, alcance y reglas profesionales. |

### Secciones comunes que deberá declarar cada perfil

| Slug | Sección | Rango | Bloques extraídos |
|---|---|---:|---:|
| `preambulo` | actores en la via publica | 34–666 | 50 |
| `seguridad` | Seguridad | 667–849 | 16 |
| `documentacion` | Documentación | 850–1055 | 20 |
| `intoxicacion` | intoxicación y alcohol | 1056–1484 | 38 |
| `varias` | varias | 1485–2248 | 78 |
| `semaforo` | Semáforo | 2249–2368 | 13 |
| `velocidades` | Velocidades | 2369–2661 | 30 |
| `adelantamiento` | Adelantamiento | 2662–2794 | 11 |
| `autopistas` | Autopistas | 2795–2925 | 12 |
| `estacionamiento` | Estacionamiento | 2992–3092 | 9 |
| `luces` | Luces | 3093–3221 | 12 |
| `giros` | Giros y rotondas | 3222–3375 | 14 |
| `senales` | Señales de Tránsito e indicaciones | 3376–4608 | 99 |
| `conduccion` | Conducción segura | 4609–6398 | 124 |
| `seg-activa` | Seguridad Activa y Pasiva | 6399–6486 | 9 |

## Compuerta de validación obligatoria

No implementar, mostrar ni promocionar un perfil hasta cerrar por escrito esta ficha para ese perfil.

| Dato a confirmar | Autoridad primaria | Evidencia aceptable | Decisión bloqueada |
|---|---|---|---|
| Clases/credenciales que emite y examina localmente | Dirección de Licencias de Conducir, Municipalidad de Marcos Paz | Respuesta institucional, instructivo vigente o resolución local | Qué perfiles existen en la UI y sus nombres legales |
| Correspondencia entre cada clase legal y cada sección del IF | Dirección Provincial de Política y Seguridad Vial, Provincia de Buenos Aires | Norma, circular, versión vigente de batería o confirmación institucional | Qué banco específico integra cada perfil |
| Vigencia/sustitución del IF-2019-33101289-GDEBA-DPPYSVMGGP | Dirección Provincial de Política y Seguridad Vial | Documento vigente o confirmación fechada | Uso de `cuestionario.pdf` como fuente de examen |
| Cantidad de preguntas, distribución, tiempo, puntaje, mínimos y aprobación | Municipio y autoridad provincial competente | Reglamento/protocolo de examen vigente | `examSize`, umbrales, cupos, temporizador y resultado |
| Efecto real de “Pregunta de carácter eliminatorio” | Misma autoridad que define el examen | Regla explícita | Inclusión forzada, reprobar por ítem o solo señalización de estudio |
| Uso de imágenes y accesibilidad alternativa | Municipio/provincia para fidelidad; responsable de accesibilidad para la presentación | Muestra oficial y revisión experta | Elegibilidad de preguntas con imagen en simulación |

**Salida de la compuerta:** una ficha versionada por perfil con fecha, contacto/expediente, URL o copia de evidencia, clases cubiertas, secciones, reglas literales y aprobación del responsable de contenido. Si falta un dato, el perfil permanece `draft` y no aparece como simulador.

## Contratos de datos propuestos

Conservar la trazabilidad existente de cada pregunta y separar definición de perfil de reglas verificadas. Los nombres son contrato de implementación, no datos para cargar ahora.

```json
{
  "id": "motos-0001",
  "profileEligibility": ["clase-a-confirmar"],
  "section": "motos",
  "category": "especificas-motos",
  "question": "...",
  "options": [{"key": "a", "text": "..."}],
  "correct": "a",
  "fundamento": "...",
  "sources": [{"material": "cuestionario", "ref": "IF-2019-33101289-GDEBA-DPPYSVMGGP", "page": 173}],
  "essential": false,
  "imageRef": null,
  "imageRequired": false,
  "srcFile": "cuestionario.pdf",
  "srcPage": 173,
  "confidence": 0.95,
  "reviewed": true
}
```

```json
{
  "id": "clase-a-confirmar",
  "status": "draft",
  "label": "Motocicletas",
  "legalClasses": [],
  "banks": ["comunes", "motos"],
  "rules": {
    "sourceStatus": "pending-validation",
    "examSize": null,
    "passThreshold": null,
    "scorePerQuestion": null,
    "timeLimitMinutes": null,
    "composition": [],
    "eliminatoryBehavior": "pending-validation"
  },
  "validation": {"municipal": null, "provincial": null}
}
```

**Invariantes:** `id` global y estable; `number` puede repetirse o ser nulo; `correct` pertenece a `options`; cada respuesta tiene `fundamento`, fuente precisa, confianza y revisión; una regla `null` o `pending-validation` impide pasar `draft` a `enabled`; una pregunta dependiente de imagen no entra a examen hasta contar con imagen y alternativa accesible validadas.

## Fases de entrega

| Fase | Entregable revisable | Actividades | Criterio de aceptación |
|---|---|---|---|
| 0. Confirmación de autoridad | Matriz legal y de examen firmada/registrada | Completar la compuerta por perfil; resolver equivalencias de clase y reglas | Ningún campo de regla o clase queda inferido; perfiles no confirmados siguen ocultos. |
| 1. Extracción reproducible | Inventario bruto completo | Versionar/automatizar la extracción de los nueve rangos excluidos; conservar `srcPage`, línea, imagen, número y anomalías; comparar conteos contra PDF | Los 290 bloques actuales se reproducen o toda diferencia queda explicada y aprobada; no se pierde el banco B. |
| 2. Normalización y esquema | Esquema/migración y manifiesto de secciones | Generalizar enums y categorías; agregar elegibilidad por perfil y manifiesto de estado; detectar duplicados, V/F, opciones truncadas, imágenes y secciones comunes | Validación de esquema, unicidad de `id`, trazabilidad de cada bloque y rechazo de perfiles `enabled` con reglas pendientes. |
| 3. Autoría y validación experta | Banco candidato por perfil | Redactar `correct`, `fundamento`, `sources`, confianza y revisión; cotejo por especialista vial/jurídico; capturar/matchear imágenes y texto alternativo | 100% de las preguntas seleccionables tienen respuesta, fundamento y fuente; 100% revisadas según umbral aprobado; ninguna imagen necesaria carece de alternativa. |
| 4. Composición y reglas | Ficha de reglas ejecutable por perfil | Traducir evidencia confirmada a tamaño, puntaje, umbral, tiempo, distribución, mínimos/máximos y eliminatorias; pruebas deterministas | Cada valor tiene cita de la ficha de fase 0; pruebas cubren composición, no repetición, puntuación y límites. |
| 5. UI y manifiesto | Selector de perfil y vistas contextualizadas | Mostrar solo perfiles `enabled`; cargar bancos declarados; explicar fuente, reglas y cobertura; mantener estudio separado de examen | Cambio de perfil no mezcla bancos; perfiles `draft` son inaccesibles; teclado, foco, contraste, imágenes y mensajes se validan. |
| 6. QA y publicación | Evidencia de release por perfil | Tests de datos/engine/UI, revisión de contenido, auditoría accesible y prueba en URL estática GitHub Pages bajo subruta | Pipeline pasa; carga HTTP real sin rutas absolutas; navegador móvil/escritorio; checklist de contenido y autoridad cerrado. |

## Secuencia de releases

1. Release 0: solo inventario y ficha de validación; sin nuevos simuladores.
2. Release 1: primer perfil no B cuya ficha de fase 0 esté completa, banco revisado y QA aprobado.
3. Releases siguientes: un perfil o grupo que comparta exactamente las mismas reglas confirmadas, con revisión independiente de banco y UI.
4. Release final: auditoría transversal de perfiles, trazabilidad de fuentes y revisión de regresión de Clase B.

La prioridad se decide por evidencia disponible y demanda municipal, no por el tamaño de la sección. Como referencia de carga de autoría, el primer lote específico más pequeño es Tracción a sangre (5 bloques), seguido de Taxis y Remises (17); Cargas (78) es el más grande. Los 535 comunes se revisan una vez, pero su elegibilidad se valida por cada perfil.

## QA, accesibilidad y Pages

| Área | Verificación requerida |
|---|---|
| Extracción | Conteos por sección, páginas fuente, V/F, opciones, numeración duplicada/nula y preguntas con imagen. |
| Contenido | Dos revisiones independientes de respuesta/fundamento/fuente; resolución documentada de desacuerdos; muestreo contra PDF. |
| Motor | Examen reproducible por semilla; composición exacta por perfil; sin repetidos; puntuación, umbrales, tiempo y eliminatorias según evidencia. |
| UI | Selector visible, reglas antes de iniciar, progreso y resultado claros; no revelar perfiles no validados. |
| Accesibilidad | Navegación completa por teclado, foco visible, semántica/formularios, contraste, mensajes anunciables y `alt`/equivalente textual para cada imagen. |
| GitHub Pages | `fetch` relativo, prueba desde servidor HTTP y URL publicada bajo subruta; errores de carga comprensibles; sin depender de `file://`. |

## Riesgos y decisiones

| Riesgo | Impacto | Mitigación/decisión |
|---|---|---|
| Batería desactualizada o no aplicable localmente | Simulador engañoso | Fase 0 bloqueante; conservar fecha/IF/evidencia por perfil. |
| Sección no corresponde 1:1 a clase legal | Perfil mal rotulado | Usar `legalClasses: []` hasta confirmación; permitir varios perfiles solo con evidencia. |
| Reglas B asumidas para otras clases | Resultado falso de aprobado/reprobado | No reutilizar 40/30 ni cupos B; valores nulos bloquean publicación. |
| Sin clave de respuestas | Error pedagógico/legal | Autoría con fuente, confianza y doble revisión experta. |
| Preguntas con imagen | Respuesta imposible o inaccesible | Inventario, mapeo visual, alternativa textual y exclusión de examen hasta validación. |
| Extracción imperfecta | Banco incompleto o corrupto | Comparar PDF/texto, fixtures por variante y revisión de anomalías. |
| Secciones comunes con contenido ajeno a un perfil | Examen irrelevante | Elegibilidad explícita por pregunta/sección y muestreo por perfil, no banco global ciego. |
| Release estático parcial | Perfil visible sin datos | Gate que exige manifiesto `enabled`, reglas validadas, bancos no vacíos y pruebas. |

## Responsables y puntos de decisión

| Responsable | Responsabilidad | Punto de decisión |
|---|---|---|
| Responsable municipal de Licencias, Marcos Paz | Confirmar oferta local, procedimiento y reglas operativas | Autoriza que un perfil represente una evaluación local. |
| Dirección Provincial de Política y Seguridad Vial, PBA | Confirmar vigencia del IF, equivalencias y reglas provinciales | Autoriza fuente y composición normativa. |
| Experto vial/jurídico designado | Validar respuestas, fundamentos y fuentes | Aprueba banco publicable. |
| Responsable de producto/contenido | Priorizar perfiles y custodiar evidencia | Promueve `draft` a candidato de release. |
| Desarrollo/QA | Implementar contratos, pruebas, accesibilidad y Pages | Promueve candidato a `enabled` solo tras checklist completo. |

## Checklist por perfil

- [ ] Clase legal y etiqueta pública confirmadas por Marcos Paz.
- [ ] Sección/específica y secciones comunes confirmadas por PBA.
- [ ] IF/fuente vigente confirmada y registrada.
- [ ] Cantidad de preguntas, puntaje, aprobación, tiempo y eliminatorias confirmados o explícitamente no aplicables.
- [ ] Extracción reproducible revisada contra el PDF.
- [ ] Banco con respuesta, fundamento y fuente para cada pregunta elegible.
- [ ] Revisión experta y resolución de incertidumbres completadas.
- [ ] Imágenes y equivalentes accesibles validados.
- [ ] Motor, UI, accesibilidad y GitHub Pages aprobados.
- [ ] Ficha de evidencia y aprobación de release archivadas.

## Referencias de partida

- `cuestionario.pdf` — Anexo I, IF-2019-33101289-GDEBA-DPPYSVMGGP, Dirección Provincial de Política y Seguridad Vial.
- `scripts/extract.py` — rangos `SECTION_MAP` y normalizaciones existentes.
- `scripts/build_bank.py` — exclusión actual de secciones no B y contrato de autoría.
- `data/exams.json`, `js/config.js`, `js/quiz-engine.js` — perfil y reglas actuales de Clase B, que no constituyen evidencia para otros perfiles.
- `data/schema/question.schema.json` — contrato vigente de preguntas y trazabilidad.

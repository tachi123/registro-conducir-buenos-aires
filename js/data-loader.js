/**
 * data-loader.js — relative-path data fetching with a friendly failure mode.
 *
 * Contract (static-site spec): fetch via `./data/...` (subpath-safe); on 404
 * or network failure (e.g. file://) throw DataLoadError so views can show a
 * clear error state instead of a silent blank screen.
 */

export class DataLoadError extends Error {
  constructor(message) {
    super(message)
    this.name = 'DataLoadError'
  }
}

export function dataUrl(name) {
  return `./data/${name}`
}

export async function loadJSON(path) {
  let res
  try {
    res = await fetch(path)
  } catch {
    throw new DataLoadError(
      `No se pudo cargar "${path}". Abrí la app desde un servidor (http) — el modo archivo (file://) no permite leer los datos.`
    )
  }
  if (!res.ok) {
    throw new DataLoadError(
      `No se encontró el archivo "${path}" (${res.status}).`
    )
  }
  return res.json()
}
/**
 * config.js — single configuration point for the Clase B quiz (design.md).
 * The engine reads examSize/floors from cfg at call time; this is the ONE
 * place the app-level constants live.
 */
export const CONFIG = {
  EXAM_SIZE: 40,
  PASS_THRESHOLD: 30,
  FLOORS: { senales: 8, generales: 20, auto: 6 },
  CONFIDENCE_GATE: 0.9,
}

export const CLASE_B_PROFILE = {
  id: 'clase-b-auto',
  label: 'Clase B / Auto',
  examSize: CONFIG.EXAM_SIZE,
  passThreshold: CONFIG.PASS_THRESHOLD,
  floors: CONFIG.FLOORS,
  banks: ['generales', 'senales', 'auto'],
}

export const FALLBACK_EXAMS_MANIFEST = {
  version: 1,
  profiles: [CLASE_B_PROFILE],
}

export const engineConfig = () => ({
  examSize: CONFIG.EXAM_SIZE,
  floors: CONFIG.FLOORS,
})

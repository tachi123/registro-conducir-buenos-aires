/**
 * quiz-engine.js — pure ESM exam builder for the Clase B quiz.
 *
 * Contract (design.md + quiz-mode spec):
 * - buildExam(bank, cfg, seed) -> { questions, seatLog }, deterministic per seed.
 * - Stratified sampling with category floors: senales <= 8 (cap),
 *   generales >= 20, auto >= 6. Essentials force-included (cap yields).
 * - Options per render: Fisher-Yates shuffle + bijective displayKey remap.
 * - evaluate(question, displayKey) + isPass(score, size, threshold).
 *
 * Pure functions only: no DOM, no module state, bank never mutated.
 */

const DEFAULT_FLOORS = { senales: 8, generales: 20, auto: 6 }

// ---------------------------------------------------------------------------
// Seedable RNG (mulberry32)
// ---------------------------------------------------------------------------
export function mulberry32(seed) {
  let a = seed >>> 0
  return function next() {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function shuffle(arr, rng) {
  const out = arr.slice()
  for (let i = out.length - 1; i > 0; i -= 1) {
    const j = Math.floor(rng() * (i + 1))
    ;[out[i], out[j]] = [out[j], out[i]]
  }
  return out
}

function categoryOf(question) {
  if (question.category === 'especificas-auto') return 'auto'
  return question.category
}

// ---------------------------------------------------------------------------
// Sampling
// ---------------------------------------------------------------------------
export function buildExam(bank, cfg = {}, seed = Date.now()) {
  const rng = mulberry32(seed)
  const examSize = cfg.examSize ?? 40
  const floors = { ...DEFAULT_FLOORS, ...(cfg.floors ?? {}) }
  const bankBy = new Map(bank.map(q => [q.id, q]))

  // 1. Candidate pool: exclude imageRequired while the image pipeline is absent.
  const candidates = bank.filter(q => !q.imageRequired)

  // 2. Essentials: deterministic order (confidence desc, number asc, id asc);
  //    include all when slots allow, else deterministic top-K.
  const essentialOrder = q => [-(q.confidence ?? 0), q.number ?? Infinity, q.id]
  const essentials = candidates
    .filter(q => q.essential)
    .sort((a, b) => {
      const ka = essentialOrder(a)
      const kb = essentialOrder(b)
      for (let i = 0; i < ka.length; i += 1) {
        if (ka[i] < kb[i]) return -1
        if (ka[i] > kb[i]) return 1
      }
      return 0
    })
  const included = essentials.length <= examSize ? essentials : essentials.slice(0, examSize)
  const chosen = new Map(included.map(q => [q.id, q]))
  const seatLog = { essentials: included.map(q => q.id), picks: [] }

  // 3. Remaining seats per category (minus essentials already drawn).
  const pools = { generales: [], senales: [], auto: [] }
  for (const q of candidates) {
    if (chosen.has(q.id)) continue
    pools[categoryOf(q)].push(q)
  }
  const chosenCount = cat => [...chosen.values()].filter(q => categoryOf(q) === cat).length

  // min_c = clamp(floor_c - essentials_c, 0, avail_c); deficits reallocated below.
  const minFor = {
    generales: Math.max(0, Math.min(floors.generales - chosenCount('generales'), pools.generales.length)),
    auto: Math.max(0, Math.min(floors.auto - chosenCount('auto'), pools.auto.length)),
    senales: 0, // senales is a CAP not a floor; essentials already honored it
  }

  const catOrder = ['generales', 'auto', 'senales']
  for (const cat of catOrder) {
    const need = minFor[cat]
    const draw = pools[cat].slice(0, need)
    for (const q of draw) chosen.set(q.id, q)
    seatLog.picks.push(...draw.map(q => q.id))
    pools[cat] = pools[cat].slice(need)
  }

  // 4. Residual slots: weighted by remaining pool size, never exceeding the
  //    senales cap; guard: exactly examSize unique ids.
  const seats = examSize - chosen.size

  for (let s = 0; s < seats; s += 1) {
    const alive = []
    for (const cat of catOrder) {
      if (pools[cat].length === 0) continue
      if (cat === 'senales' && chosenCount('senales') >= floors.senales) continue
      alive.push(cat)
    }
    if (alive.length === 0) break // pool exhausted; fewer than examSize possible
    // weighted pick proportional to remaining pool size
    const weights = alive.map(cat => pools[cat].length)
    const total = weights.reduce((a, b) => a + b, 0)
    let roll = rng() * total
    let picked = alive[alive.length - 1]
    for (let i = 0; i < alive.length; i += 1) {
      if (roll < weights[i]) { picked = alive[i]; break }
      roll -= weights[i]
    }
    const q = pools[picked].shift()
    chosen.set(q.id, q)
    seatLog.picks.push(q.id)
  }

  // 5. Per-render: shuffle options + bijective displayKey remap.
  const letter = i => String.fromCharCode(97 + i)
  const questions = [...chosen.values()].map(q => {
    const options = shuffle(q.options, rng)
    const display = options.map((o, i) => ({ displayKey: letter(i), text: o.text }))
    const correctIndex = options.findIndex(o => o.key === q.correct)
    return {
      id: q.id,
      number: q.number,
      section: q.section,
      category: q.category,
      question: q.question,
      answerType: q.answerType,
      essential: q.essential,
      imageRequired: q.imageRequired,
      options: display,
      correctDisplayKey: letter(correctIndex),
      fundamento: q.fundamento,
      sources: q.sources,
    }
  })

  return { questions, seatLog }
}

// ---------------------------------------------------------------------------
// Scoring
// ---------------------------------------------------------------------------
export function evaluate(question, chosenDisplayKey) {
  return question.correctDisplayKey === chosenDisplayKey
}

export function isPass(score, examSize = 40, passThreshold = 30) {
  return score >= passThreshold && score <= examSize
}
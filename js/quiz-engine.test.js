/**
 * Quiz engine tests (Strict TDD — these define the API before the engine exists).
 *
 * Contract (design.md + quiz-mode spec):
 * - buildExam(bank, cfg, seed) -> { questions, seatLog }; deterministic per seed.
 * - Exam: exactly cfg.examSize (default 40) distinct questions, none imageRequired.
 * - Floors: senales <= 8 (cap), generales >= 20, auto >= 6 (deficit: category
 *   smaller than its floor contributes all of its candidates, residual filled
 *   elsewhere).
 * - Essentials: force-included (all when slots allow; cap yields for essential
 *   senales), never mutated bank, deterministic tiebreak.
 * - Options per render: Fisher-Yates shuffle + bijective displayKey remap;
 *   correctDisplayKey identifies the correct option; bank object unchanged.
 * - Scoring: 1 point per correct answer; isPass(score) against configurable
 *   threshold (default 30/40).
 */

import { describe, it, expect } from 'vitest'
import { buildExam, isPass, evaluate } from './quiz-engine.js'

// ---------------------------------------------------------------------------
// Bank builders (synthetic, schema-shaped)
// ---------------------------------------------------------------------------
function mkQ(id, section, category, { essential = false, imageRequired = false, confidence = 0.9, number = null } = {}) {
  return {
    id,
    number,
    section,
    category,
    question: `Question ${id}?`,
    options: [
      { key: 'a', text: `${id}-a` },
      { key: 'b', text: `${id}-b` },
      { key: 'c', text: `${id}-c` },
    ],
    correct: 'b',
    answerType: 'single',
    fundamento: `Fundamento ${id}`,
    sources: [{ material: 'manual', ref: 'Cap. II', page: null }],
    essential,
    imageRef: null,
    imageRequired,
    srcFile: 'cuestionario.pdf',
    srcPage: 1,
    regionNote: null,
    confidence,
    reviewed: true,
  }
}

/** Build a bank with n questions per category plus a few imageRequired decoys. */
function mkBank({ generales = 60, senales = 15, auto = 10, essentials = { generales: 5, senales: 2, auto: 2 } } = {}) {
  const bank = []
  let n = 0
  const make = (count, section, category, essentialCount) => {
    for (let i = 0; i < count; i += 1) {
      n += 1
      bank.push(mkQ(`${section}-${String(n).padStart(4, '0')}`, section, category, {
        essential: i < essentialCount,
      }))
    }
  }
  make(generales, 'seguridad', 'generales', essentials.generales)
  make(senales, 'senales', 'senales', essentials.senales)
  make(auto, 'auto', 'especificas-auto', essentials.auto)
  // image decoys that must NEVER be sampled
  bank.push(mkQ('senales-999a', 'senales', 'senales', { imageRequired: true }))
  bank.push(mkQ('auto-999b', 'auto', 'especificas-auto', { imageRequired: true }))
  return bank
}

const FULL = mkBank()
const CFG = { examSize: 40, floors: { senales: 8, generales: 20, auto: 6 } }

describe('buildExam composition', () => {
  it('returns exactly 40 distinct questions and no imageRequired items', () => {
    const { questions } = buildExam(FULL, CFG, 1234)
    expect(questions).toHaveLength(40)
    const ids = questions.map(q => q.id)
    expect(new Set(ids).size).toBe(40)
    for (const q of questions) expect(q.imageRequired).toBe(false)
  })

  it('respects floors: senales <= 8, generales >= 20, auto >= 6', () => {
    const { questions } = buildExam(FULL, CFG, 1234)
    const count = cat => questions.filter(q => q.category === cat).length
    expect(count('senales')).toBeLessThanOrEqual(8)
    expect(count('generales')).toBeGreaterThanOrEqual(20)
    expect(count('especificas-auto')).toBeGreaterThanOrEqual(6)
    expect(count('senales') + count('generales') + count('especificas-auto')).toBe(40)
  })

  it('is deterministic under the same seed', () => {
    const a = buildExam(FULL, CFG, 42).questions.map(q => q.id)
    const b = buildExam(FULL, CFG, 42).questions.map(q => q.id)
    expect(a).toEqual(b)
  })

  it('varies under different seeds', () => {
    const a = buildExam(FULL, CFG, 1).questions.map(q => q.id)
    const b = buildExam(FULL, CFG, 2).questions.map(q => q.id)
    expect(a).not.toEqual(b)
  })

  it('shuffles the final batch order even when every question is essential', () => {
    const bank = mkBank({ generales: 40, senales: 0, auto: 0, essentials: { generales: 40, senales: 0, auto: 0 } })
    const a = buildExam(bank, { examSize: 40, floors: { senales: 0, generales: 40, auto: 0 } }, 1)
    const b = buildExam(bank, { examSize: 40, floors: { senales: 0, generales: 40, auto: 0 } }, 2)
    expect(a.questions.map(q => q.id)).not.toEqual(b.questions.map(q => q.id))
  })

  it('uses defaults when no cfg passed: 40 questions, 8/20/6 floors', () => {
    const { questions } = buildExam(FULL, undefined, 99)
    expect(questions).toHaveLength(40)
    const count = cat => questions.filter(q => q.category === cat).length
    expect(count('senales')).toBeLessThanOrEqual(8)
    expect(count('generales')).toBeGreaterThanOrEqual(20)
    expect(count('especificas-auto')).toBeGreaterThanOrEqual(6)
  })

  it('supports a configurable exam size with matching floors', () => {
    const mini = { examSize: 10, floors: { senales: 2, generales: 5, auto: 2 } }
    const { questions } = buildExam(FULL, mini, 4)
    expect(questions).toHaveLength(10)
    const count = cat => questions.filter(q => q.category === cat).length
    expect(count('senales')).toBeLessThanOrEqual(2)
    expect(count('generales')).toBeGreaterThanOrEqual(5)
    expect(count('especificas-auto')).toBeGreaterThanOrEqual(2)
    expect(new Set(questions.map(q => q.id)).size).toBe(10)
  })
})

describe('essential force-include', () => {
  it('includes every essential question when slots allow', () => {
    const { questions } = buildExam(FULL, CFG, 7)
    const ids = questions.map(q => q.id)
    const essentialIds = FULL.filter(q => q.essential).map(q => q.id)
    for (const id of essentialIds) expect(ids).toContain(id)
  })

  it('essential senales exceed the cap: cap yields, essentials still included', () => {
    const bank = mkBank({ generales: 60, senales: 12, auto: 10, essentials: { generales: 5, senales: 9, auto: 2 } })
    const { questions } = buildExam(bank, CFG, 3)
    const ids = questions.map(q => q.id)
    const essentialSenales = bank.filter(q => q.essential && q.category === 'senales').map(q => q.id)
    for (const id of essentialSenales) expect(ids).toContain(id)
    const countSenales = questions.filter(q => q.category === 'senales').length
    expect(countSenales).toBe(9) // all essential senales drawn; cap yielded
  })

  it('essentials exceed exam size: deterministic top-K subset, all essential', () => {
    // 50 essential generales in a bank of 60 -> only 40 can fit; the engine
    // must pick the 40 highest-priority ones deterministically (confidence desc)
    const big = []
    for (let i = 0; i < 60; i += 1) {
      big.push(mkQ(`seguridad-${String(i + 1).padStart(4, '0')}`, 'seguridad', 'generales', {
        essential: i < 50,
        confidence: 0.9 - (i % 7) * 0.001, // tiny spread so the sort is real
      }))
    }
    const { questions } = buildExam(big, { ...CFG, floors: { ...CFG.floors, generales: 40, auto: 6, senales: 8 } }, 6)
    expect(questions).toHaveLength(40)
    expect(questions.every(q => q.essential)).toBe(true)
    // deterministic under the same seed
    const again = buildExam(big, { ...CFG, floors: { ...CFG.floors, generales: 40, auto: 6, senales: 8 } }, 6)
    expect(again.questions.map(q => q.id)).toEqual(questions.map(q => q.id))
  })
})

describe('floor deficit reallocation', () => {
  it('category smaller than its floor contributes all; residual filled elsewhere', () => {
    const bank = mkBank({ generales: 60, senales: 15, auto: 2, essentials: { generales: 5, senales: 2, auto: 0 } })
    const { questions } = buildExam(bank, CFG, 5)
    expect(questions).toHaveLength(40)
    const auto = questions.filter(q => q.category === 'especificas-auto')
    expect(auto).toHaveLength(2) // ALL available auto questions drawn
    const ids = new Set(questions.map(q => q.id))
    for (const q of auto) expect(ids.has(q.id)).toBe(true)
    const other = questions.filter(q => q.category !== 'especificas-auto')
    expect(other).toHaveLength(38)
  })
})

describe('option shuffle and displayKey remap', () => {
  it('renders shuffled options with bijective displayKeys', () => {
    const { questions } = buildExam(FULL, CFG, 11)
    for (const q of questions) {
      const keys = q.options.map(o => o.displayKey)
      expect(new Set(keys).size).toBe(keys.length) // bijective
      expect(keys.sort()).toEqual(['a', 'b', 'c'])
      for (const o of q.options) expect(o.text).toMatch(new RegExp(`^${q.id}-[abc]$`))
    }
  })

  it('correctDisplayKey points at the correct option text', () => {
    const { questions } = buildExam(FULL, CFG, 11)
    const bankBy = new Map(FULL.map(q => [q.id, q]))
    for (const q of questions) {
      const rendered = q.options.find(o => o.displayKey === q.correctDisplayKey)
      const source = bankBy.get(q.id)
      const originalCorrect = source.options.find(o => o.key === source.correct)
      expect(rendered.text).toBe(originalCorrect.text)
    }
  })

  it('never mutates the bank', () => {
    const before = JSON.stringify(FULL)
    buildExam(FULL, CFG, 21)
    buildExam(FULL, CFG, 22)
    expect(JSON.stringify(FULL)).toBe(before)
  })
})

describe('scoring and pass threshold', () => {
  it('evaluate() marks the correct display key right and others wrong', () => {
    const { questions } = buildExam(FULL, CFG, 31)
    const q = questions[0]
    expect(evaluate(q, q.correctDisplayKey)).toBe(true)
    const wrongKey = q.options.find(o => o.displayKey !== q.correctDisplayKey).displayKey
    expect(evaluate(q, wrongKey)).toBe(false)
  })

  it('default threshold: 30/40 PASS, 29/40 FAIL', () => {
    expect(isPass(30, 40)).toBe(true)
    expect(isPass(29, 40)).toBe(false)
  })

  it('threshold overridable: 28/40 PASS at 28, FAIL at 27', () => {
    expect(isPass(28, 40, 28)).toBe(true)
    expect(isPass(27, 40, 28)).toBe(false)
  })
})

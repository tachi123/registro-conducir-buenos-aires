/**
 * View tests (Strict TDD, task 4.2): quiz/study/materials renderers.
 *
 * Contract (quiz-mode, study-mode, material-summaries specs):
 * - quizView: renders a random exam (engine output: rendered options with
 *   displayKey), after EVERY answer shows correct/incorrect + fundamento +
 *   sources[] chips before the next question; final score with pass/fail.
 * - studyView: renders all bank questions (incl. imageRequired) from data,
 *   filters by category+subcategory, empty filter -> empty-state message,
 *   imageRequired -> placeholder + srcPage link, answer reveal with evidence.
 * - materialsView: renders 5 cards each with title, queEs, queEstudiar, peso.
 *
 * Each view exposes { load(), render(content, data) }.
 */

import { describe, it, expect, vi, afterEach } from 'vitest'
import { quizView, studyView, materialsView } from './views.js'

// QUIZ bank: small, schema-shaped, none imageRequired (the engine skips those)
function mkQ(id, section, category, question, correctIdx = 0) {
  const options = [
    { key: 'a', text: `${id}-a` },
    { key: 'b', text: `${id}-b` },
    { key: 'c', text: `${id}-c` },
  ]
  return {
    id, number: null, section, category, subcategory: category, question,
    options, correct: options[correctIdx].key, answerType: 'single',
    fundamento: `Fundamento ${id}`, sources: [{ material: 'manual', ref: 'Cap. II', page: 7 }],
    essential: true, imageRef: null, imageRequired: false,
    srcFile: 'cuestionario.pdf', srcPage: 5, regionNote: null,
    confidence: 0.9, reviewed: true,
  }
}

const QUIZ_BANK = [
  mkQ('varias-001', 'varias', 'generales', '¿Quién tiene prioridad sobre el puente angosto?'),
  mkQ('varias-002', 'varias', 'generales', '¿Qué debe hacer ante una ambulancia con sirena?'),
  mkQ('auto-001', 'auto', 'especificas-auto', '¿Cada cuánto se hace la VTV?'),
]

const BANK = [
  {
    id: 'senales-225a', number: 225, section: 'senales', category: 'senales',
    subcategory: 'reglamentarias', question: 'La siguiente señal indica:',
    options: [
      { key: 'a', text: 'Detención transporte público.' },
      { key: 'b', text: 'Terminal ómnibus.' },
      { key: 'c', text: 'Punto panorámico.' },
    ],
    correct: 'a', answerType: 'single',
    fundamento: 'R27 detención transporte público.',
    sources: [{ material: 'ansv-senales', ref: 'Señales reglamentarias', page: 12 }],
    essential: true, imageRequired: true, srcPage: 96,
  },
  {
    id: 'varias-014', number: 14, section: 'varias', category: 'generales',
    subcategory: 'prioridad', question: '¿Quién tiene prioridad?',
    options: [
      { key: 'a', text: 'Ambulancias.' },
      { key: 'b', text: 'Nadie.' },
      { key: 'c', text: 'Todos.' },
    ],
    correct: 'a', answerType: 'single',
    fundamento: 'Emergencia con advertencia.',
    sources: [{ material: 'ley-24449', ref: 'art. 64', page: null }],
    essential: false, imageRequired: false, srcPage: 40,
  },
]

const MATERIALS = [
  { id: 'cuestionario', title: 'Cuestionario oficial', queEs: 'Batería oficial', queEstudiar: 'Toda la batería', peso: 1 },
  { id: 'manual', title: 'Manual del Conductor', queEs: 'Manual PBA', queEstudiar: 'Cap. I al VII', peso: 2 },
  { id: 'ansv-senales', title: 'Libro de Señales ANSV', queEs: 'Catálogo', queEstudiar: 'Todas las señales', peso: 3 },
  { id: 'ley-24449', title: 'Ley 24.449', queEs: 'Ley nacional', queEstudiar: 'Artículos clave', peso: 4 },
  { id: 'ley-13927', title: 'Ley 13.927', queEs: 'Ley provincial', queEstudiar: 'Jurisdicción', peso: 5 },
]

let mountedContent = null

function mkContent() {
  const el = document.createElement('div')
  document.body.appendChild(el)
  mountedContent = el
  return el
}

afterEach(() => {
  if (mountedContent) mountedContent.remove()
  mountedContent = null
})

describe('quizView', () => {
  it('renders an exam question with option labels and a submit button', () => {
    const content = mkContent()
    quizView.render(content, QUIZ_BANK)
    const stem = content.querySelector('.stem')
    expect(stem).not.toBeNull()
    expect(QUIZ_BANK.some(q => q.question === stem.textContent)).toBe(true)
    const labels = [...content.querySelectorAll('label')]
    expect(labels).toHaveLength(3)
    expect(labels[0].textContent.trim()).toMatch(/-(a|b|c)$/)
    expect(content.querySelector('button[type="submit"]')).not.toBeNull()
  })

  it('shows verdict, fundamento and source chips after answering', () => {
    const content = mkContent()
    quizView.render(content, QUIZ_BANK)
    const radio = content.querySelector('input[type="radio"]')
    radio.checked = true
    content.querySelector('button[type="submit"]').click()
    const verdict = content.querySelector('.feedback .correct, .feedback .incorrect')
    expect(verdict).not.toBeNull()
    expect(content.querySelector('.fundamento').textContent).toMatch(/^Fundamento /)
    expect(content.querySelector('.source-chip')).not.toBeNull()
    expect(content.textContent).toMatch(/manual/)
    // feedback blocking: the submit is disabled until the next question button
    expect(content.querySelector('button[type="submit"]').disabled).toBe(true)
  })

  it('shows PASS/FAIL summary at the end against the threshold', () => {
    const content = mkContent()
    quizView.renderSummary(content, { correctCount: 30, total: 40, threshold: 30 })
    expect(content.textContent).toMatch(/Aprobaste/i)
    quizView.renderSummary(content, { correctCount: 29, total: 40, threshold: 30 })
    expect(content.textContent).toMatch(/No aprobaste/i)
  })

  it('drains the whole exam into a final summary (loop closes)', () => {
    const content = mkContent()
    quizView.render(content, QUIZ_BANK)
    // ANSWER_ALL: for every rendered question click the first option then next
    let guard = 0
    while (content.querySelector('button[type="submit"]:not(:disabled)') && guard < 10) {
      const radio = content.querySelector('input[type="radio"]')
      radio.checked = true
      content.querySelector('button[type="submit"]').click()
      const next = content.querySelector('button[type="button"]')
      if (next) next.click()
      guard += 1
    }
    expect(content.textContent).toMatch(/Aprobaste|No aprobaste/i)
    expect(guard).toBeLessThan(10)
  })
})

describe('studyView', () => {
  it('renders all questions from the data, including imageRequired ones', () => {
    const content = mkContent()
    studyView.render(content, BANK)
    const items = [...content.querySelectorAll('.study-item')]
    expect(items).toHaveLength(2)
    expect(content.textContent).toMatch(/señal indica/)
    expect(content.textContent).toMatch(/prioridad/)
  })

  it('filters by category and subcategory', () => {
    const content = mkContent()
    studyView.render(content, BANK)
    const cat = content.querySelector('select[data-filter="category"]')
    cat.value = 'senales'
    cat.dispatchEvent(new Event('change'))
    const shown = [...content.querySelectorAll('.study-item')]
    expect(shown).toHaveLength(1)
    expect(shown[0].textContent).toMatch(/señal indica/)
  })

  it('shows an empty-state message when the filter matches nothing', () => {
    const content = mkContent()
    studyView.render(content, BANK)
    // real user flow: pick senales, pick its subcategory, then switch category
    // so the retained subcategory no longer matches -> empty state
    const cat = content.querySelector('select[data-filter="category"]')
    const sub = content.querySelector('select[data-filter="subcategory"]')
    cat.value = 'senales'
    cat.dispatchEvent(new Event('change'))
    sub.value = 'reglamentarias'
    sub.dispatchEvent(new Event('change'))
    expect([...content.querySelectorAll('.study-item')]).toHaveLength(1)
    cat.value = 'generales'
    cat.dispatchEvent(new Event('change'))
    const shown = [...content.querySelectorAll('.study-item')]
    expect(shown).toHaveLength(0)
    expect(content.querySelector('.empty-state')).not.toBeNull()
    expect(content.textContent).toMatch(/sin resultados|no hay/i)
  })

  it('renders a placeholder + srcPage link for imageRequired, none for text-only', () => {
    const content = mkContent()
    studyView.render(content, BANK)
    const imageItems = [...content.querySelectorAll('.study-item')].filter(el =>
      el.textContent.includes('señal indica'))
    expect(imageItems.length).toBe(1)
    expect(imageItems[0].querySelector('.image-placeholder')).not.toBeNull()
    const srcLink = imageItems[0].querySelector('a[data-srcpage]')
    expect(srcLink).not.toBeNull()
    expect(srcLink.textContent).toMatch(/96/)
    // text-only question has no placeholder
    const textItem = [...content.querySelectorAll('.study-item')].find(el =>
      el.textContent.includes('prioridad'))
    expect(textItem.querySelector('.image-placeholder')).toBeNull()
  })
})

describe('materialsView', () => {
  it('renders five cards each with the four fields', () => {
    const content = mkContent()
    materialsView.render(content, MATERIALS)
    const cards = [...content.querySelectorAll('.material-card')]
    expect(cards).toHaveLength(5)
    for (const card of cards) {
      expect(card.querySelector('.card-title')).not.toBeNull()
      expect(card.textContent).toMatch(/qué es/i)
      expect(card.textContent).toMatch(/qué estudiar/i)
      expect(card.textContent).toMatch(/peso/i)
    }
  })

  it('weights come from the data (Questionario = 1, highest)', () => {
    const content = mkContent()
    materialsView.render(content, MATERIALS)
    const cards = [...content.querySelectorAll('.material-card')]
    const questionario = cards.find(c => c.textContent.includes('Cuestionario oficial'))
    expect(questionario.textContent).toMatch(/peso/i)
    expect(questionario.textContent).toMatch(/1/)
  })
})
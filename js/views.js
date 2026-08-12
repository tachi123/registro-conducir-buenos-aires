/**
 * views.js — quiz / study / materials renderers (task 4.2).
 *
 * Each exports { load(), render(content, data) } so app.js can drive them
 * uniformly. Views write into the injected content element (no shared state).
 */

import { buildExam, isPass } from './quiz-engine.js'
import { CONFIG } from './config.js'
import { dataUrl, loadJSON } from './data-loader.js'

// ---------------------------------------------------------------------------
// Quiz view
// ---------------------------------------------------------------------------
function sourceChips(sources) {
  const chips = document.createElement('div')
  chips.className = 'source-chips'
  for (const src of sources) {
    const chip = document.createElement('span')
    chip.className = 'source-chip'
    chip.textContent = `${src.material}${src.ref ? ` · ${src.ref}` : ''}${
      src.page ? ` · p. ${src.page}` : ''
    }`
    chips.appendChild(chip)
  }
  return chips
}

export const quizView = {
  load: async () => {
    const index = await loadJSON(dataUrl('index.json'))
    const files = {
      generales: dataUrl('generales.json'),
      senales: dataUrl('senales.json'),
      auto: dataUrl('auto.json'),
    }
    const [generales, senales, auto] = await Promise.all(
      ['generales', 'senales', 'auto'].map(name => loadJSON(files[name]))
    )
    return { bank: [...generales, ...senales, ...auto], index }
  },

  render(content, ctx) {
    const bank = ctx.bank ?? ctx
    const cfg = { examSize: CONFIG.EXAM_SIZE, floors: CONFIG.FLOORS }
    const seed = Math.floor(Math.random() * 2 ** 31)
    const { questions } = buildExam(bank, cfg, seed)
    if (questions.length === 0) {
      content.innerHTML = '<p class="empty-state">No hay preguntas disponibles todavía.</p>'
      return
    }
    // fresh exam session state kept closure-local
    const session = {
      queue: [...questions],
      current: null,
      correctCount: 0,
      total: 0,
    }
    nextQuestion(content, session)
  },

  renderSummary(content, { correctCount, total, threshold = CONFIG.PASS_THRESHOLD }) {
    const passed = isPass(correctCount, total, threshold)
    const h2 = document.createElement('h2')
    h2.textContent = passed ? '¡Aprobaste!' : 'No aprobaste esta vez'
    const p = document.createElement('p')
    p.className = passed ? 'correct' : 'incorrect'
    p.textContent = `Resultado: ${correctCount}/${total} — necesitás ${threshold} para aprobar.`
    content.innerHTML = ''
    content.appendChild(h2)
    content.appendChild(p)
  },
}

function nextQuestion(content, session) {
  const q = session.queue.shift()
  if (!q) {
    quizView.renderSummary(content, session)
    return
  }
  session.current = q
  session.total += 1
  content.innerHTML = ''

  const card = document.createElement('article')
  card.className = 'quiz-item'
  const h2 = document.createElement('h2')
  h2.textContent = `Pregunta ${session.total}/${CONFIG.EXAM_SIZE}`
  const stem = document.createElement('p')
  stem.className = 'stem'
  stem.textContent = q.question
  card.appendChild(h2)
  card.appendChild(stem)

  const form = document.createElement('form')
  const fieldset = document.createElement('fieldset')
  for (const opt of q.options) {
    const label = document.createElement('label')
    const radio = document.createElement('input')
    radio.type = 'radio'
    radio.name = 'answer'
    radio.value = opt.displayKey
    label.appendChild(radio)
    label.appendChild(document.createTextNode(` ${opt.text}`))
    fieldset.appendChild(label)
  }
  form.appendChild(fieldset)
  const submit = document.createElement('button')
  submit.type = 'submit'
  submit.textContent = 'Responder'
  form.appendChild(submit)
  card.appendChild(form)

  const feedback = document.createElement('div')
  feedback.className = 'feedback'
  card.appendChild(feedback)

  form.addEventListener('submit', ev => {
    ev.preventDefault()
    const chosen = fieldset.querySelector('input[name="answer"]:checked')
    if (!chosen) return
    const right = chosen.value === q.correctDisplayKey
    if (right) session.correctCount += 1
    feedback.innerHTML = ''
    const verdict = document.createElement('p')
    verdict.className = right ? 'correct' : 'incorrect'
    verdict.textContent = right ? '¡Correcto!' : 'Incorrecto.'
    feedback.appendChild(verdict)
    const fund = document.createElement('p')
    fund.className = 'fundamento'
    fund.textContent = q.fundamento
    feedback.appendChild(fund)
    feedback.appendChild(sourceChips(q.sources))
    submit.disabled = true
    const nextBtn = document.createElement('button')
    nextBtn.type = 'button'
    nextBtn.textContent = 'Siguiente'
    nextBtn.addEventListener('click', () => nextQuestion(content, session))
    feedback.appendChild(nextBtn)
  })

  content.appendChild(card)
}

// ---------------------------------------------------------------------------
// Study view
// ---------------------------------------------------------------------------
export const studyView = {
  load: async () => {
    const [generales, senales, auto] = await Promise.all(
      ['generales', 'senales', 'auto'].map(name => loadJSON(dataUrl(`${name}.json`)))
    )
    return [...generales, ...senales, ...auto]
  },

  render(content, bank) {
    content.innerHTML = ''
    const filters = document.createElement('div')
    filters.className = 'filters'

    const cats = [...new Set(bank.map(q => q.category))]
    const catSel = document.createElement('select')
    catSel.dataset.filter = 'category'
    catSel.innerHTML = '<option value="">Todas las categorías</option>' +
      cats.map(c => `<option value="${c}">${c}</option>`).join('')

    const subSel = document.createElement('select')
    subSel.dataset.filter = 'subcategory'
    subSel.innerHTML = '<option value="">Todas las subcategorías</option>'

    filters.appendChild(catSel)
    filters.appendChild(subSel)
    content.appendChild(filters)

    const list = document.createElement('div')
    list.className = 'study-list'
    content.appendChild(list)

    function applyFilters() {
      const cat = catSel.value
      const sub = subSel.value
      const subs = [...new Set(bank.filter(q => !cat || q.category === cat).map(q => q.subcategory))].sort()
      subSel.innerHTML = '<option value="">Todas las subcategorías</option>' +
        subs.map(s => `<option value="${s}">${s}</option>`).join('')
      // keep the selected subcategory value (even if it no longer matches the
      // current category): the spec REQUIRES an empty-state message for an
      // unmatched filter combination instead of silently resetting.
      if (sub) subSel.value = sub
      const shown = bank.filter(q => (!cat || q.category === cat) && (!sub || q.subcategory === sub))
      renderList(shown)
    }

    function renderList(shown) {
      list.innerHTML = ''
      if (shown.length === 0) {
        const empty = document.createElement('p')
        empty.className = 'empty-state'
        empty.textContent = 'No hay preguntas con esos filtros.'
        list.appendChild(empty)
        return
      }
      for (const q of shown) {
        const item = document.createElement('article')
        item.className = 'study-item'
        const stem = document.createElement('p')
        stem.className = 'stem'
        stem.textContent = q.question
        item.appendChild(stem)
        if (q.imageRequired) {
          const ph = document.createElement('div')
          ph.className = 'image-placeholder'
          ph.textContent = 'Imagen pendiente (ver el PDF)'
          item.appendChild(ph)
          const link = document.createElement('a')
          link.setAttribute('data-srcpage', String(q.srcPage))
          link.href = `#src=${q.srcPage}`
          link.textContent = `Ver página ${q.srcPage} del cuestionario`
          item.appendChild(link)
        }
        const answers = document.createElement('form')
        answers.className = 'study-answers'
        const fieldset = document.createElement('fieldset')
        for (const opt of q.options) {
          const label = document.createElement('label')
          const radio = document.createElement('input')
          radio.type = 'radio'
          radio.name = `answer-${q.id}`
          radio.value = opt.key
          label.appendChild(radio)
          label.appendChild(document.createTextNode(` ${opt.text}`))
          fieldset.appendChild(label)
        }
        answers.appendChild(fieldset)
        const btn = document.createElement('button')
        btn.type = 'submit'
        btn.textContent = 'Ver respuesta'
        answers.appendChild(btn)
        const fb = document.createElement('div')
        fb.className = 'feedback'
        answers.appendChild(fb)
        answers.addEventListener('submit', ev => {
          ev.preventDefault()
          const chosen = fieldset.querySelector('input:checked')
          const right = chosen && chosen.value === q.correct
          fb.innerHTML = ''
          const verdict = document.createElement('p')
          verdict.className = right ? 'correct' : 'incorrect'
          verdict.textContent = right ? '¡Correcto!' : 'Incorrecto.'
          fb.appendChild(verdict)
          const fund = document.createElement('p')
          fund.className = 'fundamento'
          fund.textContent = q.fundamento
          fb.appendChild(fund)
          fb.appendChild(sourceChips(q.sources))
          btn.disabled = true
        })
        item.appendChild(answers)
        list.appendChild(item)
      }
    }

    catSel.addEventListener('change', applyFilters)
    subSel.addEventListener('change', applyFilters)
    applyFilters()
  },
}

// ---------------------------------------------------------------------------
// Materials view
// ---------------------------------------------------------------------------
export const materialsView = {
  load: async () => loadJSON(dataUrl('materials.json')),

  render(content, materials) {
    content.innerHTML = ''
    const grid = document.createElement('div')
    grid.className = 'material-cards'
    for (const m of materials) {
      const card = document.createElement('article')
      card.className = 'material-card'
      const title = document.createElement('h2')
      title.className = 'card-title'
      title.textContent = m.title
      card.appendChild(title)
      const queEs = document.createElement('p')
      queEs.innerHTML = `<strong>¿Qué es?</strong> ${m.queEs}`
      card.appendChild(queEs)
      const queEstudiar = document.createElement('p')
      queEstudiar.innerHTML = `<strong>¿Qué estudiar?</strong> ${m.queEstudiar}`
      card.appendChild(queEstudiar)
      const peso = document.createElement('p')
      peso.innerHTML = `<strong>Peso en examen:</strong> ${m.peso}`
      card.appendChild(peso)
      grid.appendChild(card)
    }
    content.appendChild(grid)
  },
}
/**
 * views.js — quiz / study / materials renderers (task 4.2).
 *
 * Each exports { load(), render(content, data) } so app.js can drive them
 * uniformly. Views write into the injected content element (no shared state).
 */

import { buildExam, isPass } from './quiz-engine.js'
import { CONFIG, FALLBACK_EXAMS_MANIFEST } from './config.js'
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
    let manifest = FALLBACK_EXAMS_MANIFEST
    try {
      const loaded = await loadJSON(dataUrl('exams.json'))
      if (loaded?.version === 1 && Array.isArray(loaded.profiles) && loaded.profiles.length > 0) {
        manifest = loaded
      }
    } catch {
      // Clase B remains usable if the optional profile manifest is unavailable.
    }
    const banks = [...new Set(manifest.profiles.flatMap(profile => profile.banks))]
    const loadedBanks = await Promise.all(banks.map(name => loadJSON(dataUrl(`${name}.json`))))
    return { bank: loadedBanks.flat(), profiles: manifest.profiles }
  },

  render(content, ctx) {
    const bank = ctx.bank ?? ctx
    const profiles = ctx.profiles ?? FALLBACK_EXAMS_MANIFEST.profiles
    let profile = profiles[0]
    let session = null

    content.innerHTML = ''
    const controls = document.createElement('div')
    controls.className = 'quiz-controls'
    const profileLabel = document.createElement('label')
    profileLabel.className = 'quiz-profile'
    profileLabel.textContent = 'Perfil de examen'
    const profileSelect = document.createElement('select')
    profileSelect.setAttribute('aria-label', 'Perfil de examen')
    for (const item of profiles) {
      const option = document.createElement('option')
      option.value = item.id
      option.textContent = item.label
      profileSelect.appendChild(option)
    }
    profileLabel.appendChild(profileSelect)
    const regenerate = document.createElement('button')
    regenerate.type = 'button'
    regenerate.textContent = 'Generar nuevo examen'
    controls.append(profileLabel, regenerate)
    const examContent = document.createElement('div')
    content.append(controls, examContent)

    const isInProgress = () => session && session.total > 0 && session.queue.length > 0
    const confirmDiscard = () => !isInProgress() || window.confirm('Vas a perder las respuestas de este examen. ¿Querés continuar?')
    const startExam = () => {
      const cfg = { examSize: profile.examSize, floors: profile.floors }
      const { questions } = buildExam(bank, cfg, Math.floor(Math.random() * 2 ** 31))
      if (questions.length === 0) {
        examContent.innerHTML = '<p class="empty-state">No hay preguntas disponibles todavía.</p>'
        return
      }
      session = { queue: [...questions], current: null, correctCount: 0, total: 0, profile }
      nextQuestion(examContent, session)
    }
    regenerate.addEventListener('click', () => {
      if (confirmDiscard()) startExam()
    })
    profileSelect.addEventListener('change', () => {
      const nextProfile = profiles.find(item => item.id === profileSelect.value)
      if (!nextProfile) return
      if (!confirmDiscard()) {
        profileSelect.value = profile.id
        return
      }
      profile = nextProfile
      startExam()
    })
    startExam()
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
    quizView.renderSummary(content, {
      ...session,
      threshold: session.profile.passThreshold,
    })
    return
  }
  session.current = q
  session.total += 1
  content.innerHTML = ''

  const card = document.createElement('article')
  card.className = 'quiz-item'
  const h2 = document.createElement('h2')
  h2.textContent = `Pregunta ${session.total}/${session.profile.examSize}`
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

// ---------------------------------------------------------------------------
// Resumenes view (study summaries)
// ---------------------------------------------------------------------------
export const resumenesView = {
  load: async () => loadJSON(dataUrl('resumenes.json')),

  render(content, entries) {
    content.innerHTML = ''
    const filters = document.createElement('div')
    filters.className = 'filters'

    // license options are DERIVED from the data at render time — never
    // hardcoded — so a future "moto" tag appears with zero code changes.
    const licenses = [...new Set(entries.flatMap(e => e.licencias))].sort()
    const sel = document.createElement('select')
    sel.dataset.filter = 'licencia'
    sel.innerHTML = '<option value="">Todas</option>' +
      licenses.map(l => `<option value="${l}">${l}</option>`).join('')
    filters.appendChild(sel)
    content.appendChild(filters)

    const list = document.createElement('div')
    list.className = 'resumen-list'
    content.appendChild(list)

    function applyFilter() {
      const lic = sel.value
      const shown = entries.filter(e => !lic || e.licencias.includes(lic))
      renderList(shown)
    }

    function renderList(shown) {
      list.innerHTML = ''
      if (shown.length === 0) {
        const empty = document.createElement('p')
        empty.className = 'empty-state'
        empty.textContent = 'No hay resúmenes para esa licencia.'
        list.appendChild(empty)
        return
      }
      for (const e of shown) {
        const card = document.createElement('article')
        card.className = 'resumen-card'
        const title = document.createElement('h2')
        title.className = 'card-title'
        title.textContent = e.title
        card.appendChild(title)
        const chips = document.createElement('div')
        chips.className = 'source-chips'
        for (const lic of e.licencias) {
          const chip = document.createElement('span')
          chip.className = 'license-chip'
          chip.textContent = lic
          chips.appendChild(chip)
        }
        card.appendChild(chips)
        const ideas = document.createElement('ul')
        ideas.className = 'ideas-clave'
        for (const idea of e.ideasClave) {
          const li = document.createElement('li')
          li.textContent = idea
          ideas.appendChild(li)
        }
        card.appendChild(ideas)
        list.appendChild(card)
      }
    }

    sel.addEventListener('change', applyFilter)
    applyFilter()
  },
}

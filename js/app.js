/**
 * app.js — bootstrap + hash router for the Clase B quiz (static-site spec).
 *
 * Contract:
 * - boot({root, views, load}) renders nav (quiz/study/materials), subscribes
 *   to hashchange, lazy-fetches the active view's data, renders it, and shows
 *   a friendly error banner on fetch failure while keeping the nav usable.
 * - views registry: { [name]: { load: () => Promise, render: (data) => void } }.
 * - load defaults to the real data-loader; tests inject a fake.
 */

import { loadJSON, DataLoadError } from './data-loader.js'

const VIEW_NAMES = ['quiz', 'study', 'materials']

function currentView() {
  const hash = window.location.hash.replace(/^#\/?/, '')
  return VIEW_NAMES.includes(hash) ? hash : 'quiz'
}

function showError(root, message) {
  const old = root.querySelector('[role="alert"]')
  if (old) old.remove()
  const banner = document.createElement('div')
  banner.setAttribute('role', 'alert')
  banner.textContent = message
  root.querySelector('#app-content').prepend(banner)
}

export function boot({ root = document.body, views, load = loadJSON } = {}) {
  const nav = document.createElement('nav')
  for (const name of VIEW_NAMES) {
    const link = document.createElement('a')
    link.id = `nav-${name}`
    link.href = `#${name}`
    link.textContent = name
    link.addEventListener('click', () => {
      window.location.hash = name
    })
    nav.appendChild(link)
  }
  const content = document.createElement('div')
  content.id = 'app-content'
  root.appendChild(nav)
  root.appendChild(content)

  async function render() {
    const name = currentView()
    document.querySelectorAll('nav a').forEach(a => {
      a.classList.toggle('active', a.id === `nav-${name}`)
    })
    content.innerHTML = ''
    const view = views[name]
    if (!view) return
    try {
      const data = await view.load()
      content.innerHTML = ''
      view.render(content, data)
    } catch (err) {
      content.innerHTML = ''
      showError(
        root,
        err instanceof DataLoadError
          ? err.message
          : 'No se pudo cargar esta sección. Intenta de nuevo.'
      )
    }
  }

  window.addEventListener('hashchange', render)
  render()

  return { render }
}
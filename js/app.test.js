/**
 * App shell tests (Strict TDD, task 4.1): config single point, data loader
 * with friendly failure, and the boot/router contract.
 *
 * Contract (static-site spec + design.md):
 * - config.js exports the ONE config point: EXAM_SIZE=40, PASS_THRESHOLD=30,
 *   FLOORS {senales:8, generales:20, auto:6}, CONFIDENCE_GATE=0.9.
 * - data-loader.loadJSON(path) fetches with relative paths; on 404 or network
 *   failure it throws DataLoadError (never returns undefined silently).
 * - app.boot() renders nav (quiz/study/materials), reacts to hash changes,
 *   lazy-fetches view data, and on fetch failure shows a friendly error banner
 *   while the nav stays usable.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { CONFIG } from './config.js'
import { loadJSON, DataLoadError, dataUrl } from './data-loader.js'
import { boot } from './app.js'

describe('config.js single configuration point', () => {
  it('exposes the exam contract constants', () => {
    expect(CONFIG.EXAM_SIZE).toBe(40)
    expect(CONFIG.PASS_THRESHOLD).toBe(30)
    expect(CONFIG.FLOORS).toEqual({ senales: 8, generales: 20, auto: 6 })
    expect(CONFIG.CONFIDENCE_GATE).toBe(0.9)
  })
})

describe('data-loader', () => {
  beforeEach(() => vi.unstubAllGlobals())

  it('loadJSON resolves with parsed data on a successful fetch', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => ({
      ok: true,
      json: async () => ({ version: 1, sections: {} }),
    })))
    const data = await loadJSON('./data/index.json')
    expect(data.version).toBe(1)
    expect(fetch).toHaveBeenCalledWith('./data/index.json')
  })

  it('loadJSON throws DataLoadError on HTTP 404', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => ({ ok: false, status: 404 })))
    await expect(loadJSON('./data/missing.json')).rejects.toBeInstanceOf(DataLoadError)
  })

  it('loadJSON throws DataLoadError when fetch itself fails (file:// case)', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => { throw new TypeError('Failed to fetch') }))
    await expect(loadJSON('./data/index.json')).rejects.toBeInstanceOf(DataLoadError)
  })

  it('dataUrl builds subpath-safe relative references', () => {
    expect(dataUrl('generales.json')).toBe('./data/generales.json')
  })
})

describe('app boot/router', () => {
  let root
  const navIds = () => [...root.querySelectorAll('nav a')].map(a => a.id)

  function mount(fakeViews, fakeLoad) {
    root = document.createElement('div')
    document.body.appendChild(root)
    return boot({ root, views: fakeViews, load: fakeLoad })
  }

  beforeEach(() => {
    document.body.innerHTML = ''
  })

  afterEach(() => {
    if (root) root.remove()
    window.location.hash = ''
  })

  it('renders the three nav entries on boot', () => {
    mount(
      { quiz: { load: vi.fn(async () => []), render: vi.fn() },
        study: { load: vi.fn(async () => []), render: vi.fn() },
        materials: { load: vi.fn(async () => []), render: vi.fn() } },
      vi.fn(async () => []),
    )
    expect(navIds()).toEqual(['nav-quiz', 'nav-study', 'nav-materials'])
  })

  it('lazy-loads and renders the view matching the hash', async () => {
    const study = { load: vi.fn(async () => [{ id: 'q1' }]), render: vi.fn() }
    mount(
      { quiz: { load: vi.fn(async () => []), render: vi.fn() },
        study,
        materials: { load: vi.fn(async () => []), render: vi.fn() } },
      vi.fn(async () => []),
    )
    window.location.hash = '#study'
    window.dispatchEvent(new HashChangeEvent('hashchange'))
    await vi.waitFor(() => expect(study.render).toHaveBeenCalled())
    expect(study.load).toHaveBeenCalled()
    // render(content, data): data is the second argument
    expect(study.render.mock.calls[0][1]).toEqual([{ id: 'q1' }])
  })

  it('shows a friendly error banner and keeps nav on fetch failure', async () => {
    const failing = {
      load: vi.fn(async () => { throw new DataLoadError('No se pudo cargar la sección de quiz.') }),
      render: vi.fn(),
    }
    const ok = { load: vi.fn(async () => []), render: vi.fn() }
    mount(
      { quiz: failing, study: ok, materials: ok },
      vi.fn(async () => []),
    )
    window.location.hash = '#quiz'
    window.dispatchEvent(new HashChangeEvent('hashchange'))
    await vi.waitFor(() => {
      expect(root.querySelector('[role="alert"]')).not.toBeNull()
    })
    const banner = root.querySelector('[role="alert"]')
    expect(banner.textContent).toMatch(/no se pudo cargar/i)
    // nav still usable: switching to another view clears the banner and works
    window.location.hash = '#study'
    window.dispatchEvent(new HashChangeEvent('hashchange'))
    await vi.waitFor(() => expect(ok.render).toHaveBeenCalled())
    expect(root.querySelector('[role="alert"]')).toBeNull()
    expect(navIds()).toEqual(['nav-quiz', 'nav-study', 'nav-materials'])
  })

  it('injects the loader for lazy fetch (boot passes the load function)', async () => {
    const loader = vi.fn(async path => ({ path }))
    const quiz = { load: vi.fn(async () => []), render: vi.fn() }
    mount({ quiz, study: quiz, materials: quiz }, loader)
    expect(loader).not.toHaveBeenCalled() // nothing loaded at boot
  })
})

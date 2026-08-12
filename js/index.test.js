/**
 * index.html structural test (task 4.3): the static-site entry must wire the
 * app with subpath-safe relative references and a module script. CSS class
 * assertions are banned by the TDD rules — we assert the HTML contract only.
 */
import { describe, it, expect } from 'vitest'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'
import { JSDOM } from 'jsdom'

const here = dirname(fileURLToPath(import.meta.url))
const html = readFileSync(resolve(here, '..', 'index.html'), 'utf-8')
const dom = new JSDOM(html)
const doc = dom.window.document

describe('index.html static entry', () => {
  it('loads the app as an ES module with a relative path', () => {
    const scripts = [...doc.querySelectorAll('script')]
    const module = scripts.find(s => s.type === 'module')
    expect(module).not.toBeUndefined()
    const src = module.getAttribute('src') ?? ''
    expect(src).toMatch(/^\.\//)
    expect(src).toMatch(/app\.js$/)
  })

  it('provides the root mount point the app renders into', () => {
    const root = doc.querySelector('#app')
    expect(root).not.toBeNull()
  })

  it('references stylesheet with a relative path', () => {
    const link = doc.querySelector('link[rel="stylesheet"]')
    expect(link).not.toBeNull()
    expect(link.getAttribute('href')).toMatch(/^\.\//)
  })

  it('has no hardcoded question data (data comes from JSON only)', () => {
    // spec: app views MUST read question data from data/*.json, no hardcoded
    // questions — the HTML must not embed any option text or stems.
    expect(html).not.toMatch(/cuánto se hace la VTV|señal indica|prioridad/i)
    expect(html).not.toMatch(/displayKey|correctDisplayKey/)
  })

  it('uses only relative ./data references if any data path appears', () => {
    // the bootstrap imports ./js/app.js; data paths appear at runtime via
    // data-loader — the HTML must not hardcode absolute /data or /js paths
    expect(html).not.toMatch(/["']\/data\//)
    expect(html).not.toMatch(/["']\/js\//)
  })
})

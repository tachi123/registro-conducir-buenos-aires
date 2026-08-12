describe('vitest boots', () => {
  it('runs tests in the jsdom environment', () => {
    expect(typeof document).toBe('object')
    expect(typeof document.createElement).toBe('function')
  })

  it('supports ESM imports from the repo', async () => {
    const pkg = await import('../package.json')
    expect(pkg.default.type).toBe('module')
  })
})
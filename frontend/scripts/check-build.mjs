import { readdir, readFile, access } from 'node:fs/promises'
import { resolve, join } from 'node:path'

const root = resolve('.output/public')
for (const file of ['index.html', '200.html', '404.html', 'compare/index.html', 'api-test-console/index.html', 'maps/greater-melbourne-sa2.geojson']) await access(join(root, file))
async function inspect(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name)
    if (entry.isDirectory()) await inspect(path)
    else if (/\.(sqlite|db|py|env)$/.test(entry.name) || entry.name === '.env') throw new Error(`Private file in static output: ${path}`)
  }
}
await inspect(root)
if (!(await readFile(join(root, 'index.html'), 'utf8')).includes('Find your place in Melbourne.')) throw new Error('Homepage was not prerendered')
console.log('Static output checked: homepage, fallback pages, no database or backend files.')

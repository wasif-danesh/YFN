// Local preview/test server only. Render serves .output/public directly.
import { createServer } from 'node:http'
import { readFile } from 'node:fs/promises'
import { resolve, extname, sep } from 'node:path'

const root = resolve('.output/public')
const mime = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.geojson': 'application/geo+json',
  '.png': 'image/png',
  '.woff': 'font/woff',
  '.svg': 'image/svg+xml',
}
createServer(async (req, res) => {
  try {
    const pathname = decodeURIComponent(
      new URL(req.url, 'http://localhost').pathname,
    )
    const path = resolve(
      root,
      `.${pathname.endsWith('/') ? pathname + 'index.html' : /\.[^/]+$/.test(pathname) ? pathname : pathname + '/index.html'}`,
    )
    if (!path.startsWith(root + sep)) {
      res.writeHead(403)
      return res.end()
    }
    const body = await readFile(path)
    res.writeHead(200, {
      'Content-Type': mime[extname(path)] || 'application/octet-stream',
    })
    res.end(body)
  } catch {
    const isRoute = !extname(new URL(req.url, 'http://localhost').pathname)
    res.writeHead(isRoute ? 200 : 404, { 'Content-Type': 'text/html' })
    res.end(await readFile(resolve(root, isRoute ? '200.html' : '404.html')))
  }
}).listen(Number(process.env.PORT || 4173), '127.0.0.1', () =>
  console.log('Static preview: http://127.0.0.1:4173'),
)

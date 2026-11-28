/**
 * Generate `public/llms.txt` — a curated, link-first index of the docs for LLMs
 * (the llms.txt proposal). Low proven ROI (plan4 §1, 🧪), but ~free here since
 * route discovery already exists. Reuses discoverRoutes() and reads each page's
 * front-matter title/description.
 */
import { writeFile, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import pc from 'picocolors';

import type { NextraSeoConfig, RouteInfo } from '../core/types.js';
import { discoverRoutes } from '../core/routes.js';

interface PageMeta {
  path: string;
  title: string;
  description: string;
}

/** Pull `title:` / `description:` from a file's YAML front-matter (cheap regex). */
async function readMeta(route: RouteInfo): Promise<PageMeta> {
  let title = route.path;
  let description = '';
  try {
    const src = await readFile(route.file, 'utf8');
    const fm = src.match(/^---\n([\s\S]*?)\n---/);
    if (fm) {
      const t = fm[1].match(/^title:\s*(.+)$/m);
      const d = fm[1].match(/^description:\s*(.+)$/m);
      if (t) title = t[1].trim().replace(/^['"]|['"]$/g, '');
      if (d) description = d[1].trim().replace(/^['"]|['"]$/g, '');
    }
  } catch {
    /* keep defaults */
  }
  return { path: route.path, title, description };
}

export async function generateLlmsTxt(config: NextraSeoConfig): Promise<void> {
  console.log(pc.cyan('Generating llms.txt from content tree...'));
  const base = config.baseUrl.replace(/\/+$/, '');
  const routes = await discoverRoutes(config);
  const metas = await Promise.all(routes.map(readMeta));

  // Sort by path for a stable, scannable index.
  metas.sort((a, b) => a.path.localeCompare(b.path));

  const lines: string[] = [
    `# ${config.name ?? 'Documentation'}`,
    '',
    `> ${config.description ?? 'Documentation index for large language models.'}`,
    '',
    '## Docs',
    '',
  ];
  for (const m of metas) {
    const url = `${base}${m.path === '/' ? '' : m.path}`;
    const desc = m.description ? `: ${m.description}` : '';
    lines.push(`- [${m.title}](${url})${desc}`);
  }
  lines.push('');

  const outDir = config.outputDir ?? 'public';
  await writeFile(join(outDir, 'llms.txt'), lines.join('\n'));
  console.log(pc.green(`✓ ${join(outDir, 'llms.txt')} (${metas.length} pages)`));
}

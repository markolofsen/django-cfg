/**
 * Sitemap + robots.txt generation from the Nextra content tree (root-based URLs).
 */
import { writeFile, mkdir } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import pc from 'picocolors';
import { discoverRoutes } from '../core/routes.js';
import type { NextraSeoConfig, RouteInfo } from '../core/types.js';

function xmlEscape(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

export function generateSitemapXml(routes: RouteInfo[], baseUrl: string): string {
  const base = baseUrl.replace(/\/+$/, '');
  const urls = routes
    .map((r) => {
      const loc = xmlEscape(`${base}${r.path === '/' ? '' : r.path}` || `${base}/`);
      return [
        '  <url>',
        `    <loc>${loc}</loc>`,
        `    <lastmod>${r.lastmod.slice(0, 10)}</lastmod>`,
        `    <changefreq>${r.changefreq}</changefreq>`,
        `    <priority>${r.priority.toFixed(1)}</priority>`,
        '  </url>',
      ].join('\n');
    })
    .join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>
`;
}

/**
 * AI / answer-engine crawlers we explicitly allow. The site exists to be
 * discovered and cited, so we opt INTO AI indexing rather than block it.
 * (GEO best practice — being citable beats being hidden.)
 */
const AI_CRAWLERS = [
  'GPTBot', // OpenAI training
  'OAI-SearchBot', // ChatGPT search
  'ChatGPT-User', // ChatGPT browsing
  'ClaudeBot', // Anthropic training
  'Claude-User', // Claude browsing
  'Claude-SearchBot', // Anthropic search index
  'PerplexityBot', // Perplexity
  'Google-Extended', // Gemini / AI Overviews
  'Bingbot', // Bing / Copilot index
  'Applebot-Extended', // Apple Intelligence
  'CCBot', // Common Crawl (feeds many models)
];

export function generateRobotsTxt(baseUrl: string): string {
  const base = baseUrl.replace(/\/+$/, '');
  const aiStanzas = AI_CRAWLERS.map((bot) => `User-agent: ${bot}\nAllow: /`).join(
    '\n\n',
  );
  return `User-agent: *
Allow: /

${aiStanzas}

Sitemap: ${base}/sitemap.xml
`;
}

export async function generateSitemap(config: NextraSeoConfig): Promise<RouteInfo[]> {
  console.log(pc.cyan('Generating sitemap from content tree...'));
  const routes = await discoverRoutes(config);
  console.log(pc.dim(`  ${routes.length} routes discovered`));

  const outDir = resolve(process.cwd(), config.outputDir);
  await mkdir(outDir, { recursive: true });
  await writeFile(join(outDir, 'sitemap.xml'), generateSitemapXml(routes, config.baseUrl));
  await writeFile(join(outDir, 'robots.txt'), generateRobotsTxt(config.baseUrl));

  console.log(pc.green(`✓ ${join(config.outputDir, 'sitemap.xml')} (${routes.length} urls)`));
  console.log(pc.green(`✓ ${join(config.outputDir, 'robots.txt')}`));
  return routes;
}

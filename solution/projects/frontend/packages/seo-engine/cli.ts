#!/usr/bin/env node
/**
 * Universal Nextra-4 docs SEO CLI (scripts/seo) — brand-agnostic.
 *
 * Project specifics (base URL, name) live in the project's `seo.config.ts`,
 * NOT here — so this folder can be copied verbatim between Nextra apps.
 *
 * Commands:
 *   sitemap   Generate public/sitemap.xml + robots.txt from the Nextra content tree.
 *   check     Find broken internal refs — pages, #anchors, images, JSX-relative hrefs (offline, CI-friendly).
 *   external  Probe outbound http(s) URLs for dead links (network).
 *   fix       Auto-fix safe broken links (dry-run unless --write).
 */
import { Command } from 'commander';
import pc from 'picocolors';
import { loadConfig } from './core/config.js';
import { generateSitemap } from './commands/sitemap.js';
import { generateLlmsTxt } from './commands/llms.js';
import { checkLinks } from './commands/check.js';
import { checkExternal } from './commands/external.js';
import { printCheckReport, printExternalReport } from './reporters/report.js';
import { fixLinks, printFixResult } from './commands/fix.js';

const program = new Command();

program
  .name('nextra-docs-seo')
  .description('Universal SEO + link-integrity toolkit for Nextra 4 docs apps')
  .version('0.1.0');

program
  .command('sitemap')
  .description('Generate sitemap.xml + robots.txt from the content tree')
  .option('-c, --config <path>', 'Path to config file')
  .option('--content <dir>', 'Content directory (default: content)')
  .option('-o, --output <dir>', 'Output directory (default: public)')
  .option('--base-url <url>', 'Base URL for the sitemap')
  .action(async (opts) => {
    const config = await loadConfig(opts.config);
    if (opts.content) config.contentDir = opts.content;
    if (opts.output) config.outputDir = opts.output;
    if (opts.baseUrl) config.baseUrl = opts.baseUrl;
    await generateSitemap(config);
    if (config.llms !== false) await generateLlmsTxt(config);
  });

program
  .command('check')
  .description('Check broken internal refs: pages, #anchors, images (exit 1 if any broken)')
  .option('-c, --config <path>', 'Path to config file')
  .option('--content <dir>', 'Content directory (default: content)')
  .option('--public <dir>', 'Public assets directory (default: public)')
  .action(async (opts) => {
    const config = await loadConfig(opts.config);
    if (opts.content) config.contentDir = opts.content;
    if (opts.public) config.publicDir = opts.public;
    const result = await checkLinks(config);
    printCheckReport(result);
    if (result.broken.length > 0) process.exitCode = 1;
  });

program
  .command('external')
  .description('Probe outbound http(s) URLs for dead links (network; exit 1 if any dead)')
  .option('-c, --config <path>', 'Path to config file')
  .option('--content <dir>', 'Content directory (default: content)')
  .option('--concurrency <n>', 'Parallel requests (default: 16)', (v) => parseInt(v, 10), 16)
  .option('--timeout <ms>', 'Per-request timeout in ms (default: 12000)', (v) => parseInt(v, 10), 12000)
  .action(async (opts) => {
    const config = await loadConfig(opts.config);
    if (opts.content) config.contentDir = opts.content;
    const result = await checkExternal(config, { concurrency: opts.concurrency, timeoutMs: opts.timeout });
    printExternalReport(result);
    if (result.dead.length > 0) process.exitCode = 1;
  });

program
  .command('fix')
  .description('Auto-fix safe broken links (dry-run by default)')
  .option('-c, --config <path>', 'Path to config file')
  .option('--content <dir>', 'Content directory (default: content)')
  .option('-w, --write', 'Apply fixes to disk (default: dry-run)', false)
  .action(async (opts) => {
    const config = await loadConfig(opts.config);
    if (opts.content) config.contentDir = opts.content;
    const result = await fixLinks(config, { write: !!opts.write });
    printFixResult(result);
  });

program.parseAsync().catch((err) => {
  console.error(pc.red('Error:'), err?.message ?? err);
  process.exit(1);
});

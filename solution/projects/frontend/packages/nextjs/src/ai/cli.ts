#!/usr/bin/env node
/**
 * DjangoCFG AI Docs CLI
 *
 * Usage:
 *   npx djangocfg-docs search "database configuration"
 *   npx djangocfg-docs mcp
 */

import { consola } from 'consola';

import { getMcpConfig, MCP_API_URL, MCP_SERVER_URL, search } from './index';

const args = process.argv.slice(2);
const command = args[0];
const query = args.slice(1).join(' ');

/** Wrap text to terminal width with indent */
function wrapText(text: string, indent = 3, maxWidth?: number): string {
  const width = maxWidth || process.stdout.columns || 80;
  const effectiveWidth = width - indent;
  const prefix = ' '.repeat(indent);

  // Clean up text - remove extra whitespace and newlines
  const cleaned = text.replace(/\s+/g, ' ').trim();

  if (cleaned.length <= effectiveWidth) {
    return prefix + cleaned;
  }

  const words = cleaned.split(' ');
  const lines: string[] = [];
  let currentLine = '';

  for (const word of words) {
    if (currentLine.length + word.length + 1 <= effectiveWidth) {
      currentLine += (currentLine ? ' ' : '') + word;
    } else {
      if (currentLine) lines.push(prefix + currentLine);
      currentLine = word;
    }
  }
  if (currentLine) lines.push(prefix + currentLine);

  return lines.join('\n');
}

async function main() {
  switch (command) {
    case 'search':
    case 's':
      if (!query) {
        consola.error('Usage: djangocfg-docs search "your query"');
        process.exit(1);
      }
      consola.info(`Searching: ${query}\n`);
      try {
        const results = await search(query, { limit: 5 });
        if (results.length === 0) {
          consola.warn('No results found.');
        } else {
          results.forEach((r, i) => {
            consola.success(`${i + 1}. ${r.title}`);
            // Wrap content to terminal width
            const contentPreview = r.content.slice(0, 200);
            console.log(wrapText(contentPreview + '...'));
            if (r.url) consola.log(`   ${r.url}`);
            consola.log('');
          });
        }
      } catch (err) {
        consola.error('Error:', err instanceof Error ? err.message : err);
        process.exit(1);
      }
      break;

    case 'mcp':
      consola.box('MCP Server Configuration');
      consola.log(JSON.stringify(getMcpConfig(), null, 2));
      consola.info('Add this to your AI assistant configuration.');
      break;

    case 'info':
    case 'i':
      consola.box('DjangoCFG AI Documentation');
      consola.info(`MCP Server: ${MCP_SERVER_URL}`);
      consola.info(`Search API: ${MCP_API_URL}`);
      consola.log('\nUsage:');
      consola.log('  npx djangocfg-docs search "database configuration"');
      consola.log('  npx djangocfg-docs mcp');
      break;

    default:
      consola.box('DjangoCFG AI Documentation CLI');
      consola.log('Commands:');
      consola.log('  search <query>  Search documentation');
      consola.log('  mcp             Show MCP server config');
      consola.log('  info            Show help\n');
      consola.log('Examples:');
      consola.log('  npx djangocfg-docs search "database configuration"');
      consola.log('  npx djangocfg-docs search "redis cache"');
      consola.log('  npx djangocfg-docs mcp');
      break;
  }
}

main();

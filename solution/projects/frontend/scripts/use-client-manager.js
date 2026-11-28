#!/usr/bin/env node

/**
 * Use Client Directive Manager
 * 
 * Universal script to manage 'use client' directives in Next.js App Router projects.
 * Can scan, add, or remove directives from React components.
 * 
 * Usage:
 *   node use-client-manager.js scan [path]   - Scan for files needing 'use client'
 *   node use-client-manager.js add [path]    - Add 'use client' to files that need it
 *   node use-client-manager.js remove [path] - Remove 'use client' from all files
 * 
 * If no path is provided, defaults to ../packages (relative to this script)
 */

const fs = require('fs');
const path = require('path');

// Third-party libraries that require client-side
const CLIENT_LIBRARIES = [
  '@radix-ui',
  'vaul',
  'recharts',
  'react-hook-form',
  'cmdk',
  'embla-carousel-react',
  'react-day-picker',
  'react-resizable-panels',
  'sonner',
  'input-otp',
  'framer-motion',
  '@vidstack',
];

// React patterns that require client-side
const CLIENT_PATTERNS = [
  // React Hooks
  /\buseState\b/,
  /\buseEffect\b/,
  /\buseContext\b/,
  /\buseReducer\b/,
  /\buseCallback\b/,
  /\buseMemo\b/,
  /\buseRef\b/,
  /\buseId\b/,
  /\buseTransition\b/,
  /\buseDeferredValue\b/,
  /\buseLayoutEffect\b/,
  /\buseImperativeHandle\b/,
  // React Context
  /\bcreateContext\b/,
  // Browser APIs
  /\bwindow\./,
  /\bdocument\./,
  /\bnavigator\./,
  /\blocalStorage\b/,
  /\bsessionStorage\b/,
  /\baddEventListener\b/,
  // Event Handlers
  /\bonClick\s*=/,
  /\bonChange\s*=/,
  /\bonSubmit\s*=/,
  // Next.js Pages Router (needs client)
  /from ['"]next\/router['"]/,
];

function hasUseClientDirective(content) {
  return /^['"]use client['"]/m.test(content);
}

function needsUseClient(content) {
  // Already has directive
  if (hasUseClientDirective(content)) {
    return { needs: false, reason: 'Already has directive' };
  }
  
  // Check for third-party libraries
  for (const lib of CLIENT_LIBRARIES) {
    if (content.includes(`from "${lib}`) || content.includes(`from '${lib}`)) {
      return { needs: true, reason: `Uses ${lib}` };
    }
  }
  
  // Check for React patterns
  for (const pattern of CLIENT_PATTERNS) {
    if (pattern.test(content)) {
      return { needs: true, reason: `Uses ${pattern.source.replace(/\\b/g, '')}` };
    }
  }
  
  return { needs: false, reason: 'No client-side patterns detected' };
}

function addUseClientDirective(content) {
  // Skip if already has directive
  if (hasUseClientDirective(content)) {
    return { modified: false, content };
  }
  
  // Add at the top, before any imports
  const newContent = `"use client"\n\n${content}`;
  return { modified: true, content: newContent };
}

function removeUseClientDirective(content) {
  // Remove 'use client' directive and any following empty lines
  const newContent = content.replace(/^['"]use client['"]\s*\n+/m, '');
  return { modified: content !== newContent, content: newContent };
}

function processDirectory(dir, action, results = []) {
  if (!fs.existsSync(dir)) {
    console.error(`❌ Directory not found: ${dir}`);
    return results;
  }

  const files = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const file of files) {
    const fullPath = path.join(dir, file.name);
    
    // Skip node_modules and dist directories
    if (file.isDirectory()) {
      if (file.name === 'node_modules' || file.name === 'dist' || file.name === '.next') {
        continue;
      }
      processDirectory(fullPath, action, results);
    } else if (file.name.endsWith('.tsx') || file.name.endsWith('.ts')) {
      const content = fs.readFileSync(fullPath, 'utf8');
      
      if (action === 'scan') {
        const check = needsUseClient(content);
        if (check.needs) {
          results.push({
            file: file.name,
            path: fullPath,
            reason: check.reason
          });
        }
      } else if (action === 'add') {
        const check = needsUseClient(content);
        if (check.needs) {
          const result = addUseClientDirective(content);
          if (result.modified) {
            fs.writeFileSync(fullPath, result.content, 'utf8');
            results.push({
              file: file.name,
              path: fullPath,
              reason: check.reason
            });
          }
        }
      } else if (action === 'remove') {
        const result = removeUseClientDirective(content);
        if (result.modified) {
          fs.writeFileSync(fullPath, result.content, 'utf8');
          results.push({
            file: file.name,
            path: fullPath
          });
        }
      }
    }
  }
  
  return results;
}

function printHelp() {
  console.log(`
Use Client Directive Manager

Usage:
  node use-client-manager.js <command> [path]

Commands:
  scan [path]   - Scan for files that need 'use client' directive
  add [path]    - Add 'use client' to files that need it
  remove [path] - Remove 'use client' from all files

Arguments:
  path          - Optional path to scan (default: ../packages)

Examples:
  node use-client-manager.js scan
  node use-client-manager.js add ../ui/src/components
  node use-client-manager.js remove ../ui/src/hooks
`);
}

// Main execution
const args = process.argv.slice(2);
const command = args[0];
// Default to scanning all packages
const targetPath = args[1] || path.join(__dirname, '..', 'packages');

if (!command || command === 'help' || command === '--help' || command === '-h') {
  printHelp();
  process.exit(0);
}

if (!['scan', 'add', 'remove'].includes(command)) {
  console.error(`❌ Unknown command: ${command}`);
  printHelp();
  process.exit(1);
}

console.log(`🔍 ${command.charAt(0).toUpperCase() + command.slice(1)}ing in: ${targetPath}\n`);

const results = processDirectory(targetPath, command);

if (command === 'scan') {
  if (results.length === 0) {
    console.log('✅ All files already have "use client" directive where needed!\n');
  } else {
    console.log(`⚠️  Found ${results.length} file(s) that need "use client":\n`);
    results.forEach(({ file, reason }) => {
      console.log(`  📄 ${file}`);
      console.log(`     → ${reason}\n`);
    });
    console.log(`\n💡 Run 'node use-client-manager.js add' to fix automatically.`);
  }
} else if (command === 'add') {
  if (results.length === 0) {
    console.log('✅ No files needed "use client" directive.\n');
  } else {
    console.log(`✅ Added "use client" to ${results.length} file(s):\n`);
    results.forEach(({ file, reason }) => {
      console.log(`  📄 ${file}`);
      console.log(`     → ${reason}\n`);
    });
  }
} else if (command === 'remove') {
  if (results.length === 0) {
    console.log('✅ No files had "use client" directive to remove.\n');
  } else {
    console.log(`✅ Removed "use client" from ${results.length} file(s):\n`);
    results.forEach(({ file }) => {
      console.log(`  📄 ${file}`);
    });
  }
}

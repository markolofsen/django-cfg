/**
 * Language Detection & Mapping
 *
 * Maps file extensions to Monaco Editor language IDs.
 * Monaco supports 80+ languages out of the box.
 */

/**
 * File extension to Monaco language ID mapping
 */
export const LANGUAGE_MAP: Record<string, string> = {
  // Web
  '.html': 'html',
  '.htm': 'html',
  '.xhtml': 'html',
  '.vue': 'html',
  '.svelte': 'html',

  // CSS
  '.css': 'css',
  '.scss': 'scss',
  '.sass': 'scss',
  '.less': 'less',

  // JavaScript/TypeScript
  '.js': 'javascript',
  '.mjs': 'javascript',
  '.cjs': 'javascript',
  '.jsx': 'javascript',
  '.ts': 'typescript',
  '.tsx': 'typescript',
  '.mts': 'typescript',
  '.cts': 'typescript',

  // Data formats
  '.json': 'json',
  '.jsonc': 'json',
  '.json5': 'json',
  '.yaml': 'yaml',
  '.yml': 'yaml',
  '.toml': 'ini',
  '.xml': 'xml',
  '.svg': 'xml',
  '.xsl': 'xml',
  '.xsd': 'xml',

  // Markdown & Documentation
  '.md': 'markdown',
  '.mdx': 'markdown',
  '.markdown': 'markdown',
  '.rst': 'restructuredtext',
  '.txt': 'plaintext',
  '.text': 'plaintext',

  // Programming languages
  '.py': 'python',
  '.pyw': 'python',
  '.pyi': 'python',
  '.rb': 'ruby',
  '.rake': 'ruby',
  '.gemspec': 'ruby',
  '.php': 'php',
  '.phtml': 'php',
  '.java': 'java',
  '.kt': 'kotlin',
  '.kts': 'kotlin',
  '.scala': 'scala',
  '.go': 'go',
  '.rs': 'rust',
  '.swift': 'swift',
  '.c': 'c',
  '.h': 'c',
  '.cpp': 'cpp',
  '.cc': 'cpp',
  '.cxx': 'cpp',
  '.hpp': 'cpp',
  '.hxx': 'cpp',
  '.cs': 'csharp',
  '.fs': 'fsharp',
  '.fsx': 'fsharp',
  '.vb': 'vb',
  '.lua': 'lua',
  '.r': 'r',
  '.R': 'r',
  '.m': 'objective-c',
  '.mm': 'objective-c',
  '.pl': 'perl',
  '.pm': 'perl',
  '.ex': 'elixir',
  '.exs': 'elixir',
  '.erl': 'erlang',
  '.hrl': 'erlang',
  '.clj': 'clojure',
  '.cljs': 'clojure',
  '.cljc': 'clojure',
  '.hs': 'haskell',
  '.lhs': 'haskell',
  '.ml': 'fsharp',
  '.mli': 'fsharp',
  '.dart': 'dart',
  '.groovy': 'groovy',
  '.gradle': 'groovy',
  '.jl': 'julia',

  // Shell & Scripts
  '.sh': 'shell',
  '.bash': 'shell',
  '.zsh': 'shell',
  '.fish': 'shell',
  '.ps1': 'powershell',
  '.psm1': 'powershell',
  '.psd1': 'powershell',
  '.bat': 'bat',
  '.cmd': 'bat',

  // Config files
  '.ini': 'ini',
  '.cfg': 'ini',
  '.conf': 'ini',
  '.properties': 'ini',
  '.env': 'ini',
  '.gitignore': 'ini',
  '.gitattributes': 'ini',
  '.editorconfig': 'ini',
  '.npmrc': 'ini',

  // Database
  '.sql': 'sql',
  '.mysql': 'mysql',
  '.pgsql': 'pgsql',
  '.plsql': 'plsql',
  '.redis': 'redis',

  // Templates
  '.hbs': 'handlebars',
  '.handlebars': 'handlebars',
  '.mustache': 'handlebars',
  '.ejs': 'html',
  '.pug': 'pug',
  '.jade': 'pug',
  '.twig': 'twig',
  '.liquid': 'liquid',

  // GraphQL
  '.graphql': 'graphql',
  '.gql': 'graphql',

  // Docker
  '.dockerfile': 'dockerfile',

  // Other
  '.diff': 'diff',
  '.patch': 'diff',
  '.log': 'log',
  '.tex': 'latex',
  '.cls': 'latex',
  '.sty': 'latex',
  '.proto': 'protobuf',
  '.sol': 'sol',
  '.asm': 'mips',
  '.s': 'mips',
  '.wasm': 'wasm',
};

/**
 * Special filename mappings (without extension)
 */
const FILENAME_MAP: Record<string, string> = {
  Dockerfile: 'dockerfile',
  'docker-compose.yml': 'yaml',
  'docker-compose.yaml': 'yaml',
  Makefile: 'makefile',
  makefile: 'makefile',
  Gemfile: 'ruby',
  Rakefile: 'ruby',
  Jenkinsfile: 'groovy',
  Vagrantfile: 'ruby',
  '.bashrc': 'shell',
  '.bash_profile': 'shell',
  '.zshrc': 'shell',
  '.profile': 'shell',
  '.vimrc': 'plaintext',
  '.gitconfig': 'ini',
  '.htaccess': 'ini',
  'nginx.conf': 'ini',
  'package.json': 'json',
  'tsconfig.json': 'json',
  'jsconfig.json': 'json',
  '.prettierrc': 'json',
  '.eslintrc': 'json',
  'composer.json': 'json',
  'Cargo.toml': 'ini',
  'go.mod': 'go',
  'go.sum': 'plaintext',
  'requirements.txt': 'plaintext',
  'pyproject.toml': 'ini',
  'setup.py': 'python',
  'setup.cfg': 'ini',
};

/**
 * Get Monaco language ID from file extension
 */
export function getLanguageByExtension(extension: string): string {
  const ext = extension.startsWith('.') ? extension.toLowerCase() : `.${extension.toLowerCase()}`;
  return LANGUAGE_MAP[ext] || 'plaintext';
}

/**
 * Get Monaco language ID from filename
 * Checks special filenames first, then falls back to extension
 */
export function getLanguageByFilename(filename: string): string {
  // Check special filenames first
  if (FILENAME_MAP[filename]) {
    return FILENAME_MAP[filename];
  }

  // Extract extension
  const lastDot = filename.lastIndexOf('.');
  if (lastDot === -1) {
    return 'plaintext';
  }

  const extension = filename.slice(lastDot).toLowerCase();
  return LANGUAGE_MAP[extension] || 'plaintext';
}

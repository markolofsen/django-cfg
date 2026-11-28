/**
 * DiagramStore - Base class for building Mermaid diagrams
 * Accumulates diagram lines with proper indentation
 * @module Mermaid/builders/core/DiagramStore
 */

export interface DiagramStoreOptions {
  /** Indentation string (default: '  ' - two spaces) */
  indent?: string;
}

const DEFAULT_OPTIONS: Required<DiagramStoreOptions> = {
  indent: '  ',
};

/**
 * Base store for accumulating Mermaid diagram code
 * Handles indentation and line management
 */
export class DiagramStore {
  protected lines: string[] = [];
  protected indentLevel = 0;
  protected options: Required<DiagramStoreOptions>;

  constructor(header: string, options: DiagramStoreOptions = {}) {
    this.options = { ...DEFAULT_OPTIONS, ...options };
    this.lines.push(header);
  }

  /**
   * Add a line to the diagram with current indentation
   */
  add(line: string): this {
    const indent = this.options.indent.repeat(this.indentLevel);
    this.lines.push(indent + line);
    return this;
  }

  /**
   * Add a raw line without indentation
   */
  addRaw(line: string): this {
    this.lines.push(line);
    return this;
  }

  /**
   * Add an empty line
   */
  addBlank(): this {
    this.lines.push('');
    return this;
  }

  /**
   * Add a comment line
   */
  addComment(comment: string): this {
    return this.add(`%% ${comment}`);
  }

  /**
   * Increase indentation level
   */
  indent(): this {
    this.indentLevel++;
    return this;
  }

  /**
   * Decrease indentation level
   */
  dedent(): this {
    if (this.indentLevel > 0) {
      this.indentLevel--;
    }
    return this;
  }

  /**
   * Execute a callback within an indented block
   * @param header - Block header line
   * @param fn - Callback to execute inside the block
   * @param footer - Block footer line (default: 'end')
   */
  block(header: string, fn: () => void, footer = 'end'): this {
    this.add(header);
    this.indent();
    fn();
    this.dedent();
    this.add(footer);
    return this;
  }

  /**
   * Execute a callback within a subgraph block
   * @param name - Subgraph name/title
   * @param fn - Callback to execute inside the subgraph
   */
  subgraph(name: string, fn: () => void): this {
    return this.block(`subgraph ${name}`, fn);
  }

  /**
   * Add direction directive (for subgraphs)
   */
  direction(dir: 'TB' | 'BT' | 'LR' | 'RL'): this {
    return this.add(`direction ${dir}`);
  }

  /**
   * Get the current indentation string
   */
  getIndent(): string {
    return this.options.indent.repeat(this.indentLevel);
  }

  /**
   * Get the current indentation level
   */
  getIndentLevel(): number {
    return this.indentLevel;
  }

  /**
   * Convert the diagram to a Mermaid string
   */
  toString(): string {
    return this.lines.join('\n');
  }

  /**
   * Get all lines (for debugging)
   */
  getLines(): readonly string[] {
    return this.lines;
  }
}

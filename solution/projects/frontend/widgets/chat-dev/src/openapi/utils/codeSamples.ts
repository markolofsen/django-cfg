/**
 * Code sample generation.
 *
 * In-house, browser-safe generator for a small catalogue of languages
 * (curl / fetch / Node axios / Python requests / Go / PHP / Ruby /
 * Java OkHttp). We used to wrap Kong's ``httpsnippet`` here but it is
 * Node-only — the bundle referenced ``global`` / ``stream`` /
 * ``string_decoder`` and crashed in Vite dev. Writing our own keeps the
 * chunk small (a few kB vs ~1.5 MB) and avoids runtime polyfills.
 *
 * Adding more targets later is one function plus a row in the catalogue.
 */

import type { HarRequest } from './operationToHar';

// Prism language ids used by ``prism-react-renderer``. ``bash``,
// ``ruby``, ``java`` and ``php`` aren't in the library's default
// bundle, but our ``registerPrismLanguages`` module pulls their
// grammars from ``prismjs`` at load time so they work as first-class
// languages here.
export const CODE_SAMPLE_TARGETS = [
    { id: 'curl', label: 'cURL', prism: 'bash' },
    { id: 'fetch', label: 'JavaScript', prism: 'javascript' },
    { id: 'axios', label: 'Node (axios)', prism: 'javascript' },
    { id: 'python', label: 'Python', prism: 'python' },
    { id: 'go', label: 'Go', prism: 'go' },
    { id: 'php', label: 'PHP', prism: 'php' },
    { id: 'ruby', label: 'Ruby', prism: 'ruby' },
    { id: 'java', label: 'Java', prism: 'java' },
] as const;

export type CodeSampleTargetId = typeof CODE_SAMPLE_TARGETS[number]['id'];

// ─── Body literal helpers ─────────────────────────────────────────────────────
//
// Pre-formatted JSON bodies (``JSON.stringify(value, null, 2)``) carry
// real newlines that we want the snippet to preserve — a one-line
// escaped string like ``"{\n  \"id\": 10,\n …}"`` reads as a wall of
// escape sequences. Each helper below returns a multi-line string
// literal in the target language's native syntax so the snippet reads
// like hand-written code.

/** Go raw string literal — uses backticks. Falls back to a double-
 *  quoted escaped literal when the body itself contains a backtick. */
function goRawString(s: string): string {
    return s.includes('`') ? JSON.stringify(s) : `\`${s}\``;
}

/** Ruby squiggly heredoc — ``<<~JSON`` style strips common leading
 *  whitespace. Safe unless the body literally contains ``JSON`` on a
 *  line by itself, which is vanishingly rare. */
function rubyHeredoc(s: string): string {
    return `<<~JSON\n${s}\nJSON`;
}

/** PHP heredoc — ``<<<JSON`` style. Same caveat as Ruby's. Trailing
 *  ``JSON;`` must sit at column 0 (enforced by this template). */
function phpHeredoc(s: string): string {
    return `<<<JSON\n${s}\nJSON`;
}

/** Java 15+ text block — ``"""``. Falls back to an escaped literal
 *  when the body contains that sequence. */
function javaTextBlock(s: string): string {
    if (s.includes('"""')) return JSON.stringify(s);
    // Text blocks need the opening ``"""`` on its own line — the
    // parser strips the newline that immediately follows the delimiter.
    return `"""\n${s}\n"""`;
}

function fullUrl(har: HarRequest): string {
    if (!har.queryString.length) return har.url;
    const qs = har.queryString
        .map((p) => `${encodeURIComponent(p.name)}=${encodeURIComponent(p.value)}`)
        .join('&');
    const sep = har.url.includes('?') ? '&' : '?';
    return `${har.url}${sep}${qs}`;
}

function shellEscape(value: string): string {
    return `'${value.replace(/'/g, `'\\''`)}'`;
}

function renderCurl(har: HarRequest): string {
    const lines: string[] = [`curl -X ${har.method} ${shellEscape(fullUrl(har))}`];
    for (const h of har.headers) {
        lines.push(`  -H ${shellEscape(`${h.name}: ${h.value}`)}`);
    }
    if (har.postData?.text) {
        lines.push(`  -d ${shellEscape(har.postData.text)}`);
    }
    return lines.join(' \\\n');
}

function jsHeadersLiteral(har: HarRequest, indent: string): string {
    if (!har.headers.length) return '{}';
    const entries = har.headers
        .map((h) => `${indent}  ${JSON.stringify(h.name)}: ${JSON.stringify(h.value)}`)
        .join(',\n');
    return `{\n${entries},\n${indent}}`;
}

/** JS template literal — backtick string that preserves newlines and
 *  escapes backticks / ``${`` sequences. Makes multi-line JSON body
 *  readable inside the fetch() options. */
function jsTemplateLiteral(s: string): string {
    if (/[`$]/.test(s)) return JSON.stringify(s);
    return `\`${s}\``;
}

function renderFetch(har: HarRequest): string {
    const url = fullUrl(har);
    const options: string[] = [`  method: ${JSON.stringify(har.method)}`];
    if (har.headers.length) {
        options.push(`  headers: ${jsHeadersLiteral(har, '  ')}`);
    }
    if (har.postData?.text) {
        options.push(`  body: ${jsTemplateLiteral(har.postData.text)}`);
    }
    return `const response = await fetch(${JSON.stringify(url)}, {\n${options.join(',\n')},\n});\nconst data = await response.json();`;
}

function renderAxios(har: HarRequest): string {
    const url = fullUrl(har);
    const config: string[] = [
        `  method: ${JSON.stringify(har.method.toLowerCase())}`,
        `  url: ${JSON.stringify(url)}`,
    ];
    if (har.headers.length) {
        config.push(`  headers: ${jsHeadersLiteral(har, '  ')}`);
    }
    if (har.postData?.text) {
        // Axios auto-serializes objects; we pass the raw JSON string as data.
        config.push(`  data: ${har.postData.text}`);
    }
    return `import axios from 'axios';\n\nconst { data } = await axios({\n${config.join(',\n')},\n});`;
}

function renderPython(har: HarRequest): string {
    const lines: string[] = [`import requests`, ``];
    lines.push(`url = ${JSON.stringify(fullUrl(har))}`);
    if (har.headers.length) {
        const headerEntries = har.headers
            .map((h) => `    ${JSON.stringify(h.name)}: ${JSON.stringify(h.value)}`)
            .join(',\n');
        lines.push(`headers = {\n${headerEntries},\n}`);
    }
    if (har.postData?.text) {
        // ``json=payload`` on ``requests`` expects a Python object, not
        // a JSON string — so we leave the body as a raw dict literal
        // (which Python parses identically to the JSON source for the
        // shapes we generate). No wrapping helper needed here.
        lines.push(`payload = ${har.postData.text}`);
    }
    const args = [`url`];
    if (har.headers.length) args.push(`headers=headers`);
    if (har.postData?.text) args.push(`json=payload`);
    lines.push(``, `response = requests.${har.method.toLowerCase()}(${args.join(', ')})`);
    lines.push(`data = response.json()`);
    return lines.join('\n');
}

function renderGo(har: HarRequest): string {
    const url = fullUrl(har);
    const lines: string[] = [
        `package main`,
        ``,
        `import (`,
        `    "fmt"`,
        `    "io"`,
    ];
    if (har.postData?.text) lines.push(`    "strings"`);
    lines.push(`    "net/http"`);
    lines.push(`)`, ``, `func main() {`);
    if (har.postData?.text) {
        lines.push(`    payload := strings.NewReader(${goRawString(har.postData.text)})`);
        lines.push(`    req, _ := http.NewRequest(${JSON.stringify(har.method)}, ${JSON.stringify(url)}, payload)`);
    } else {
        lines.push(`    req, _ := http.NewRequest(${JSON.stringify(har.method)}, ${JSON.stringify(url)}, nil)`);
    }
    for (const h of har.headers) {
        lines.push(`    req.Header.Add(${JSON.stringify(h.name)}, ${JSON.stringify(h.value)})`);
    }
    lines.push(
        ``,
        `    res, _ := http.DefaultClient.Do(req)`,
        `    defer res.Body.Close()`,
        `    body, _ := io.ReadAll(res.Body)`,
        `    fmt.Println(string(body))`,
        `}`,
    );
    return lines.join('\n');
}

function renderPhp(har: HarRequest): string {
    const lines: string[] = [`<?php`, ``, `$curl = curl_init();`, ``, `curl_setopt_array($curl, [`];
    lines.push(`    CURLOPT_URL => ${JSON.stringify(fullUrl(har))},`);
    lines.push(`    CURLOPT_RETURNTRANSFER => true,`);
    lines.push(`    CURLOPT_CUSTOMREQUEST => ${JSON.stringify(har.method)},`);
    if (har.postData?.text) {
        lines.push(`    CURLOPT_POSTFIELDS => ${phpHeredoc(har.postData.text)},`);
    }
    if (har.headers.length) {
        const headerList = har.headers
            .map((h) => `        ${JSON.stringify(`${h.name}: ${h.value}`)}`)
            .join(',\n');
        lines.push(`    CURLOPT_HTTPHEADER => [\n${headerList},\n    ],`);
    }
    lines.push(`]);`, ``, `$response = curl_exec($curl);`, `curl_close($curl);`, `echo $response;`);
    return lines.join('\n');
}

function renderRuby(har: HarRequest): string {
    const lines: string[] = [
        `require 'net/http'`,
        `require 'uri'`,
        `require 'json'`,
        ``,
        `uri = URI(${JSON.stringify(fullUrl(har))})`,
        `http = Net::HTTP.new(uri.host, uri.port)`,
        `http.use_ssl = uri.scheme == 'https'`,
        ``,
    ];
    const methodClass = har.method.charAt(0) + har.method.slice(1).toLowerCase();
    lines.push(`request = Net::HTTP::${methodClass}.new(uri)`);
    for (const h of har.headers) {
        lines.push(`request[${JSON.stringify(h.name)}] = ${JSON.stringify(h.value)}`);
    }
    if (har.postData?.text) {
        lines.push(`request.body = ${rubyHeredoc(har.postData.text)}`);
    }
    lines.push(``, `response = http.request(request)`, `puts response.body`);
    return lines.join('\n');
}

function renderJava(har: HarRequest): string {
    const lines: string[] = [
        `OkHttpClient client = new OkHttpClient();`,
        ``,
    ];
    if (har.postData?.text) {
        lines.push(
            `MediaType mediaType = MediaType.parse("application/json");`,
            `RequestBody body = RequestBody.create(mediaType, ${javaTextBlock(har.postData.text)});`,
            ``,
        );
    }
    lines.push(`Request request = new Request.Builder()`);
    lines.push(`  .url(${JSON.stringify(fullUrl(har))})`);
    if (har.postData?.text) {
        lines.push(`  .method(${JSON.stringify(har.method)}, body)`);
    } else {
        lines.push(`  .method(${JSON.stringify(har.method)}, null)`);
    }
    for (const h of har.headers) {
        lines.push(`  .addHeader(${JSON.stringify(h.name)}, ${JSON.stringify(h.value)})`);
    }
    lines.push(`  .build();`, ``, `Response response = client.newCall(request).execute();`);
    return lines.join('\n');
}

const RENDERERS: Record<CodeSampleTargetId, (har: HarRequest) => string> = {
    curl: renderCurl,
    fetch: renderFetch,
    axios: renderAxios,
    python: renderPython,
    go: renderGo,
    php: renderPhp,
    ruby: renderRuby,
    java: renderJava,
};

export function renderSnippet(har: HarRequest, targetId: CodeSampleTargetId): string | null {
    const renderer = RENDERERS[targetId];
    if (!renderer) return null;
    try {
        return renderer(har);
    } catch {
        return null;
    }
}

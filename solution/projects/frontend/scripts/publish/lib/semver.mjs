export const BUMPS = ['patch', 'minor', 'major'];

export function parse(v) {
  const m = /^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$/.exec(v);
  if (!m) throw new Error(`Not a semver version: "${v}"`);
  return { major: +m[1], minor: +m[2], patch: +m[3], pre: m[4] };
}

export function bump(v, kind) {
  const { major, minor, patch } = parse(v);
  switch (kind) {
    case 'patch': return `${major}.${minor}.${patch + 1}`;
    case 'minor': return `${major}.${minor + 1}.0`;
    case 'major': return `${major + 1}.0.0`;
    default: throw new Error(`Unknown bump "${kind}" (expected ${BUMPS.join('|')})`);
  }
}

export function compare(a, b) {
  const x = parse(a); const y = parse(b);
  for (const k of ['major', 'minor', 'patch']) if (x[k] !== y[k]) return x[k] - y[k];
  if (x.pre === y.pre) return 0;
  if (!x.pre) return 1;
  if (!y.pre) return -1;
  return x.pre < y.pre ? -1 : 1;
}

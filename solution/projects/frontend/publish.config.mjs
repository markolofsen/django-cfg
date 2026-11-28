/**
 * What `scripts/publish` publishes, and how each group is versioned.
 *
 * Two policies:
 *
 *   synced       — every member carries the master's version. One bump moves
 *                  them all, so a consumer pins one number for the whole
 *                  framework. `packages/*`.
 *   independent  — every member has its own version and only moves when it
 *                  is published. `widgets/*`.
 *
 * Membership is discovered: every `package.json` one level under `<dir>/` that is not
 * `private: true` is a member. Mark a package `private` to keep it out.
 */
export default {
  scope: '@djangocfg',
  tmpDir: '.tmp/publish',
  groups: [
    { name: 'packages', dir: 'packages', versioning: 'synced', master: 'nextjs' },
    { name: 'widgets', dir: 'widgets', versioning: 'independent' },
  ],
};

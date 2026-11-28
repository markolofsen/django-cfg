/**
 * The chat's own message sounds, inlined as base64 data URLs: a host needs no `.mp3` loader, no asset route and no type shim.
 * To replace one: `base64 -i <file>.mp3` and paste the result into the matching module.
 */
export { default as sent } from "./sent";
export { default as received } from "./received";
export { default as start } from "./start";
export { default as error } from "./error";

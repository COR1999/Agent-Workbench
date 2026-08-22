---
applies-to: [node, typescript]
discovered: 2026-08
status: active
---

# `btoa` is Latin-1 only, and raw base64 is not URL-safe

`btoa` throws `InvalidCharacterError` on any character above U+00FF, and its
output can contain `+`, `/`, and `=`. Encoding JSON that embeds external
strings — API error bodies, display names, anything user-visible — therefore
either crashes at encode time or produces URLs that break routing and length
limits. Both failures are silent in practice: a click handler with no catch
just does nothing, and ASCII-only test payloads hide the trap completely.

**Cost:** A share-a-snapshot feature failed silently whenever results included
non-ASCII provider error text; large payloads also produced multi-KB URL paths
that browsers and CDNs may reject. The defect survived review because every
hand test used clean ASCII data.

**Instead:** To put arbitrary data in a URL: `new TextEncoder().encode(json)`
→ build a binary string from the bytes → `btoa` → map to base64url (`+`→`-`,
`/`→`_`, strip `=` padding). Decoding reverses the mapping, re-pads, then
`atob` + `TextDecoder`. Carry metadata like timestamps inside the payload
rather than trying to parse meaning out of the encoded blob.

**Strongest rung available:** one shared `encodeToken`/`decodeToken` helper
with a roundtrip test whose fixture contains non-ASCII input; if the stack
supports custom lint rules, banning bare `btoa(` outside that helper is the
stronger rung.

---
name: sharepoint-html
description: Build, optimise, validate, package and troubleshoot HTML pages for Microsoft's modern SharePoint HTML Pages feature (the Site Pages library). Use when creating or adapting standalone HTML, dashboards, interactive reports, slide-style presentations or lightweight browser tools for upload to SharePoint, or when an uploaded HTML page breaks, downloads instead of rendering, or blocks scripts, images, fonts, media, frames or links. SharePoint HTML Pages are a sandbox, not unrestricted web hosting.
license: Reusable guidance; verify current Microsoft documentation before relying on product behaviour.
metadata:
  product: SharePoint in Microsoft 365
  language: en-GB
  version: "2.0"
  last-reviewed: 2026-11-26
---

# SharePoint HTML pages

Build an `.html` file, or an HTML folder (page plus supporting files), that is uploaded to a site's **Site Pages** library, then published and shared under SharePoint permissions. An HTML file in an ordinary document library is not a SharePoint HTML page.

## Sources

- Primary: [Create, upload, edit, and publish HTML pages in SharePoint](https://support.microsoft.com/en-us/sharepoint/create-edit-publish-html-pages). Re-read it before making capability claims; the feature is new and changes often.
- Context only: [Publish in SharePoint](https://support.microsoft.com/en-us/sharepoint/sites-pages/getting-started-with-publish-in-sharepoint), [modern page lifecycle](https://support.microsoft.com/en-us/sharepoint/sites-pages/management-and-lifecycle-of-a-sharepoint-modern-page), [SharePoint limits](https://learn.microsoft.com/en-us/office365/servicedescriptions/sharepoint-online-service-description/sharepoint-online-limits), [custom script security](https://learn.microsoft.com/en-us/sharepoint/security-considerations-of-allowing-custom-script), [SharePoint Framework](https://learn.microsoft.com/en-us/sharepoint/dev/spfx/sharepoint-framework-overview). These describe modern ASPX pages, custom script or SPFx; do not apply them to HTML pages automatically.

Label every claim as **documented** (Microsoft article), **observed** (tenant probe, with date) or **untested**. When they disagree, say so and probe.

## Platform facts (documented, reviewed 2026-11-26)

### Enablement and roles

- HTML pages are on by default. A site owner can turn them off or on in **Site Pages** > **File types** > **Allow HTML files**. This does not affect HTML in document libraries. It cannot be restricted at tenant level. The PnP `Get-PnPFeature` cmdlet shows feature `HtmlPages` (`b35f1374-dbc0-454a-973c-2a0ab62d5afa`) when allowed.
- Upload, move, edit on canvas and publish need Edit/Contribute. Viewing needs Read.
- Creating or editing a page through the Copilot chat pane, or opening the creation screen from **+ New** / **Create**, needs a Microsoft 365 Copilot licence. Uploading from the **Site Pages** library does not.

### Getting a page into Site Pages

- **Site Pages** > **Create or upload** > **Upload HTML page** or **Upload HTML folder**.
- From a document library: **Edit in SharePoint** or **Move to** moves the file (it leaves the original library); **Copy to** keeps the original.
- Non-HTML content embedded in the HTML or included in a folder is uploaded to **Site assets**.
- Authors can edit text and images directly on the canvas (Ctrl+Click reaches hidden tabs or sections). Treat the build source as the master copy; re-uploading replaces canvas edits.

### Size

- Maximum HTML file: **10 MB**, excluding images and videos that SharePoint copies to **Site assets**. Do not invent a lower Microsoft limit; label internal targets as recommendations.
- Untested: whether base64 data URIs are extracted to Site assets (and so excluded) or count towards the 10 MB. Assume they count.
- To shrink: link hosted assets instead of embedding, cut inline CSS/JS, remove unused markup.

### Sandbox

- Rendered in a **sandboxed iframe** with a Content Security Policy. The page cannot reach the SharePoint header, footer, navigation, cookies or parent frame.
- JavaScript in the same HTML file runs. No `localStorage`. No arbitrary `fetch` or outbound API calls (Graph, SharePoint REST, third-party). No cross-tenant communication.
- Libraries: only Microsoft-managed **Chart.js, Mermaid, React, Fluent UI and Babylon** from a Microsoft CDN. No other CDN or open-source script locations. Microsoft does not publish the loading syntax; do not guess it. Prefer plain HTML, CSS, inline SVG and JavaScript.
- Live data from SharePoint lists and Excel is supported; the mechanism is not documented. Third-party live data (e.g. Jira) is not.

### Capabilities

| Capability | Status |
|---|---|
| Images: user-added (base64 or same-domain URL), stock, organisation assets | Yes |
| Video overlay (same-domain URL) | Yes |
| Inline video and audio | Yes, ≤8 MB per item and ≤24 MB per page across media; larger items fall back to overlay or link. **Conflicts with the 2026-10-06 observation below. Probe first.** |
| Word, Excel, PowerPoint, PDF opening in a new tab (same domain) | Yes; inline display: No |
| Links: same site, same tenant, in-page anchors | Yes |
| Links: other tenants, outside SharePoint | Yes, once the domain is on the site's **HTML Field Security** allow list |
| Scheduling, approvals, analytics, send to email as a link | Yes |
| Site branding | Only for Copilot-created or Copilot-updated pages; never applied to uploaded HTML, nor taken from brand centre or the organisation asset library |
| Teams desktop app (view and edit) | Yes |
| Teams mobile, SharePoint iOS/Android apps, mobile editing | No |
| News post, template, private drafts, co-authoring, reactions/comments, rich email, Amplify to Teams/Viva Engage, AI-generated images | No |

Allow list: **Settings** > **Site information** > **View all site settings** > **HTML Field Security**. A blocked link shows "This link can't be opened because your organization doesn't allow access to this site."

## Field observations (2026-10-06, one tenant)

Captured from `securitypolicyviolation.originalPolicy` inside an uploaded page. Tenant- and release-dependent; re-capture with the probe (workflow step 5).

```text
default-src 'none'; script-src 'unsafe-inline' 'unsafe-eval'; style-src 'unsafe-inline';
img-src data: blob: <tenant SharePoint cache path>; font-src data: blob:;
frame-src 'none'; connect-src 'none'; worker-src 'none'; object-src 'none';
base-uri 'none'; form-action 'none';
```

- Only inline `<script>` and `<style>` ran. Do not assume `<script src>` or `<link rel="stylesheet">` from a folder upload will load; whether SharePoint rewrites them was not tested.
- `unsafe-eval` was allowed, but avoid `eval`, `new Function` and string `setTimeout` so the page survives a tighter policy.
- Images and fonts loaded only from `data:`/`blob:` (plus the cache path). Remote image URLs failed. Embed fonts or use system fonts.
- No `media-src`, so `<video>`/`<audio>` were blocked even with `data:`/`blob:` sources. Microsoft now documents inline media; re-probe before relying on either.
- `frame-src 'none'` blocked every `<iframe>`, including `srcdoc`, Stream and other embed players, and the tenant's own domain.
- `connect-src`/`form-action 'none'`: no fetch, XHR, WebSocket or form submission.
- `location` was `about:srcdoc`, origin `null`, base URL `blob:`. The page cannot see its SharePoint URL, so query strings, `location.href`, `document.referrer` and relative links do not work. Relative links fail with the "can't be opened" error.
- A poster image linked to a video's absolute `https://` URL worked. It played in a new browser tab, or the default browser from Teams desktop.
- Single-file mode (inline CSS, JS and data-URI images) worked end to end.

## Fit check

Use HTML pages for self-contained interactive reports, explainers, dashboards with data embedded at build time, presentations, and browser-only calculators or tools.

Do not use them when the solution needs arbitrary or authenticated API calls, server code, CRUD beyond the documented list/Excel support, unapproved libraries, browser storage, multi-route hosting, service workers or background processing. Recommend a governed app host or SPFx, and do not invent the organisation's approved route.

## Workflow

### 1. Inspect

- Find the entry HTML. List every `src`, `href`, `url(...)`, import, `fetch`, XHR, WebSocket, worker, iframe and storage call.
- Note bundler assumptions (root-absolute paths, hashed chunks, lazy chunk loading), external domains, and total and per-asset size.
- Classify each dependency: inline-safe, packaged asset, Microsoft-managed library, same-domain link, allow-list link, unsupported, or untested.

### 2. Remove unsupported behaviour

Replace or remove: API calls and CDN scripts; browser storage; parent-frame access and `postMessage`; localhost and dev paths; unresolved build placeholders; `<iframe>`/`srcdoc` wrappers (render views in one document); routing through `location` or query strings (switch views in-page); `eval`-style code (use an explicit dispatcher); URL-based debug switches (use build-time flags).

Do not silently remove external links; list them for allow-listing. If removal changes what the user asked for, say so and propose a static or pre-generated alternative.

### 3. Package

- **Single file** (default): inline CSS, JS and deduplicated data-URI images, generated by a build script from readable sources. Validated in a tenant. Example: [assets/lotus-gallery-interactive.html](assets/lotus-gallery-interactive.html).
- **HTML folder**: only when embedding would push the HTML near 10 MB, and only after the probe shows each asset type (CSS, JS, image) loads from Site assets. Use relative forward-slash paths.
- Host large videos and documents in a normal document library whose permissions match the page audience. Link them by absolute `https://` URL with `target="_blank" rel="noopener"`.
- Make the location of linked files a build parameter. Prefer path-based URLs to GUID URLs so a move to another site needs only a rebuild.

### 4. Implement

- `<!doctype html>`, `<meta charset="utf-8">`, responsive viewport, `lang`.
- Semantic, keyboard-operable markup with visible focus, adequate contrast, `alt` text (`alt=""` if decorative), reduced-motion support, and a skip link. Uploaded HTML gets no automatic accessibility or branding; build both in.
- Defensive JavaScript that shows visible error states. Keep the first view usable before scripts finish.
- Fixed-size content (slides, artboards): scale to fit **both** `innerWidth` and `innerHeight`, centre, and recompute on `resize`. SharePoint chrome and Teams reduce the height, so width-only scaling clips.
- Images: resize to displayed size. Per image, keep whichever is smaller: the original, lossless WebP or lossy WebP (one build went from ~11 MB to ~5 MB). Animated GIF beat animated WebP. Store each distinct image once, keyed by content hash, and cache re-encodes by hash. Trim corrupt or near-black final GIF frames. Never use a SharePoint sharing-page URL as an image source.
- No secrets, personal data, source maps, debug output, or sensitive comments and embedded JSON. Everything shipped is readable by viewers, and permissions are not secret storage. Refuse requests to weaken browser or SharePoint security controls.

### 5. Probe the tenant

Before relying on frames, media, fonts, external files or links, upload a build with a **build-time** probe flag (off by default) that shows an on-screen log of:

- `location`, `document.baseURI`, `location.origin`, `location.ancestorOrigins` (reveals Teams hosting);
- user agent, window size, pixel ratio;
- every `securitypolicyviolation` (`violatedDirective`, `blockedURI`, `originalPolicy`);
- `error` events, failed resource loads, and link clicks with their resolved URLs.

Keep it free of user data. Rebuild without it for delivery, and scan the output to confirm it is off. Re-probe when behaviour changes or something is reported broken. Update this skill when an observation contradicts it.

### 6. Validate locally

Run existing project checks, then at least:

- HTML and JavaScript syntax; local-reference resolution; size report; console errors.
- Accessibility smoke test, and responsive check including a short, wide window.
- Serve the page with the observed policy as a `Content-Security-Policy` header. Success without it proves nothing.
- Forbidden-pattern scan. Inspect each hit and record the decision:

```text
fetch( XMLHttpRequest axios WebSocket EventSource localStorage sessionStorage indexedDB
navigator.serviceWorker new Worker( window.parent window.top postMessage( localhost
cdn.jsdelivr.net unpkg.com cdnjs.cloudflare.com eval( new Function( <iframe <script src <video <audio
```

### 7. Deliver

- The HTML file (or folder), a `README.md` with upload steps, and a `validation-report.md` covering: sizes and largest assets, external domains and the allow-list entries needed, removed or replaced features, untested items, and browsers and viewports tested.
- Exclude `node_modules`, caches, source maps, `.env` files and unrelated sources.

## Publish and test in SharePoint

1. In **Site Pages**, choose **Create or upload** > **Upload HTML page** or **Upload HTML folder**. If the option is missing, ask a site owner to allow HTML files.
2. Open the page and check it in edit mode.
3. Select **Publish** (or **Save and close** to keep a draft). Publishing shows the current version to people who already have access; it grants no new permissions.
4. Re-test the published URL as a normal viewer: assets, every link (same site, tenant, cross-tenant, external), absolute video and document links, keyboard use, layout at phone to wide-desktop sizes, fixed content fitting without scrolling, Teams desktop (fit, controls, outbound links open in the browser), no console errors, probe off.

If the file downloads instead of rendering, or works in preview but not as a page: confirm it is in **Site Pages**, HTML is allowed, and the file is under 10 MB. Then test the published view rather than a viewer or preview, inspect console and CSP errors, check allow-list needs and unsupported scripts, APIs or storage, and check permissions on the page and its assets. Do not claim an undocumented preview-size limit.

## Report format

```markdown
## Compatibility assessment
- Packaging mode / blockers / asset strategy / external domains / size

## Changes made
## Validation
## Upload instructions
## Tenant-side checks still needed
```

## Done when

- The HTML is under 10 MB and every local reference resolves.
- Unsupported API, CDN, storage, frame and media assumptions are removed or reported.
- External domains are listed with their allow-list needs.
- Assets are deliberately chosen and optimised.
- The page is responsive and keyboard-usable.
- README and validation report are included, with no secrets or dev files.
- The probe is off.
- Anything verifiable only in the tenant is marked as a tenant-side test.
- Never claim SharePoint compatibility because a page works from disk or a dev server.

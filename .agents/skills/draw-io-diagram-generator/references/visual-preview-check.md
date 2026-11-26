# Visual check of a draw.io page in the browser

`validate-drawio.py` checks the XML only. It cannot tell you whether edges cross boxes or
whether labels sit on the right arrow. For LLD, DFD and sequence diagrams, check the page
visually before you deliver it.

## Procedure

1. Validate the XML first: `python .agents/skills/draw-io-diagram-generator/scripts/validate-drawio.py <file.drawio>`.
2. Start the preview server as an **attached** process (not detached), for example with
   the bash tool in `mode: "async"`:

   ```bash
   python .agents/skills/draw-io-diagram-generator/scripts/preview-serve.py <file.drawio> --port 8765
   ```

   It prints the URL and keeps serving until the process is stopped.
3. Open `http://127.0.0.1:8765/preview.html` with `openBrowserPage`. If the page is blank, see [Fixes for common problems](#fixes-for-common-problems) before changing the diagram. Use the `http` URL. The integrated browser blocks `file://` pages.
4. Check the page:
   - `screenshotPage` for layout, edge routing and label placement.
   - `readPage` for the accessibility snapshot. It lists every label as text, so you can confirm
     each label appears once and on the intended edge.
5. After every edit to the `.drawio` file, stop the server and start it again. The preview HTML
   embeds the XML when it is rendered, so a reload alone shows the old diagram. Then reload the
   browser page (`navigatePage`, `type: "reload"`) and take a new screenshot.
6. Stop the server and confirm cleanup before you finish (see [Shutdown and cleanup](#shutdown-and-cleanup-required)).

## Shutdown and cleanup (required)

Clean up before you finish the task or start on another diagram. Each step below is required.

1. **Run the server attached.** Never detach it, and never background it with `&`, `nohup` or `disown`.
   A detached server keeps running after the turn ends, holds the port and leaves its folder behind.
2. **Stop it yourself.** Use `stop_bash` with the shellId you started it with, which sends SIGTERM.
   If you must stop it by PID, use `kill <PID>` with that exact PID. Do not use `pkill` or `killall`.
3. **Read the stop message.** The output must end with `Removed temporary folder: <path> (exists: False)`.
4. **Check nothing is left.**
   - `ls -d /tmp/drawio-preview-*` should print nothing.
   - `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:<port>/preview.html` should print `000`, which means the port is free.
5. **Browser tab.** The browser tools cannot close a page. Navigate it to `about:blank` (`navigatePage`, `type: "url"`) so it no longer shows the preview.

How each way of stopping affects the temporary folder:

| How it stops | Folder removed? | What you see |
|---|---|---|
| Ctrl+C (SIGINT) or `stop_bash` (SIGTERM) | Yes | `Stopping preview server.` then `Removed temporary folder` |
| Port already in use | Yes | `Cannot listen on 127.0.0.1:<port>` and exit code 1 |
| Render fails (for example, a missing file) | Yes | The render error, then exit with the render's code |
| SIGKILL (`kill -9`, or `timeout -s KILL`) | **No** | No stop message. The folder stays |
| Session or machine crash | **No** | Same as SIGKILL |

SIGKILL cannot be trapped, so the script cannot clean up after it. The start message prints the
folder path (`Temporary folder: ...`). After a SIGKILL, check the path matches your run, then remove
that exact path with `rm -rf <path>`. Do not use a wildcard.


## Fixes for common problems

| Symptom | Cause | Fix |
|---|---|---|
| `ERR_UNEXPECTED (-9)` on a `file://` URL | The integrated browser blocks file URLs | Serve over `http://127.0.0.1` with `preview-serve.py` |
| Starting the server is denied | A detached process needs approval | Run it attached (`mode: "async"`, no `detach`) |
| Screenshot is unchanged after an edit | The page was reloaded before the preview was rebuilt | Restart `preview-serve.py`, then reload the page |
| An edge runs through another box | Auto-routing picked the wrong sides | Pin the ends in the edge style: `exitX`, `exitY`, `entryX`, `entryY` (0 to 1, relative to the shape) |
| Two edges run on top of each other near one box | They leave from the same side | Give them different `exitY` (or `entryY`) values |
| A label floats away from its arrow, or sits on a box border | The label is at the midpoint of a short gap or of a long segment, with no background | Shorten the label, add `labelBackgroundColor=#ffffff;`, and pin the edge ends so the segment is clear |
| Preview is blank and the page error is `Invalid regular expression ... Range out of order` | The page had no charset, so the UTF-8 viewer script was decoded as Latin-1 | `render-preview.py` now writes `<meta charset="utf-8">` and `charset="utf-8"` on the script. Re-run the server, then open the URL with a new query string (`preview.html?v=2`), because the browser caches the bad script |
| Preview is blank, no page error | The viewer script at `viewer.diagrams.net` could not load | Check network access with `curl -sI https://viewer.diagrams.net/js/viewer-static.min.js`; the preview needs it |
| Screenshot of a large diagram is unreadable | The viewer fits the whole page into the viewport, so text is tiny | With `runPlaywrightCode`, set `document.querySelector('.mxgraph').style.zoom='2'` and `window.scrollTo(x, y)`, then `screenshotPage` each region. `page.screenshot({path})` writes outside the workspace and `view` cannot read it, so use `screenshotPage` |

## Notes

- The preview loads the draw.io viewer from `viewer.diagrams.net`. The diagram XML stays in the
  local HTML, but the viewer script is third-party. Do not use this for diagrams that must not
  touch a third-party page.
- Keep edge labels short (for example `200`, `204`, `yes`). Use a longer label only where a
  segment is long enough to hold it.
- The preview is a check, not a deliverable. Clean it up as described in [Shutdown and cleanup](#shutdown-and-cleanup-required) before you finish.

# web/public

Static files served by `web/server.js`. `player.html` is the two-tier showpiece player (see
`web/README.md` for the two-tier explanation).

Two files land here from task B4 (the human GPU render step, `Scripts/render_cinematic.sh`), and do
not exist yet:

- `cinematic.mp4` - the rendered Movie Render Queue output, encoded to a web-ready H.264 MP4.
- `poster.jpg` - a mid-timeline poster frame, shown before the video plays.

Until both files are dropped here, `player.html` still serves and its Tier 1 video element just has
nothing to play; the server responds 404 for those two paths rather than erroring, which is the
correct, expected state before task B4.

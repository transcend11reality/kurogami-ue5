# Kurogami web player (runs in Codespaces, no GPU)

Two-tier browser delivery for the showpiece:

1. **Pre-rendered cinematic (Tier 1).** Render your environment in UE with Movie Render Queue to a
   4K MP4, save it as `public/cinematic.mp4` (and a `public/poster.jpg`). This plays for everyone,
   on any device, at near-zero serving cost. Ship this first.
2. **Interactive Pixel Streaming (Tier 2).** A GPU-backed live session embedded via iframe. Set
   `STREAM_URL` in `public/player.html` to your signalling server or managed provider.

## Run it
    npm start
Then open the forwarded port 8080 (Codespaces will offer it automatically).

## Making Tier 2 work (needs a GPU, not Codespaces)
The interactive stream requires the packaged UE app running on a GPU host plus a signalling server.
Two paths:

- **Managed provider (fastest):** Arcware, Vagon Streams, Eagle 3D Streaming, and similar. You
  upload your packaged UE build; they host the GPUs, autoscaling, and a player URL you put in
  `STREAM_URL`.
- **Self-hosted:** use Epic's open-source Pixel Streaming Infrastructure (signalling server + web
  frontend) on a cloud GPU VM (AWS g5, Azure NV, GCP). Run the packaged UE app with
  `-PixelStreamingURL=ws://SIGNALLING_HOST:8888 -RenderOffScreen`, then point `STREAM_URL` at the
  signalling server's player page. This is more ops work; budget for it.

Cost reminder: interactive Pixel Streaming is roughly one cloud GPU per concurrent viewer. Gate
access, set session timeouts, and autoscale to zero. Keep Tier 1 as the mass-reach fallback.

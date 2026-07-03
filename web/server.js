// Zero-dependency static server for the Kurogami web player.
// Runs in Codespaces or locally: `npm start`, then open the forwarded port 8080.
const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "public");
const PORT = process.env.PORT || 8080;
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css",
  ".mp4": "video/mp4", ".png": "image/png", ".jpg": "image/jpeg", ".json": "application/json" };

http.createServer((req, res) => {
  let rel = decodeURIComponent(req.url.split("?")[0]);
  if (rel === "/") rel = "/player.html";
  const file = path.join(ROOT, path.normalize(rel));
  if (!file.startsWith(ROOT)) { res.writeHead(403); return res.end("forbidden"); }
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404); return res.end("not found"); }
    res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] || "application/octet-stream" });
    res.end(data);
  });
}).listen(PORT, () => console.log("Kurogami web player on http://localhost:" + PORT));

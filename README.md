# VIDROP
Frontend: GitHub Pages. Backend: FastAPI + yt-dlp (not hosted on GitHub Pages).

## Deploy backend
Connect this repository to Render as a new Blueprint using `render.yaml`. The free tier may sleep, have rate limits, or change availability. Copy the resulting `https://...onrender.com` URL. Open VIDROP, enter that address in the API server setting, and save. Check `/health` for status.

This is a prototype, not a production download service. Public, unprotected content only; platforms may block extraction. No DRM bypass, account login, cookies, watermark-removal guarantee, or download guarantee. Some media URLs require headers, expire, or fail iPhone cross-origin access. Do not expose an unrestricted resolver publicly without rate limits, abuse protection, egress limits, and a SSRF review. Use only content you have rights to save.

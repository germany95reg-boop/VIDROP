import os, re, ipaddress, socket
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import yt_dlp

app = FastAPI(title="VIDROP API", version="0.1.0")
origins = [s.strip() for s in os.getenv("ALLOWED_ORIGINS", "https://germany95reg-boop.github.io").split(",") if s.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

class VideoRequest(BaseModel):
    url: str

def validate_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise HTTPException(400, "Use a public HTTPS video URL")
    host = parsed.hostname.lower().rstrip(".")
    if host in ("localhost",) or host.endswith((".localhost", ".local", ".internal")):
        raise HTTPException(400, "Invalid host")
    try:
        addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
            raise HTTPException(400, "Private host not allowed")
    except socket.gaierror:
        raise HTTPException(400, "Host not found")
    # Restrict to explicitly supported public platforms; no arbitrary URL fetches.
    allowed = ("youtube.com", "youtu.be", "instagram.com", "tiktok.com", "reddit.com", "x.com", "twitter.com", "vimeo.com", "facebook.com")
    if not any(host == d or host.endswith("." + d) for d in allowed):
        raise HTTPException(400, "Unsupported platform")
    return value

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/resolve")
def resolve(req: VideoRequest):
    url = validate_url(req.url)
    options = {"quiet": True, "no_warnings": True, "noplaylist": True, "skip_download": True, "socket_timeout": 12, "retries": 1, "extract_flat": False, "format": "best[ext=mp4]/best", "ignore_no_formats_error": False}
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info or info.get("_type") in ("playlist", "url", "url_transparent"):
                raise HTTPException(422, "No single public video found")
            media = info.get("url")
            if not media or not media.startswith("https://"):
                raise HTTPException(422, "No downloadable HTTPS video format found")
            return {"title": str(info.get("title") or "video")[:180], "thumbnail": info.get("thumbnail"), "download_url": media, "ext": info.get("ext") or "mp4", "note": "Temporary direct media URL; availability depends on the platform"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(422, "Could not resolve this video. It may be private, protected, unavailable, or blocked by the platform.")

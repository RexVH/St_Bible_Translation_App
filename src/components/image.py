from pathlib import Path
import base64
import mimetypes
import html

def banner_with_overlay(
    image_ref: str,
    title: str,
    subtitle: str | None = None,
    banner_height_px: int = 260,
):
    """
    image_ref: URL (preferred) or local file path.
    """
    # Decide whether we're dealing with a URL or a local path
    is_url = image_ref.startswith("http://") or image_ref.startswith("https://")

    if is_url:
        img_src = html.escape(image_ref, quote=True)
    else:
        p = Path(image_ref)
        img_bytes = p.read_bytes()
        mime, _ = mimetypes.guess_type(str(p))
        mime = mime or "image/png"
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        img_src = f"data:{mime};base64,{b64}"

    safe_title = html.escape(title or "")
    safe_sub = html.escape(subtitle or "") if subtitle else ""
    sub_html = f"<div class='overlay-subtitle'>{safe_sub}</div>" if subtitle else ""

    return f"""
        <style>
        .banner {{
            position: relative;
            width: 100%;
            height: {banner_height_px}px;
            overflow: hidden;
            border-radius: 14px;
        }}
        .banner img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display:block;
        }}
        .overlay {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 18px 24px;
            background: linear-gradient(
                to top,
                rgba(0,0,0,0.70),
                rgba(0,0,0,0.25),
                rgba(0,0,0,0)
            );
            color: white;
        }}
        .overlay-title {{
            font-size: 1.6rem;
            font-weight: 700;
            line-height: 1.2;
        }}
        .overlay-subtitle {{
            font-size: 1.05rem;
            opacity: 0.9;
            margin-top: 6px;
        }}
        </style>

        <div class="banner">
            <a href="{img_src}" target="_blank" title="Open full image">
                <img src="{img_src}" />
            </a>
            <div class="overlay">
                <div class="overlay-title">{safe_title}</div>
                {sub_html}
            </div>
        </div>
        """.strip()

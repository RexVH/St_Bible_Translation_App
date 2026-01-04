# app/components/audio.py
from __future__ import annotations

import html
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components
from i18n import t

ALLOWED_SPEEDS = [0.75, 0.80, 0.90, 1.0, 1.25, 1.5]

def render_audio_player(
  *,
    audio_url: Optional[str],
    speed_key: str = "audio_speed",
    label: str = "Audio",
    speed_label: str = "Speed",
    download_label: str = "Download MP3",
) -> None:
    """
    Renders an HTML5 audio player with playback speed controls.

    Notes:
    - Avoids using key= on components.html for compatibility with older Streamlit versions.
    - Uses a unique <audio> id derived from active_* state so reruns don't clash.
    - Applies playbackRate on loadedmetadata/canplay (no setTimeout).
    """
    if not audio_url:
        st.info("No audio available for this chapter.")
        return

    # Ensure speed exists and is valid
    if speed_key not in st.session_state:
      st.session_state[speed_key] = 1.0
    if float(st.session_state[speed_key]) not in ALLOWED_SPEEDS:
      st.session_state[speed_key] = 1.0

    c1, c2, c3 = st.columns([1, 3, 1])

    with c1:
        st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
        # Speed picker (Streamlit state)
        idx = ALLOWED_SPEEDS.index(float(st.session_state[speed_key]))
        new_speed = st.selectbox(
            speed_label,
            ALLOWED_SPEEDS,
            index=idx,
            key=f"_{speed_key}_select",
        )
        if float(new_speed) != float(st.session_state[speed_key]):
            st.session_state[speed_key] = float(new_speed)
    
    with c2:
      st.caption(t(st.session_state, "audio_speed"))

      safe_url = html.escape(audio_url, quote=True)
      speed = float(st.session_state[speed_key])

      # Unique audio element id per active context (prevents collisions on reruns)
      ss = st.session_state
      bible_id = ss.get("active_bible_id", "na")
      level = ss.get("active_level", "na")
      book_id = ss.get("active_book_id", "na")
      chapter = ss.get("active_chapter", "na")

      # Keep id DOM-safe
      audio_id = f"audio_{bible_id}_{level}_{book_id}_{chapter}"
      audio_id = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in str(audio_id))

      html_block = f"""
      <div style="width: 100%;">
        <audio id="{audio_id}" controls style="width: 100%;" preload="metadata">
          <source src="{safe_url}" type="audio/mpeg">
          Your browser does not support the audio element.
        </audio>
      </div>

      <script>
        (function() {{
          const audio = document.getElementById("{audio_id}");
          if (!audio) return;

          const speed = {speed};

          function applySpeed() {{
            try {{
              audio.playbackRate = speed;
            }} catch (e) {{}}
          }}

          applySpeed();
          audio.addEventListener("loadedmetadata", applySpeed);
          audio.addEventListener("canplay", applySpeed);
        }})();
      </script>
      """
      components.html(html_block, height=90)
    
    with c3:
      st.markdown('<div style="height: 56px;"></div>', unsafe_allow_html=True)
      st.link_button(download_label, audio_url)

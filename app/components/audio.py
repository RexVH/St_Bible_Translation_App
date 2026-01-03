# app/components/audio.py
from __future__ import annotations

import html
import streamlit as st
import streamlit.components.v1 as components
from typing import Optional


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
    - Uses st.session_state[speed_key] to store speed.
    - Provides a Streamlit-native selectbox for speed (reliable state).
    - Embeds audio player via HTML so playbackRate can be applied.
    """
    if not audio_url:
        st.info("No audio available for this chapter.")
        return

    # Ensure speed exists and is valid
    if speed_key not in st.session_state:
        st.session_state[speed_key] = 1.0
    if float(st.session_state[speed_key]) not in ALLOWED_SPEEDS:
        st.session_state[speed_key] = 1.0

    c1, c2 = st.columns([3, 1])

    with c2:
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

        # Download link
        st.link_button(download_label, audio_url)

    with c1:
        st.caption(label)

        # HTML audio component with JS to set playbackRate
        # Note: escaping URL for safety
        safe_url = html.escape(audio_url, quote=True)
        speed = float(st.session_state[speed_key])

        html_block = f"""
        <div style="width: 100%;">
          <audio id="audio_player" controls style="width: 100%;">
            <source src="{safe_url}" type="audio/mpeg">
            Your browser does not support the audio element.
          </audio>
        </div>
        <script>
          (function() {{
            const audio = document.getElementById("audio_player");
            if (!audio) return;

            // Apply speed now
            audio.playbackRate = {speed};

            // Re-apply speed whenever metadata is loaded (some browsers reset)
            audio.addEventListener("loadedmetadata", () => {{
              audio.playbackRate = {speed};
            }});

            // Re-apply speed if the element is re-rendered
            setTimeout(() => {{
              audio.playbackRate = {speed};
            }}, 50);
          }})();
        </script>
        """
        components.html(html_block, height=85)

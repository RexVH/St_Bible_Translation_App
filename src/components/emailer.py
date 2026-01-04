from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, Optional

import streamlit as st


def _get_secret(name: str) -> Optional[str]:
    try:
        v = st.secrets.get(name)  # type: ignore[attr-defined]
        if v is None:
            return None
        v = str(v).strip()
        return v or None
    except Exception:
        return None


def _send_sendgrid_email(
    api_key: str,
    to_email: str,
    from_email: str,
    subject: str,
    body: str,
) -> None:
    """
    Sends an email via SendGrid v3 API using only stdlib (no extra dependency).
    Requires:
      - SENDGRID_API_KEY
      - FEEDBACK_TO_EMAIL
      - FEEDBACK_FROM_EMAIL  (must be a verified sender in SendGrid)
    """
    url = "https://api.sendgrid.com/v3/mail/send"
    payload: Dict[str, Any] = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}],
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            # SendGrid returns 202 Accepted on success
            status = getattr(resp, "status", None)
            if status not in (200, 202):
                raise RuntimeError(f"SendGrid returned unexpected status: {status}")
    except urllib.error.HTTPError as e:
        # Include response body if possible
        try:
            detail = e.read().decode("utf-8", errors="replace")
        except Exception:
            detail = ""
        raise RuntimeError(f"SendGrid HTTPError: {e.code} {e.reason} {detail}") from e


def send_feedback_email(subject: str, body: str) -> None:
    """
    Provider wrapper used by the feedback component.
    Configure via Streamlit secrets:

    Required (SendGrid):
      SENDGRID_API_KEY
      FEEDBACK_TO_EMAIL
      FEEDBACK_FROM_EMAIL

    Optional:
      FEEDBACK_SUBJECT_PREFIX  (e.g., "[Bible App]")
      EMAIL_PROVIDER           (defaults to "sendgrid")
    """
    provider = (_get_secret("EMAIL_PROVIDER") or "sendgrid").lower()

    subject_prefix = _get_secret("FEEDBACK_SUBJECT_PREFIX")
    if subject_prefix:
        subject = f"{subject_prefix.strip()} {subject}".strip()

    if provider == "sendgrid":
        api_key = _get_secret("SENDGRID_API_KEY")
        to_email = _get_secret("FEEDBACK_TO_EMAIL")
        from_email = _get_secret("FEEDBACK_FROM_EMAIL")

        missing = [k for k, v in {
            "SENDGRID_API_KEY": api_key,
            "FEEDBACK_TO_EMAIL": to_email,
            "FEEDBACK_FROM_EMAIL": from_email,
        }.items() if not v]

        if missing:
            raise RuntimeError(
                "Missing Streamlit secrets: " + ", ".join(missing) + ". "
                "Set these in Streamlit Community Cloud → App → Settings → Secrets."
            )

        _send_sendgrid_email(
            api_key=api_key,          # type: ignore[arg-type]
            to_email=to_email,        # type: ignore[arg-type]
            from_email=from_email,    # type: ignore[arg-type]
            subject=subject,
            body=body,
        )
        return

    raise RuntimeError(
        f"Unsupported EMAIL_PROVIDER='{provider}'. "
        "Currently supported: sendgrid."
    )

"""Shared branded HTML shell for customer-facing Locally Twisted email."""
from __future__ import annotations

from pathlib import Path

import frappe
from frappe.utils import escape_html


AUTO_ACK_SUBJECT = "🎈Locally Twisted🎈 We Got Your Message! Be in Touch Soon!"
LOGO_EMBED_NAME = "lt-logo.png"
DOG_EMBED_NAME = "lt-balloon-dog-red-email-mirrored.png"
GENERAL_INBOX = "hi@locallytwisted.com"
BILLING_INBOX = "billing@locallytwisted.com"
PHONE_DISPLAY = "(801) 285-0860"
SITE_URL = "https://locallytwisted.com"


def render_customer_email(
    *,
    title: str,
    preheader: str,
    body_html: str,
    support_email: str = GENERAL_INBOX,
) -> str:
    """Return compact email-safe HTML with the LT logo and approved palette."""
    safe_title = escape_html(title)
    safe_preheader = escape_html(preheader)
    safe_support_email = escape_html(support_email)
    return f"""
<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;line-height:1px;font-size:1px;">
  {safe_preheader}
</div>
<div style="width:100%;margin:0;padding:0;background:#FAF7F2;font-family:Lato,Helvetica,Arial,sans-serif;color:#0A0A0B;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;background:#FAF7F2;">
    <tr>
      <td align="center" style="padding:0 10px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;border-collapse:collapse;background:#FFFFFF;border:1px solid #E7E5E1;border-top:5px solid #0E2240;">
          <tr>
            <td style="padding:14px 18px 8px;text-align:left;">
              <a href="{SITE_URL}" style="text-decoration:none;border:0;">
                <img embed="{LOGO_EMBED_NAME}" width="220" alt="Locally Twisted" style="display:block;width:220px;max-width:80%;height:auto;border:0;outline:none;text-decoration:none;">
              </a>
            </td>
          </tr>
          <tr>
            <td style="padding:0 18px 12px;border-bottom:2px solid #B89A5B;">
              <h1 style="font-family:Georgia,'Times New Roman',serif;font-size:22px;line-height:1.2;color:#0E2240;margin:0 0 6px;font-weight:700;border-left:4px solid #B31B34;padding-left:10px;">
                {safe_title}
              </h1>
              <p style="font-size:13px;line-height:1.45;color:#595A5C;margin:0;">
                {safe_preheader}
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:16px 18px 12px;font-size:14px;line-height:1.55;color:#30343A;word-break:break-word;">
              {body_html}
            </td>
          </tr>
          <tr>
            <td style="padding:8px 18px;background:#0E2240;color:#FAF7F2;font-size:12px;line-height:1.45;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;">
                <tr>
                  <td valign="middle" style="color:#FAF7F2;font-size:12px;line-height:1.45;">
                    <strong style="color:#FFFFFF;">Locally Twisted</strong><br>
                    <a href="mailto:{safe_support_email}" style="color:#FAF7F2;text-decoration:underline;">{safe_support_email}</a>
                    <span style="color:#B89A5B;"> | </span>{PHONE_DISPLAY}
                    <span style="color:#B89A5B;"> | </span>West Jordan, Utah
                  </td>
                  <td valign="bottom" align="right" width="70" style="width:70px;text-align:right;">
                    <img embed="{DOG_EMBED_NAME}" width="52" alt="Locally Twisted balloon dog" style="display:block;width:52px;max-width:52px;height:auto;margin:0 0 0 auto;border:0;outline:none;text-decoration:none;">
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</div>
""".strip()


def customer_email_inline_images() -> list[dict[str, object]]:
    """Return inline logo image data so customer emails do not depend on remote loading."""
    icons_path = Path(frappe.get_app_path("locally_twisted")) / "public" / "icons"
    return [
        {"filename": LOGO_EMBED_NAME, "filecontent": (icons_path / LOGO_EMBED_NAME).read_bytes()},
        {"filename": DOG_EMBED_NAME, "filecontent": (icons_path / DOG_EMBED_NAME).read_bytes()},
    ]

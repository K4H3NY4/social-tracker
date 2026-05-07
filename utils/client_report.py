# utils/client_report.py
import io
import math
import os
import base64
import smtplib
from datetime import datetime
from email.utils import formatdate, make_msgid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from sqlalchemy import select

from db.session import SessionLocal
from models.client import Client
from models.facebook import FacebookPost
from models.instagram import InstagramPost
from models.tiktok import TikTokVideo
from utils.social_analysis import (
    analyze_caption_themes,
    analyze_contract_compliance,
    count_collaborative_posts,
    count_facebook_content,
    count_instagram_content_types,
    count_tiktok_content
)


def get_matplotlib_pyplot():
    try:
        import matplotlib
        matplotlib.use('Agg')  # Headless rendering for servers
        import matplotlib.pyplot as plt
        return plt
    except ImportError as exc:
        raise RuntimeError(
            "Report charts require matplotlib. Install project dependencies before generating reports."
        ) from exc


def get_weasyprint_html():
    try:
        from weasyprint import HTML
        return HTML
    except (ImportError, OSError) as exc:
        raise RuntimeError(
            "PDF reports require WeasyPrint and its system libraries, including Pango. "
            "Install the project and WeasyPrint OS dependencies before generating PDF reports."
        ) from exc

# ──────────────────────────────────────────────────────────────────────
# 📥 DATA FETCHING HELPERS
# ──────────────────────────────────────────────────────────────────────

def fetch_platform_posts(db, platform: str, username: str, start: str = None, end: str = None):
    """Fetch posts for a given platform & username, returns (posts_list, posts_data, stats)"""
    if platform == 'facebook':
        stmt = select(FacebookPost).where(FacebookPost.user_username_raw == username)
        if start:
            stmt = stmt.where(FacebookPost.date_posted >= datetime.strptime(start, '%Y-%m-%d'))
        if end:
            end_dt = datetime.strptime(end, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            stmt = stmt.where(FacebookPost.date_posted <= end_dt)
        
        posts = db.execute(stmt.order_by(FacebookPost.date_posted.desc())).scalars().all()
        posts_data = [p.to_dict() for p in posts]
        stats = count_facebook_content(posts_data)
        return posts, posts_data, stats

    elif platform == 'instagram':
        stmt = select(InstagramPost).where(
            (InstagramPost.user_posted == username) | 
            (InstagramPost.coauthor_producers.like(f'%{username}%'))
        )
        if start:
            stmt = stmt.where(InstagramPost.date_posted >= datetime.strptime(start, '%Y-%m-%d'))
        if end:
            end_dt = datetime.strptime(end, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            stmt = stmt.where(InstagramPost.date_posted <= end_dt)
        
        posts = db.execute(stmt.order_by(InstagramPost.date_posted.desc())).scalars().all()
        posts_data = []
        for p in posts:
            posts_data.append({
                'id': p.id, 'content_id': p.content_id, 'description': p.description,
                'date_posted': p.date_posted.isoformat() if p.date_posted else None,
                'content_type': p.content_type, 'user_posted': p.user_posted,
                'coauthor_producers': p.coauthor_producers, 'like_count': p.like_count, 'comment_count': p.comment_count
            })
        stats = count_instagram_content_types(posts_data)
        collab_stats = count_collaborative_posts(posts_data, username)
        return posts, posts_data, stats, collab_stats

    elif platform == 'tiktok':
        stmt = select(TikTokVideo).where(TikTokVideo.author == username)
        if start:
            stmt = stmt.where(TikTokVideo.create_time >= datetime.strptime(start, '%Y-%m-%d'))
        if end:
            end_dt = datetime.strptime(end, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            stmt = stmt.where(TikTokVideo.create_time <= end_dt)
        
        posts = db.execute(stmt.order_by(TikTokVideo.create_time.desc())).scalars().all()
        posts_data = [v.to_dict() for v in posts]
        stats = count_tiktok_content(posts_data)
        return posts, posts_data, stats

    return [], [], {}


def get_platform_compliance_data(db, platform: str, username: str, start: str, end: str, client):
    """Generate compliance analysis for a platform"""
    result = fetch_platform_posts(db, platform, username, start, end)
    
    if platform == 'instagram':
        posts, posts_data, stats, collab_stats = result
        compliance = analyze_contract_compliance(
            contract=client.contract or '',
            posts=posts_data,
            username=username,
            date_range={'start': start, 'end': end},
            platform=platform,
            content_stats=stats,
            collaboration_stats=collab_stats
        )
    else:
        posts, posts_data, stats = result
        compliance = analyze_contract_compliance(
            contract=client.contract or '',
            posts=posts_data,
            username=username,
            date_range={'start': start, 'end': end},
            platform=platform,
            content_stats=stats
        )
    
    # Add engagement metrics
    total_likes = sum(p.get('like_count', 0) or 0 for p in posts_data)
    total_comments = sum(p.get('comment_count', 0) or 0 for p in posts_data)
    
    return {
        'username': username,
        'compliance': compliance,
        'content_stats': stats,
        'total_posts': len(posts_data),
        'total_likes': total_likes,
        'total_comments': total_comments,
        'collaboration_stats': collab_stats if platform == 'instagram' else None
    }


def get_platform_themes_data(db, platform: str, username: str, start: str, end: str):
    """Generate caption theme analysis for a platform"""
    result = fetch_platform_posts(db, platform, username, start, end)
    posts = result[0]
    
    if platform == 'facebook':
        caption_records = [{'id': p.id, 'caption': p.content, 'date': p.date_posted.isoformat() if p.date_posted else None, 'type': p.post_type} for p in posts if p.content and p.content.strip()]
    elif platform == 'instagram':
        caption_records = [{'id': p.id, 'caption': p.description, 'date': p.date_posted.isoformat() if p.date_posted else None, 'type': p.content_type} for p in posts if p.description and p.description.strip()]
    else:  # tiktok
        caption_records = [{'id': v.id, 'caption': v.description, 'date': v.create_time.isoformat() if v.create_time else None, 'type': v.post_type} for v in posts if v.description and v.description.strip()]
    
    themes = analyze_caption_themes(caption_records, platform, username, {'start': start, 'end': end})
    return {'themes': themes, 'captions_analyzed': len(caption_records)}


# ──────────────────────────────────────────────────────────────────────
# 📊 CHART GENERATION
# ──────────────────────────────────────────────────────────────────────

def create_platform_charts(compliance_data: dict, themes_data: dict, platform: str) -> dict:
    """Generate base64 charts for compliance & themes"""
    plt = get_matplotlib_pyplot()
    charts = {}

    def encode_figure(fig):
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return encoded

    def no_data_chart(title: str, message: str) -> str:
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.axis('off')
        ax.text(0.5, 0.58, title, ha='center', va='center', fontsize=11, fontweight='bold')
        ax.text(0.5, 0.42, message, ha='center', va='center', fontsize=9, color='#7f8c8d')
        return encode_figure(fig)
    
    # 1. Content Breakdown Pie Chart
    stats = compliance_data['content_stats']
    if platform == 'instagram':
        labels = ['Carousel', 'Image', 'Video']
        values = [stats.get('carousel',0), stats.get('image',0), stats.get('video',0)]
        colors = ['#3498db', '#2ecc71', '#e74c3c']
    elif platform == 'tiktok':
        labels = ['Videos', 'Images']
        values = [stats.get('videos',0), stats.get('images',0)]
        colors = ['#9b59b6', '#f39c12']
    else:
        labels = ['Posts', 'Videos']
        values = [stats.get('posts',0), stats.get('videos',0)]
        colors = ['#1abc9c', '#e67e22']

    def chart_value(value) -> int:
        try:
            number = float(value or 0)
        except (TypeError, ValueError):
            return 0
        if not math.isfinite(number) or number < 0:
            return 0
        return int(number)

    values = [chart_value(value) for value in values]
    if sum(values) > 0:
        fig, ax = plt.subplots(figsize=(4,4))
        ax.pie(values, labels=labels, autopct='%1.0f%%', startangle=90, colors=colors, textprops={'fontsize':8})
        ax.set_title(f'{platform.title()} Content Types', fontsize=10, pad=10)
        charts['content_breakdown'] = encode_figure(fig)
    else:
        charts['content_breakdown'] = no_data_chart(f'{platform.title()} Content Types', 'No posts found in this date range')
    
    # 2. Top Themes Bar Chart
    themes = themes_data['themes'].get('themes', [])[:5]
    theme_names = [t.get('theme') or 'Untitled' for t in themes]
    theme_counts = [chart_value(t.get('post_count')) for t in themes]
    if themes and sum(theme_counts) > 0:
        fig, ax = plt.subplots(figsize=(5,3))
        bars = ax.barh(theme_names[::-1], theme_counts[::-1], color='#2c3e50', edgecolor='white')
        for bar in bars:
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}', va='center', fontsize=8)
        ax.set_xlabel('Posts', fontsize=8)
        ax.set_title('Top Caption Themes', fontsize=10, pad=8)
        charts['top_themes'] = encode_figure(fig)
    else:
        charts['top_themes'] = no_data_chart('Top Caption Themes', 'No captions available to analyze')
        
    return charts


def get_compliance_analysis(report_data: dict) -> dict:
    compliance = report_data.get('compliance') or {}
    if isinstance(compliance, dict) and isinstance(compliance.get('compliance'), dict):
        return compliance.get('compliance')
    return compliance if isinstance(compliance, dict) else {}


def get_theme_analysis(report_data: dict) -> dict:
    themes = report_data.get('themes') or {}
    if isinstance(themes, dict) and isinstance(themes.get('themes'), dict):
        return themes.get('themes')
    return themes if isinstance(themes, dict) else {}


def safe_attachment_filename(name: str) -> str:
    safe_name = ''.join(char if char.isalnum() or char in ('-', '_') else '_' for char in name)
    safe_name = '_'.join(part for part in safe_name.split('_') if part)
    return safe_name or 'client'


# ──────────────────────────────────────────────────────────────────────
# 📄 PDF GENERATION
# ──────────────────────────────────────────────────────────────────────

def generate_comprehensive_pdf(client, platform_reports: dict, start: str, end: str) -> bytes:
    """Generate unified multi-platform PDF report"""
    HTML = get_weasyprint_html()
    
    html_parts = []
    
    # Header
    html_parts.append(f"""
    <div style="background:#2c3e50;color:white;padding:25px;text-align:center;margin-bottom:20px;">
        <h1 style="margin:0;font-size:22pt;">📊 Comprehensive Social Media Report</h1>
        <p style="margin:8px 0 0 0;font-size:13pt;">{client.name}</p>
        <p style="margin:4px 0 0 0;font-size:10pt;opacity:0.9;">Reporting Period: {start or 'N/A'} to {end or 'N/A'}</p>
    </div>
    """)
    
    for platform, data in platform_reports.items():
        comp = get_compliance_analysis(data)
        themes = get_theme_analysis(data)
        stats = data['content_stats']
        charts = data.get('charts', {})
        username = data['username']
        
        status = comp.get('compliance_status', 'unknown')
        status_class = {'fully_compliant':'#27ae60','partially_compliant':'#f39c12','non_compliant':'#e74c3c'}.get(status,'#95a5a6')
        status_text = status.replace('_',' ').title()
        
        html_parts.append(f"""
        <div style="page-break-before:always;padding:10px 0;">
            <h2 style="color:#2c3e50;border-bottom:2px solid #3498db;padding-bottom:6px;margin-top:0;">
                📱 {platform.title()} • @{username}
            </h2>
            
            <div style="display:flex;gap:15px;margin:15px 0;">
                <div style="flex:1;background:#f8f9fa;padding:12px;border-left:4px solid #3498db;text-align:center;">
                    <div style="font-size:20pt;font-weight:bold;color:#2980b9;">{comp.get('compliance_score','N/A')}</div>
                    <div style="font-size:8pt;color:#7f8c8d;text-transform:uppercase;">Compliance Score</div>
                </div>
                <div style="flex:1;background:#f8f9fa;padding:12px;border-left:4px solid #27ae60;text-align:center;">
                    <div style="font-size:20pt;font-weight:bold;color:#27ae60;">{data['total_posts']}</div>
                    <div style="font-size:8pt;color:#7f8c8d;text-transform:uppercase;">Posts Delivered</div>
                </div>
                <div style="flex:1;background:#f8f9fa;padding:12px;border-left:4px solid #e74c3c;text-align:center;">
                    <div style="font-size:20pt;font-weight:bold;color:#e74c3c;">{data['captions_analyzed']}</div>
                    <div style="font-size:8pt;color:#7f8c8d;text-transform:uppercase;">Captions Analyzed</div>
                </div>
            </div>
            
            <div style="display:inline-block;background:{status_class};color:white;padding:6px 14px;border-radius:16px;font-size:9pt;font-weight:bold;margin-bottom:15px;">
                {status_text}
            </div>
            
            <h3 style="font-size:12pt;color:#2c3e50;margin:15px 0 8px 0;">📈 Content & Compliance</h3>
            <div style="text-align:center;margin:10px 0;">
                <img src="data:image/png;base64,{charts.get('content_breakdown','')}" style="max-width:45%;height:auto;border:1px solid #ddd;border-radius:4px;" alt="Content Types">
            </div>
            <div style="background:#f8f9fa;padding:12px;border-radius:4px;font-size:10pt;margin:10px 0;">
                <strong>Analysis:</strong> {comp.get('analysis','No analysis available.')}
            </div>
            
            <h3 style="font-size:12pt;color:#2c3e50;margin:20px 0 8px 0;">🎯 Caption Themes</h3>
            <div style="display:flex;gap:20px;align-items:center;">
                <div style="flex:1;text-align:center;">
                    <img src="data:image/png;base64,{charts.get('top_themes','')}" style="max-width:90%;height:auto;border:1px solid #ddd;border-radius:4px;" alt="Themes">
                </div>
                <div style="flex:1.5;font-size:10pt;">
                    <strong>Top Topics:</strong>
                    <ul style="padding-left:18px;margin:6px 0;">
        """)
        
        for topic in themes.get('topics', [])[:4]:
            if not isinstance(topic, dict):
                continue
            topic_name = topic.get('topic') or 'Untitled'
            what_was_said = topic.get('what_was_said') or topic.get('description') or 'No detail available.'
            html_parts.append(f'<li><b>{topic_name}</b>: {what_was_said}</li>')
            
        html_parts.append(f"""
                    </ul>
                    <strong>Top Hashtags:</strong>
                    <p style="margin:4px 0;">{', '.join([f'#{h.get("tag")}' for h in themes.get('hashtags', [])[:6] if isinstance(h, dict) and h.get("tag")]) or 'None'}</p>
                </div>
            </div>
        </div>
        """)
    
    # Footer
    html_parts.append(f"""
    <div style="margin-top:30px;padding-top:15px;border-top:1px solid #ddd;font-size:8pt;color:#7f8c8d;text-align:center;">
        Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} • Confidential • Prepared by crAIg By Creative Edge
    </div>
    """)
    
    full_html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; font-size: 10pt; line-height: 1.4; color: #2c3e50; margin: 0; padding: 20px; }}
        h1,h2,h3 {{ margin: 10px 0 5px 0; }}
        ul {{ margin: 5px 0; padding-left: 18px; }}
        li {{ margin-bottom: 4px; }}
        @page {{ size: A4; margin: 15mm; }}
    </style>
    </head><body>{"".join(html_parts)}</body></html>
    """
    
    return HTML(string=full_html).write_pdf()


# ──────────────────────────────────────────────────────────────────────
# 📧 EMAIL DELIVERY
# ──────────────────────────────────────────────────────────────────────

def _send_client_report_email_legacy(to_email: str, client, platform_reports: dict, pdf_bytes: bytes = None):
    """Send comprehensive report via email"""
    msg = MIMEMultipart()
    msg['Subject'] = f"Compliance & Content Report • {client.name}"
    msg['From'] = os.getenv('EMAIL_FROM', os.getenv('SMTP_USERNAME'))
    msg['To'] = to_email
    
    # Build summary HTML
    summary_html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;color:#333;">
        <h2 style="color:#2c3e50;">📊 Report Ready: {client.name}</h2>
        <p>Attached is your comprehensive social media compliance & content analysis report.</p>
        <table style="width:100%;border-collapse:collapse;margin:15px 0;">
            <tr style="background:#f8f9fa;">
                <th style="padding:8px;text-align:left;border-bottom:1px solid #ddd;">Platform</th>
                <th style="padding:8px;text-align:left;border-bottom:1px solid #ddd;">Username</th>
                <th style="padding:8px;text-align:left;border-bottom:1px solid #ddd;">Score</th>
                <th style="padding:8px;text-align:left;border-bottom:1px solid #ddd;">Posts</th>
            </tr>
    """
    for plat, data in platform_reports.items():
        score = get_compliance_analysis(data).get('compliance_score', '-')
        summary_html += f"""
            <tr>
                <td style="padding:6px;border-bottom:1px solid #eee;">{plat.title()}</td>
                <td style="padding:6px;border-bottom:1px solid #eee;">@{data['username']}</td>
                <td style="padding:6px;border-bottom:1px solid #eee;font-weight:bold;">{score}/100</td>
                <td style="padding:6px;border-bottom:1px solid #eee;">{data['total_posts']}</td>
            </tr>
        """
    summary_html += """</table>
        <p style="font-size:10pt;color:#7f8c8d;">Open the attached PDF for full analysis, charts, and AI recommendations.</p>
    </div>"""
    
    msg.attach(MIMEText(summary_html, 'html'))
    
    if pdf_bytes:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=f'{client.name.replace(" ","_")}_Report.pdf')
        msg.attach(part)
        
    with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT',587))) as server:
        server.starttls()
        server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
        server.send_message(msg)


def send_client_report_email(to_email: str, client, platform_reports: dict, pdf_bytes: bytes = None):
    """Send a client report email with provider-friendly headers and body."""
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('EMAIL_FROM') or smtp_username

    if not smtp_server or not from_email:
        raise RuntimeError('SMTP_SERVER and EMAIL_FROM or SMTP_USERNAME are required to send reports.')

    domain = from_email.split('@')[-1] if '@' in from_email else None
    msg = MIMEMultipart('mixed')
    msg['Subject'] = f"Social Media Compliance Report - {client.name}"
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = make_msgid(domain=domain)
    msg['X-Mailer'] = 'Post Tracker Reports'

    rows = []
    plain_lines = [
        f"Social Media Compliance Report - {client.name}",
        "",
        "Summary"
    ]
    for platform, data in platform_reports.items():
        score = get_compliance_analysis(data).get('compliance_score', '-')
        username = data.get('username', '')
        total_posts = data.get('total_posts', 0)
        rows.append((platform.title(), username, score, total_posts))
        plain_lines.append(f"- {platform.title()} @{username}: score {score}/100, posts {total_posts}")

    if pdf_bytes:
        plain_lines.extend(["", "The PDF report is attached."])
    plain_lines.extend(["", "Regards,", "Post Tracker Reports"])
    plain_text = "\n".join(plain_lines)

    summary_html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;color:#333;">
        <h2 style="color:#2c3e50;">Social Media Compliance Report</h2>
        <p>The report for <strong>{client.name}</strong> is ready.</p>
        <table style="width:100%;border-collapse:collapse;margin:15px 0;">
            <tr style="background:#f8f9fa;">
                <th style="padding:8px;text-align:left;border-bottom:1px solid #ddd;">Platform</th>
                <th style="padding:8px;text-align:left;border-bottom:1px solid #ddd;">Username</th>
                <th style="padding:8px;text-align:left;border-bottom:1px solid #ddd;">Score</th>
                <th style="padding:8px;text-align:left;border-bottom:1px solid #ddd;">Posts</th>
            </tr>
    """
    for platform_name, username, score, total_posts in rows:
        summary_html += f"""
            <tr>
                <td style="padding:6px;border-bottom:1px solid #eee;">{platform_name}</td>
                <td style="padding:6px;border-bottom:1px solid #eee;">@{username}</td>
                <td style="padding:6px;border-bottom:1px solid #eee;font-weight:bold;">{score}/100</td>
                <td style="padding:6px;border-bottom:1px solid #eee;">{total_posts}</td>
            </tr>
        """
    summary_html += """</table>
        <p style="font-size:10pt;color:#7f8c8d;">The PDF report is attached when requested.</p>
    </div>"""

    alternative = MIMEMultipart('alternative')
    alternative.attach(MIMEText(plain_text, 'plain', 'utf-8'))
    alternative.attach(MIMEText(summary_html, 'html', 'utf-8'))
    msg.attach(alternative)

    if pdf_bytes:
        filename = f'{safe_attachment_filename(client.name)}_Report.pdf'
        part = MIMEBase('application', 'pdf')
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            if smtp_port == 587:
                server.starttls()
                server.ehlo()
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            server.send_message(msg)
    except smtplib.SMTPDataError as exc:
        detail = exc.smtp_error.decode('utf-8', errors='replace') if isinstance(exc.smtp_error, bytes) else str(exc.smtp_error)
        raise RuntimeError(
            f"SMTP provider rejected the report email ({exc.smtp_code}): {detail}. "
            "Try sending without a PDF attachment, use a sender address authenticated for this domain, "
            "and confirm SPF, DKIM, and DMARC are configured for the SMTP account."
        ) from exc
    except (smtplib.SMTPException, OSError) as exc:
        raise RuntimeError(f"SMTP send failed: {exc}") from exc



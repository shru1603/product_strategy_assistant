import re
from datetime import datetime


def _parse_markdown(text: str, styles: dict) -> list:
    """Convert markdown text into ReportLab flowables."""
    from reportlab.platypus import Paragraph, Spacer, HRFlowable
    from reportlab.lib import colors

    flowables = []
    lines = text.split('\n')

    for line in lines:
        stripped = line.strip()

        if not stripped:
            flowables.append(Spacer(1, 6))
            continue

        # h1: # Heading
        if re.match(r'^#\s', line) and not re.match(r'^##', line):
            content = re.sub(r'^#\s*', '', line)
            content = _inline_md(content)
            flowables.append(Paragraph(content, styles['h1']))
            flowables.append(HRFlowable(width='100%', color=colors.HexColor('#DDE3EA'), thickness=1))
            flowables.append(Spacer(1, 4))
            continue

        # h2: ## Heading
        if re.match(r'^##\s', line) and not re.match(r'^###', line):
            content = re.sub(r'^##\s*', '', line)
            content = _inline_md(content)
            flowables.append(Spacer(1, 8))
            flowables.append(Paragraph(content, styles['h2']))
            flowables.append(Spacer(1, 3))
            continue

        # h3: ### Heading
        if re.match(r'^###', line):
            content = re.sub(r'^###\s*', '', line)
            content = _inline_md(content)
            flowables.append(Spacer(1, 6))
            flowables.append(Paragraph(content, styles['h3']))
            flowables.append(Spacer(1, 2))
            continue

        # bold-only label: **Label:**
        if re.match(r'^\*\*[^*]+\*\*:?\s*$', stripped):
            content = stripped.replace('**', '').rstrip(':') + ':'
            flowables.append(Spacer(1, 6))
            flowables.append(Paragraph(f'<font color="#1565C0"><b>{content}</b></font>', styles['body']))
            continue

        # bullet
        if re.match(r'^[-*+]\s', line):
            content = _inline_md(re.sub(r'^[-*+]\s', '', line))
            flowables.append(Paragraph(f'<font color="#1565C0">•</font>  {content}', styles['bullet']))
            continue

        # numbered list
        if re.match(r'^\d+[\).]\s', line):
            num = re.match(r'^(\d+)', line).group(1)
            content = _inline_md(re.sub(r'^\d+[\).]\s', '', line))
            flowables.append(Paragraph(f'<font color="#1565C0"><b>{num}.</b></font>  {content}', styles['bullet']))
            continue

        # horizontal rule
        if re.match(r'^(-{3,}|_{3,})$', stripped):
            flowables.append(HRFlowable(width='100%', color=colors.HexColor('#DDE3EA'), thickness=0.5))
            continue

        # plain paragraph
        flowables.append(Paragraph(_inline_md(line), styles['body']))

    return flowables


def _inline_md(text: str) -> str:
    """Convert inline markdown (**bold**, *italic*) to ReportLab XML tags."""
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', text)
    text = re.sub(r'`(.+?)`',       r'<font face="Courier" fontSize="9">\1</font>', text)
    return text


def generate_report_pdf(report_data: dict, output_path: str) -> str:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer,
            Table, TableStyle, HRFlowable, PageBreak,
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            rightMargin=2 * cm, leftMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
        )

        base = getSampleStyleSheet()
        BLUE  = colors.HexColor('#1565C0')
        DARK  = colors.HexColor('#1a2533')
        SLATE = colors.HexColor('#2D3A4A')

        pdf_styles = {
            'h1': ParagraphStyle('h1', parent=base['Normal'],
                fontSize=15, fontName='Helvetica-Bold', textColor=DARK,
                spaceBefore=16, spaceAfter=4),
            'h2': ParagraphStyle('h2', parent=base['Normal'],
                fontSize=13, fontName='Helvetica-Bold', textColor=BLUE,
                spaceBefore=12, spaceAfter=3),
            'h3': ParagraphStyle('h3', parent=base['Normal'],
                fontSize=11, fontName='Helvetica-Bold', textColor=SLATE,
                spaceBefore=8, spaceAfter=2),
            'body': ParagraphStyle('body', parent=base['Normal'],
                fontSize=10, leading=16, spaceAfter=3, textColor=colors.HexColor('#263238')),
            'bullet': ParagraphStyle('bullet', parent=base['Normal'],
                fontSize=10, leading=15, leftIndent=12, spaceAfter=3,
                textColor=colors.HexColor('#263238')),
        }

        title_style = ParagraphStyle('T', parent=base['Title'],
            fontSize=26, textColor=BLUE, alignment=TA_CENTER, spaceAfter=6)
        sub_style = ParagraphStyle('S', parent=base['Normal'],
            fontSize=11, textColor=colors.HexColor('#546E7A'), alignment=TA_CENTER)
        section_style = ParagraphStyle('SEC', parent=base['Heading1'],
            fontSize=14, textColor=BLUE, spaceBefore=14, spaceAfter=6)

        LB = colors.HexColor('#F5F7FA')

        def sec_header(title):
            return [
                Paragraph(title, section_style),
                HRFlowable(width='100%', color=BLUE, thickness=1.5),
                Spacer(1, 0.3 * cm),
            ]

        raw = report_data.get('raw_data_summary', {})

        story = [
            Spacer(1, 2 * cm),
            Paragraph('AI Product Strategy Report', title_style),
            Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y  %I:%M %p')}", sub_style),
            PageBreak(),
        ]

        # ── Executive Summary ──────────────────────────────────────────
        story += sec_header('Executive Summary')
        rows = [
            ['Total Revenue',     f"${raw.get('total_revenue', 0):,.2f}"],
            ['Total Profit',      f"${raw.get('total_profit', 0):,.2f}"],
            ['Profit Margin',     f"{raw.get('total_profit', 0)/max(raw.get('total_revenue', 1), 1)*100:.1f}%"],
            ['Average Rating',    f"{raw.get('avg_rating', 0):.2f} / 5.0"],
            ['Total Units Sold',  f"{raw.get('total_units', 0):,}"],
            ['Total Returns',     f"{raw.get('total_returns', 0):,}"],
            ['New Customers',     f"{raw.get('total_new_customers', 0):,}"],
            ['Marketing Spend',   f"${raw.get('total_marketing_spend', 0):,.2f}"],
            ['Products',          str(len(raw.get('products', [])))],
            ['Categories',        ', '.join(raw.get('categories', []))],
            ['Regions',           ', '.join(raw.get('regions', []))],
            ['Period',            raw.get('date_range', 'N/A')],
        ]
        t = Table(rows, colWidths=[5.5 * cm, 10.5 * cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (0, -1), LB),
            ('TEXTCOLOR',     (0, 0), (0, -1), BLUE),
            ('FONTNAME',      (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, -1), 10),
            ('PADDING',       (0, 0), (-1, -1), 7),
            ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#DDE3EA')),
            ('ROWBACKGROUNDS',(0, 0), (-1, -1), [colors.white, colors.HexColor('#FAFBFC')]),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story += [t, Spacer(1, 0.5 * cm)]

        # ── Agent sections ─────────────────────────────────────────────
        sections = [
            ('Customer Insights',                    'customer_insights'),
            ('Sales Performance',                    'sales_analysis'),
            ('Market Opportunities',                 'market_opportunities'),
            ('Feature Prioritization (RICE Scores)', 'feature_priorities'),
            ('Strategic Recommendations & SWOT',     'strategy'),
        ]

        for title, key in sections:
            story.append(PageBreak())
            story += sec_header(title)
            data = report_data.get(key, {})
            text = data.get('analysis', 'No analysis available.')
            story += _parse_markdown(text, pdf_styles)
            story.append(Spacer(1, 0.4 * cm))

        doc.build(story)
        return f'PDF generated: {output_path}'

    except ImportError:
        return 'reportlab not installed. Run: pip install reportlab'
    except Exception as exc:
        return f'PDF generation failed: {exc}'

"""
Report Generator Tool - Creates professional PDF reports
"""

from langchain.tools import BaseTool
from typing import Optional, List
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from pathlib import Path
from datetime import datetime
import markdown
import re

class ReportGeneratorTool(BaseTool):
    name: str = "Report Generator Tool"
    description: str = """Generates professional PDF reports from markdown content.
    
    Input format: JSON string with keys:
    - content: report content in markdown format
    - title: report title
    - output_name: output filename (optional)
    
    Example: {"content": "# Report\\n\\nContent here...", "title": "Analysis Report"}"""
    
    def __init__(self):
        super().__init__()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
    
    def _parse_markdown_to_elements(self, content: str) -> List:
        elements = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                elements.append(Spacer(1, 0.2 * inch))
                i += 1
                continue
            
            if line.startswith('# '):
                elements.append(Paragraph(line[2:], self.styles['CustomHeading1']))
            elif line.startswith('## '):
                elements.append(Paragraph(line[3:], self.styles['CustomHeading2']))
            elif line.startswith('### '):
                elements.append(Paragraph(line[4:], self.styles['Heading3']))
            
            elif line.startswith('- ') or line.startswith('* '):
                bullet_items = []
                while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                    bullet_items.append(lines[i].strip()[2:])
                    i += 1
                i -= 1
                
                for item in bullet_items:
                    elements.append(Paragraph(f"• {item}", self.styles['CustomBody']))
            
            elif re.match(r'^\d+\.', line):
                list_items = []
                while i < len(lines) and re.match(r'^\d+\.', lines[i].strip()):
                    list_items.append(re.sub(r'^\d+\.\s*', '', lines[i].strip()))
                    i += 1
                i -= 1
                
                for idx, item in enumerate(list_items, 1):
                    elements.append(Paragraph(f"{idx}. {item}", self.styles['CustomBody']))
            
            elif line.startswith('![') and '](' in line:
                match = re.match(r'!\[.*?\]\((.*?)\)', line)
                if match:
                    img_path = match.group(1)
                    full_path = Path(img_path)
                    if not full_path.is_absolute():
                        full_path = Path('visuals') / img_path
                    
                    if full_path.exists():
                        try:
                            img = Image(str(full_path), width=5*inch, height=3*inch)
                            elements.append(img)
                            elements.append(Spacer(1, 0.2 * inch))
                        except Exception:
                            elements.append(Paragraph(f"[Image: {img_path}]", self.styles['CustomBody']))
            
            elif '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
                table_data = []
                while i < len(lines) and '|' in lines[i]:
                    row = [cell.strip() for cell in lines[i].split('|')[1:-1]]
                    if not all('---' in cell for cell in row):
                        table_data.append(row)
                    i += 1
                i -= 1
                
                if table_data:
                    t = Table(table_data)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    elements.append(t)
                    elements.append(Spacer(1, 0.3 * inch))
            
            else:
                paragraph_lines = [line]
                i += 1
                while i < len(lines) and lines[i].strip() and not any(lines[i].strip().startswith(x) for x in ['#', '-', '*', '![', '|']) and not re.match(r'^\d+\.', lines[i].strip()):
                    paragraph_lines.append(lines[i].strip())
                    i += 1
                i -= 1
                
                paragraph_text = ' '.join(paragraph_lines)
                elements.append(Paragraph(paragraph_text, self.styles['CustomBody']))
            
            i += 1
        
        return elements
    
    def _run(self, report_params: str) -> str:
        try:
            if isinstance(report_params, str):
                try:
                    params = json.loads(report_params)
                except json.JSONDecodeError:
                    params = {"content": report_params, "title": "Analysis Report"}
            else:
                params = report_params
            
            content = params.get('content', '')
            title = params.get('title', 'Analysis Report')
            output_name = params.get('output_name', None)
            
            reports_dir = Path('reports')
            reports_dir.mkdir(exist_ok=True)
            
            if not output_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_name = f"report_{timestamp}.pdf"
            
            if not output_name.endswith('.pdf'):
                output_name += '.pdf'
            
            output_path = reports_dir / output_name
            
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            elements = []
            
            elements.append(Paragraph(title, self.styles['CustomTitle']))
            elements.append(Paragraph(
                f"Generated on {datetime.now().strftime('%B %d, %Y')}",
                self.styles['Subtitle']
            ))
            elements.append(Spacer(1, 0.5 * inch))
            
            elements.extend(self._parse_markdown_to_elements(content))
            
            doc.build(elements)
            
            return f"Report generated successfully: {output_name} in reports/ directory"
            
        except Exception as e:
            return f"Error generating report: {str(e)}"
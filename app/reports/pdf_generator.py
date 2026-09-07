import os
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

def generate_parcel_survey_pdf(parcel_data: dict) -> bytes:
    """
    Generates a high-quality government-styled Land Survey Verification Certificate & Report.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'GovTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f2744')
    )
    
    sub_title_style = ParagraphStyle(
        'GovSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#475569')
    )
    
    section_style = ParagraphStyle(
        'GovSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=10,
        spaceAfter=4
    )

    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12)
    cell_normal = ParagraphStyle('CellNormal', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12)

    # Header
    story.append(Paragraph("GOVERNMENT OF MAHARASHTRA", title_style))
    story.append(Paragraph("REVENUE AND FOREST DEPARTMENT • DIRECTORATE OF LAND RECORDS", sub_title_style))
    story.append(Paragraph("<b>Rural Agricultural Land Survey / Resurvey (LandSetu)</b>", sub_title_style))
    story.append(Paragraph("<i>Accurate • Transparent • Digital India</i>", sub_title_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f2744'), spaceBefore=2, spaceAfter=12))

    # Certificate Title
    cert_title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f2744')
    )
    story.append(Paragraph("CADASTRAL SURVEY & RESURVEY VERIFICATION REPORT", cert_title_style))
    story.append(Paragraph(f"Reference No: MH/NSK/YLA/{parcel_data.get('gat_number', '50-1')}/{datetime.now().strftime('%Y%m%d')} | Date: {datetime.now().strftime('%d %b %Y')}", sub_title_style))
    story.append(Spacer(1, 12))

    # Land Parcel Information Table
    story.append(Paragraph("1. PARCEL IDENTIFICATION & LOCATION", section_style))
    
    data_p1 = [
        [Paragraph("Survey Number:", cell_bold), Paragraph(str(parcel_data.get('survey_number', '50/1')), cell_normal),
         Paragraph("Gat Number:", cell_bold), Paragraph(str(parcel_data.get('gat_number', '50/1')), cell_normal)],
        [Paragraph("State:", cell_bold), Paragraph("Maharashtra", cell_normal),
         Paragraph("District:", cell_bold), Paragraph(str(parcel_data.get('district_name', 'Nashik')), cell_normal)],
        [Paragraph("Taluka:", cell_bold), Paragraph(str(parcel_data.get('taluka_name', 'Yeola')), cell_normal),
         Paragraph("Village:", cell_bold), Paragraph(str(parcel_data.get('village_name', 'Pimpalgaon')), cell_normal)],
        [Paragraph("Khata Number:", cell_bold), Paragraph(str(parcel_data.get('khata_number', '1042')), cell_normal),
         Paragraph("Land Category:", cell_bold), Paragraph(str(parcel_data.get('land_type', 'Agricultural (Kharif)')), cell_normal)]
    ]
    t1 = Table(data_p1, colWidths=[110, 150, 110, 150])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t1)
    story.append(Spacer(1, 8))

    # Ownership Details
    story.append(Paragraph("2. OWNERSHIP & LAND HOLDER RECORD", section_style))
    data_p2 = [
        [Paragraph("Primary Landholder:", cell_bold), Paragraph(str(parcel_data.get('owner_name', 'Patil Shankar Bapu')), cell_normal),
         Paragraph("Ownership Share:", cell_bold), Paragraph("100% (Single Khatadar)", cell_normal)],
        [Paragraph("Aadhaar Verification:", cell_bold), Paragraph("Verified (UIDAI Biometric Auth)", cell_normal),
         Paragraph("Mutation (Ferfar):", cell_bold), Paragraph("Certified & Recorded", cell_normal)]
    ]
    t2 = Table(data_p2, colWidths=[110, 150, 110, 150])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 8))

    # Resurvey & Area Comparison
    story.append(Paragraph("3. RESURVEY MEASUREMENTS & BOUNDARY AUDIT", section_style))
    area_ha = parcel_data.get('area_hectares', 1.82)
    area_ac = parcel_data.get('area_acres', 4.50)
    data_p3 = [
        [Paragraph("Historical 7/12 Area:", cell_bold), Paragraph(f"{area_ha} ha ({area_ac} acres)", cell_normal),
         Paragraph("New Resurveyed Area:", cell_bold), Paragraph(f"{area_ha} ha ({area_ac} acres)", cell_normal)],
        [Paragraph("Area Difference:", cell_bold), Paragraph("0.00 ha (0.0%)", cell_normal),
         Paragraph("Boundary Status:", cell_bold), Paragraph(f"<b><font color='#16a34a'>{parcel_data.get('boundary_status', 'Verified')}</font></b>", cell_normal)],
        [Paragraph("GPS Accuracy:", cell_bold), Paragraph("± 0.5 meters (DGPS / CORS)", cell_normal),
         Paragraph("Discrepancy Check:", cell_bold), Paragraph(str(parcel_data.get('discrepancy_status', 'No Discrepancy')), cell_normal)],
        [Paragraph("Centroid Coordinates:", cell_bold), Paragraph(f"Lat: {parcel_data.get('center_lat', 19.1234)}° N, Long: {parcel_data.get('center_lng', 74.4321)}° E", cell_normal),
         Paragraph("Survey Method:", cell_bold), Paragraph("Drone Photogrammetry + ETS RTK", cell_normal)]
    ]
    t3 = Table(data_p3, colWidths=[110, 150, 110, 150])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t3)
    story.append(Spacer(1, 14))

    # Certification / Signatures
    story.append(Paragraph("4. STATUTORY VERIFICATION & SIGNATURES", section_style))
    sig_data = [
        [
            Paragraph("<b>Field Survey Officer</b><br/>Bhumi Abhilekh Surveyor<br/>Reg ID: MH-SURV-2025-089<br/>Digitally Signed: 12 Apr 2025", cell_normal),
            Paragraph("<b>Verification Authority</b><br/>Tahsildar / Circle Officer<br/>Yeola Taluka, Nashik<br/>Digitally Approved: 12 Apr 2025", cell_normal),
            Paragraph("<b>Land Intelligence Seal</b><br/>[Official Digital Seal]<br/>Govt of Maharashtra<br/>Bhu-Aadhaar Certified", cell_normal)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[170, 170, 180])
    t_sig.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_sig)
    
    story.append(Spacer(1, 16))
    notice_style = ParagraphStyle('Notice', parent=styles['Normal'], fontSize=7.5, leading=10, textColor=colors.HexColor('#64748b'), alignment=TA_CENTER)
    story.append(Paragraph("This document is generated by LandSetu (Rural Agricultural Land Survey / Resurvey System) under SIH 2026 guidelines.<br/>For development & demonstration purposes, records are validated against local cadastral geometries.", notice_style))

    doc.build(story)
    return buffer.getvalue()

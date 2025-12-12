"""
Report generation module for Auto-Report system
Generates PDF reports from cleaned data
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
from datetime import datetime
import os
from typing import Dict, Any
from data_cleaner import DataCleaner


class ReportGenerator:
    """Generate comprehensive PDF reports from cleaned data"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            spaceAfter=6
        ))
    
    def _create_chart(self, data: Dict[str, Any], chart_type: str, filename: str) -> str:
        """
        Create a chart and save it
        Returns: path to saved chart
        """
        plt.figure(figsize=(8, 5))
        
        if chart_type == 'bar':
            plt.bar(data.keys(), data.values(), color='#3498db')
            plt.xticks(rotation=45, ha='right')
        elif chart_type == 'pie':
            plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=90)
        
        plt.tight_layout()
        chart_path = os.path.join(self.output_dir, filename)
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def generate_report(self, cleaner: DataCleaner, output_filename: str = None) -> str:
        """
        Generate a comprehensive PDF report
        Returns: path to generated PDF
        """
        if not output_filename:
            output_filename = f"auto_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Get cleaned data and summary
        if not cleaner.cleaned_data:
            cleaner.clean_all_data()
        summary = cleaner.get_summary_statistics()
        
        # Title
        story.append(Paragraph("跨境电商市场分析报告", self.styles['CustomTitle']))
        story.append(Paragraph(f"Cross-Border E-Commerce Market Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Report info
        report_date = datetime.now().strftime('%Y年%m月%d日')
        story.append(Paragraph(f"报告生成日期 / Report Date: {report_date}", self.styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("一、执行摘要 / Executive Summary", self.styles['CustomHeading']))
        story.append(Paragraph(
            "本报告基于Amazon和TikTok平台的销售数据、产品评论和用户反馈，"
            "对跨境电商市场进行了全面分析。报告涵盖了销售表现、产品评价、用户互动等多个维度。",
            self.styles['CustomBody']
        ))
        story.append(Paragraph(
            "This report provides a comprehensive analysis of the cross-border e-commerce market "
            "based on sales data, product reviews, and user feedback from Amazon and TikTok platforms.",
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # Amazon Sales Analysis
        if 'amazon_sales' in summary:
            story.append(PageBreak())
            story.append(Paragraph("二、Amazon销售数据分析 / Amazon Sales Analysis", self.styles['CustomHeading']))
            
            amazon_data = summary['amazon_sales']
            
            # Create summary table
            table_data = [
                ['指标 / Metric', '数值 / Value'],
                ['产品总数 / Total Products', str(amazon_data['total_products'])],
                ['月总销量 / Total Monthly Sales', f"{amazon_data['total_monthly_sales']:,.0f}"],
                ['月总销售额 / Total Monthly Revenue', f"${amazon_data['total_monthly_revenue']:,.2f}"],
                ['平均价格 / Average Price', f"${amazon_data['avg_price']:.2f}"],
                ['平均评分 / Average Rating', f"{amazon_data['avg_rating']:.2f}"]
            ]
            
            table = Table(table_data, colWidths=[3*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
            
            # Top categories chart
            if amazon_data['top_categories']:
                chart_path = self._create_chart(
                    amazon_data['top_categories'],
                    'bar',
                    'amazon_categories.png'
                )
                story.append(Paragraph("热门类目分布 / Top Categories Distribution", self.styles['CustomBody']))
                story.append(Spacer(1, 0.1*inch))
                story.append(Image(chart_path, width=5*inch, height=3*inch))
                story.append(Spacer(1, 0.2*inch))
        
        # TikTok Sales Analysis
        if 'tiktok_sales' in summary:
            story.append(PageBreak())
            story.append(Paragraph("三、TikTok销售数据分析 / TikTok Sales Analysis", self.styles['CustomHeading']))
            
            tiktok_data = summary['tiktok_sales']
            
            table_data = [
                ['指标 / Metric', '数值 / Value'],
                ['产品总数 / Total Products', str(tiktok_data['total_products'])],
                ['总销量 / Total Sales Volume', f"{tiktok_data['total_sales_volume']:,.0f}"],
                ['总销售额 / Total Revenue', f"${tiktok_data['total_revenue']:,.2f}"],
                ['平均价格 / Average Price', f"${tiktok_data['avg_price']:.2f}"]
            ]
            
            table = Table(table_data, colWidths=[3*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
            
            if tiktok_data['top_categories']:
                chart_path = self._create_chart(
                    tiktok_data['top_categories'],
                    'bar',
                    'tiktok_categories.png'
                )
                story.append(Paragraph("热门类目分布 / Top Categories Distribution", self.styles['CustomBody']))
                story.append(Spacer(1, 0.1*inch))
                story.append(Image(chart_path, width=5*inch, height=3*inch))
                story.append(Spacer(1, 0.2*inch))
        
        # Reviews Analysis
        if 'amazon_reviews' in summary or 'tiktok_shop_reviews' in summary:
            story.append(PageBreak())
            story.append(Paragraph("四、产品评价分析 / Product Reviews Analysis", self.styles['CustomHeading']))
            
            if 'amazon_reviews' in summary:
                story.append(Paragraph("Amazon产品评价 / Amazon Product Reviews", self.styles['Heading2']))
                amazon_reviews = summary['amazon_reviews']
                
                table_data = [
                    ['指标 / Metric', '数值 / Value'],
                    ['评论总数 / Total Reviews', str(amazon_reviews['total_reviews'])],
                    ['平均评分 / Average Rating', f"{amazon_reviews['avg_rating']:.2f} / 5.0"]
                ]
                
                table = Table(table_data, colWidths=[3*inch, 3*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Spacer(1, 0.2*inch))
                
                # Rating distribution
                if amazon_reviews['rating_distribution']:
                    chart_path = self._create_chart(
                        {f"{int(k)}星": v for k, v in amazon_reviews['rating_distribution'].items()},
                        'bar',
                        'amazon_rating_dist.png'
                    )
                    story.append(Paragraph("评分分布 / Rating Distribution", self.styles['CustomBody']))
                    story.append(Spacer(1, 0.1*inch))
                    story.append(Image(chart_path, width=5*inch, height=3*inch))
                    story.append(Spacer(1, 0.2*inch))
            
            if 'tiktok_shop_reviews' in summary:
                story.append(Paragraph("TikTok店铺评价 / TikTok Shop Reviews", self.styles['Heading2']))
                tiktok_reviews = summary['tiktok_shop_reviews']
                
                table_data = [
                    ['指标 / Metric', '数值 / Value'],
                    ['评论总数 / Total Reviews', str(tiktok_reviews['total_reviews'])],
                    ['平均评分 / Average Rating', f"{tiktok_reviews['avg_rating']:.2f} / 5.0"]
                ]
                
                table = Table(table_data, colWidths=[3*inch, 3*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Spacer(1, 0.2*inch))
        
        # Video Comments Analysis
        if 'tiktok_video_comments' in summary:
            story.append(PageBreak())
            story.append(Paragraph("五、用户互动分析 / User Engagement Analysis", self.styles['CustomHeading']))
            
            video_comments = summary['tiktok_video_comments']
            
            table_data = [
                ['指标 / Metric', '数值 / Value'],
                ['评论总数 / Total Comments', str(video_comments['total_comments'])],
                ['总点赞数 / Total Likes', f"{video_comments['total_likes']:,}"],
                ['平均点赞数 / Average Likes', f"{video_comments['avg_likes']:.2f}"]
            ]
            
            table = Table(table_data, colWidths=[3*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.2*inch))
        
        # Conclusions
        story.append(PageBreak())
        story.append(Paragraph("六、结论与建议 / Conclusions and Recommendations", self.styles['CustomHeading']))
        
        conclusions = [
            "1. 数据显示Amazon和TikTok平台均有良好的销售表现，建议持续优化产品组合。",
            "2. 产品评价整体呈正面趋势，应继续保持产品质量和客户服务水平。",
            "3. 用户互动数据表明视频营销效果显著，建议加大内容营销投入。",
            "4. 建议定期分析市场数据，及时调整运营策略以适应市场变化。"
        ]
        
        for conclusion in conclusions:
            story.append(Paragraph(conclusion, self.styles['CustomBody']))
            story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)
        
        print(f"Report generated successfully: {output_path}")
        return output_path


if __name__ == "__main__":
    # Test report generation
    cleaner = DataCleaner()
    cleaner.clean_all_data()
    
    generator = ReportGenerator()
    report_path = generator.generate_report(cleaner)
    print(f"Report saved to: {report_path}")

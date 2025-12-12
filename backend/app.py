"""
Flask API backend for Auto-Report system
Provides REST API endpoints for data access and report generation
"""

from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
from data_cleaner import DataCleaner
from report_generator import ReportGenerator
import os
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize data cleaner
data_cleaner = DataCleaner()
report_generator = ReportGenerator()

# Clean data on startup
print("Initializing and cleaning data...")
data_cleaner.clean_all_data()
print("Data cleaning completed!")


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Auto-Report API is running'
    })


@app.route('/api/data/summary', methods=['GET'])
def get_summary():
    """Get summary statistics of all data"""
    try:
        summary = data_cleaner.get_summary_statistics()
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/data/amazon-sales', methods=['GET'])
def get_amazon_sales():
    """Get cleaned Amazon sales data"""
    try:
        df = data_cleaner.cleaned_data.get('amazon_sales')
        if df is None:
            return jsonify({
                'success': False,
                'error': 'Data not available'
            }), 404
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Calculate pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Convert to JSON-friendly format
        data = df.iloc[start_idx:end_idx].to_dict(orient='records')
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(df),
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/data/tiktok-sales', methods=['GET'])
def get_tiktok_sales():
    """Get cleaned TikTok sales data"""
    try:
        df = data_cleaner.cleaned_data.get('tiktok_sales')
        if df is None:
            return jsonify({
                'success': False,
                'error': 'Data not available'
            }), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        data = df.iloc[start_idx:end_idx].to_dict(orient='records')
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(df),
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/data/amazon-reviews', methods=['GET'])
def get_amazon_reviews():
    """Get cleaned Amazon reviews data"""
    try:
        df = data_cleaner.cleaned_data.get('amazon_reviews')
        if df is None:
            return jsonify({
                'success': False,
                'error': 'Data not available'
            }), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        data = df.iloc[start_idx:end_idx].to_dict(orient='records')
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(df),
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/data/tiktok-reviews', methods=['GET'])
def get_tiktok_reviews():
    """Get cleaned TikTok shop reviews data"""
    try:
        df = data_cleaner.cleaned_data.get('tiktok_shop_reviews')
        if df is None:
            return jsonify({
                'success': False,
                'error': 'Data not available'
            }), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        data = df.iloc[start_idx:end_idx].to_dict(orient='records')
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(df),
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/data/video-comments', methods=['GET'])
def get_video_comments():
    """Get cleaned TikTok video comments data"""
    try:
        df = data_cleaner.cleaned_data.get('tiktok_video_comments')
        if df is None:
            return jsonify({
                'success': False,
                'error': 'Data not available'
            }), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        data = df.iloc[start_idx:end_idx].to_dict(orient='records')
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(df),
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/report/generate', methods=['POST'])
def generate_report():
    """Generate PDF report"""
    try:
        report_path = report_generator.generate_report(data_cleaner)
        
        return jsonify({
            'success': True,
            'message': 'Report generated successfully',
            'filename': os.path.basename(report_path)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/report/download/<filename>', methods=['GET'])
def download_report(filename):
    """Download generated report"""
    try:
        # Validate filename to prevent path traversal
        import os.path
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({
                'success': False,
                'error': 'Invalid filename'
            }), 400
        
        # Ensure filename ends with .pdf
        if not filename.endswith('.pdf'):
            return jsonify({
                'success': False,
                'error': 'Only PDF files are allowed'
            }), 400
        
        report_path = os.path.join(report_generator.output_dir, filename)
        
        # Verify the path is within the reports directory
        real_report_path = os.path.realpath(report_path)
        real_reports_dir = os.path.realpath(report_generator.output_dir)
        if not real_report_path.startswith(real_reports_dir):
            return jsonify({
                'success': False,
                'error': 'Invalid file path'
            }), 400
        
        if not os.path.exists(report_path):
            return jsonify({
                'success': False,
                'error': 'Report not found'
            }), 404
        
        return send_file(
            report_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/report/list', methods=['GET'])
def list_reports():
    """List all generated reports"""
    try:
        reports = []
        report_dir = report_generator.output_dir
        
        if os.path.exists(report_dir):
            for filename in os.listdir(report_dir):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(report_dir, filename)
                    file_stats = os.stat(file_path)
                    reports.append({
                        'filename': filename,
                        'size': file_stats.st_size,
                        'created': file_stats.st_ctime
                    })
        
        # Sort by creation time (newest first)
        reports.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            'success': True,
            'reports': reports
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Create reports directory
    os.makedirs('reports', exist_ok=True)
    
    # Run the Flask app
    # Note: For production, use a production WSGI server like gunicorn
    # and disable debug mode
    print("Starting Auto-Report API server...")
    print("API will be available at http://localhost:5000")
    print("WARNING: This is a development server. Do not use in production.")
    app.run(debug=True, host='0.0.0.0', port=5000)

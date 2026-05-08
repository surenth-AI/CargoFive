import os
import io
import threading
import uuid
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
from discovery_engine import discovery_engine
from mapping_engine import mapping_engine
from planner_engine import planner_engine
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import db


load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key-antigravity-123")

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# --- Global Task Tracker for Background Processing ---
processing_tasks = {}

# --- Session Authentication Helper ---
def is_logged_in():
    return 'user_id' in session

def is_lead():
    return session.get('role') == 'lead'

@app.route('/')
def index():
    if not is_logged_in():
        return redirect('/login')
    return render_template('index.html', username=session.get('username'), role=session.get('role'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json or request.form
        username = data.get('username')
        password = data.get('password')
        
        user = db.authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return jsonify({'success': True, 'role': user['role']})
        return jsonify({'error': 'Invalid username or password'}), 401
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# --- Lead Account Creation ---
@app.route('/admin/create_user', methods=['POST'])
def admin_create_user():
    if not is_logged_in() or not is_lead():
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'employee')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
        
    success = db.create_user(username, password, role)
    if success:
        return jsonify({'message': 'User created successfully!'})
    return jsonify({'error': 'Username already exists or creation failed'}), 400

# --- File Upload with Run Tracking ---
@app.route('/upload', methods=['POST'])
def upload_file():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Start tracking the run
            run_id = db.start_file_run(session['user_id'], filename)
            
            # Process the file using the AI Discovery Engine
            results = discovery_engine.process_excel(file_path)
            
            return jsonify({
                'sheets': results,
                'filename': filename,
                'run_id': run_id
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# --- File Processing with System Duration Tracking ---
@app.route('/process', methods=['POST'])
def process_to_template():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    workbook_data = data.get('sheets')
    original_filename = data.get('filename')
    run_id = data.get('run_id')
    
    if not workbook_data:
        return jsonify({'error': 'No data to process'}), 400
        
    task_id = str(uuid.uuid4())
    processing_tasks[task_id] = {
        'status': 'processing',
        'progress': 0,
        'result': None,
        'error': None
    }

    def run_background_process(tid, w_data, o_filename, r_id):
        try:
            start_time = datetime.now()
            
            # 1. Generate strategic plan
            plan = planner_engine.generate_plan(w_data)
            schedule = plan.get('schedule', [])
            
            all_mapped_rows = []
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(mapping_engine.process_task, task, w_data) for task in schedule]
                for idx, future in enumerate(futures):
                    try:
                        mapped_rows = future.result()
                        all_mapped_rows.extend(mapped_rows)
                        # Update progress
                        processing_tasks[tid]['progress'] = int(((idx + 1) / len(futures)) * 100)
                    except Exception as task_error:
                        print(f"Error processing task concurrently: {task_error}")

            if not all_mapped_rows:
                processing_tasks[tid]['status'] = 'failed'
                processing_tasks[tid]['error'] = 'No relevant rate data found in tables'
                return
                
            output_filename = f"processed_{o_filename}"
            if not output_filename.endswith('.xlsx'):
                output_filename += '.xlsx'
                
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            # Deduplicate and merge rows based on core key fields
            total_before = len(all_mapped_rows)
            grouped_rows = {}
            
            def clean_price(val):
                if val is None: return ""
                try:
                    clean_val = "".join(c for c in str(val) if c.isdigit())
                    return str(int(clean_val)) if clean_val else ""
                except:
                    return ""

            for row in all_mapped_rows:
                origin = str(row.get("ORIGIN PORT") or row.get("ORIGIN LOCATION") or row.get("ORIGIN") or "").strip().upper()
                dest = str(row.get("DESTINATION PORT") or row.get("DESTINATION LOCATION") or row.get("DESTINATION") or "").strip().upper()
                start_date = str(row.get("START DATE") or "").split('T')[0].split(' ')[0].strip()
                exp_date = str(row.get("EXPIRATION DATE") or "").split('T')[0].split(' ')[0].strip()
                
                sig_fields = [
                    origin, dest,
                    str(row.get("CHARGE", "")).strip().upper(),
                    str(row.get("PROVIDER", "")).strip().upper(),
                    start_date, exp_date,
                    clean_price(row.get("20DRY")),
                    clean_price(row.get("40DRY")),
                    clean_price(row.get("40HDRY")),
                    clean_price(row.get("45HDRY")),
                ]
                signature = "|".join(sig_fields)
                
                if signature not in grouped_rows:
                    grouped_rows[signature] = dict(row)
                else:
                    existing_row = grouped_rows[signature]
                    existing_remarks = str(existing_row.get("REMARKS") or "").strip()
                    new_remarks = str(row.get("REMARKS") or "").strip()
                    if new_remarks and new_remarks.upper() not in existing_remarks.upper():
                        existing_row["REMARKS"] = f"{existing_remarks} | {new_remarks}" if existing_remarks else new_remarks
                    
                    existing_notes = str(existing_row.get("NOTES") or "").strip()
                    new_notes = str(row.get("NOTES") or "").strip()
                    if new_notes and new_notes.upper() not in existing_notes.upper():
                        existing_row["NOTES"] = f"{existing_notes} | {new_notes}" if existing_notes else new_notes

            all_mapped_rows = list(grouped_rows.values())
            success = mapping_engine.write_to_template(all_mapped_rows, output_path)

            end_time = datetime.now()
            system_duration_sec = int((end_time - start_time).total_seconds())
            
            if success:
                if r_id:
                    db.complete_file_run(r_id, system_duration_sec)
                
                processing_tasks[tid]['status'] = 'completed'
                processing_tasks[tid]['result'] = {
                    'download_url': f'/download/{output_filename}',
                    'row_count': len(all_mapped_rows),
                    'system_duration_sec': system_duration_sec
                }
            else:
                processing_tasks[tid]['status'] = 'failed'
                processing_tasks[tid]['error'] = 'Failed to write to template'
                
        except Exception as e:
            import traceback
            print(f"Processing error: {e}")
            print(traceback.format_exc())
            processing_tasks[tid]['status'] = 'failed'
            processing_tasks[tid]['error'] = str(e)

    # Start the thread
    thread = threading.Thread(target=run_background_process, args=(task_id, workbook_data, original_filename, run_id))
    thread.daemon = True
    thread.start()

    return jsonify({'task_id': task_id})

@app.route('/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
        
    task = processing_tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
        
    return jsonify(task)


# --- Update Manual Balance Time ---
@app.route('/run/update_manual_time', methods=['POST'])
def update_manual_time():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    run_id = data.get('run_id')
    manual_duration_sec = int(data.get('manual_duration_sec', 0))
    
    if not run_id:
        return jsonify({'error': 'Run ID is required'}), 400
        
    db.update_manual_time(run_id, manual_duration_sec)
    return jsonify({'success': True, 'message': 'Manual time updated!'})

# --- Lead & User APIs ---
@app.route('/api/user_history')
def api_user_history():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    history = db.get_user_history(session['user_id'])
    return jsonify({'history': history})

@app.route('/api/lead_dashboard')
def api_lead_dashboard():
    if not is_logged_in() or not is_lead():
        return jsonify({'error': 'Unauthorized'}), 403
    kpis = db.get_employee_kpis()
    history = db.get_lead_history()
    users = db.get_all_users()
    return jsonify({
        'kpis': kpis,
        'history': history,
        'users': [dict(row) for row in users]
    })

# --- Excel Log Report Export ---
@app.route('/export_report')
def export_report():
    if not is_logged_in():
        return redirect('/login')
        
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    # Filter by date if provided
    if from_date:
        from_date = f"{from_date} 00:00:00"
    if to_date:
        to_date = f"{to_date} 23:59:59"
        
    if is_lead():
        # Export entire team report
        data_rows = db.get_lead_history(from_date, to_date)
        columns = ['ID', 'Employee', 'Filename', 'Start Time', 'End Time', 'System Duration (s)', 'Manual Duration (s)', 'Status', 'Created At']
    else:
        # Export individual employee report
        data_rows = db.get_user_history(session['user_id'], from_date, to_date)
        columns = ['ID', 'Filename', 'Start Time', 'End Time', 'System Duration (s)', 'Manual Duration (s)', 'Status', 'Created At']

    df = pd.DataFrame(data_rows)
    if not df.empty:
        # Keep only appropriate columns
        df.columns = [c.upper() for c in df.columns]
        
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Performance Report")
        
    output.seek(0)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"performance_report_{session['username']}_{timestamp}.xlsx"
    
    return send_file(output, as_attachment=True, download_name=report_name, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.route('/download/<filename>')
def download_file(filename):
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

# --- Log Issue / Feedback Route ---
@app.route('/api/log_issue', methods=['POST'])
def api_log_issue():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    category = data.get('category')
    severity = data.get('severity')
    title = data.get('title')
    description = data.get('description')
    performance_rating = int(data.get('performance_rating', 5))
    
    if not category or not severity or not title or not description:
        return jsonify({'error': 'All fields are required!'}), 400
        
    db.log_issue(session['user_id'], category, severity, title, description, performance_rating)
    return jsonify({'success': True, 'message': 'Issue/Feedback logged successfully!'})

# --- Get All Issues Route ---
@app.route('/api/issues')
def api_all_issues():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    issues = db.get_all_issues()
    return jsonify({'issues': issues})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5011))
    app.run(host='0.0.0.0', port=port, debug=True)

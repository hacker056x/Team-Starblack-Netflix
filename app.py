#!/usr/bin/env python3
"""
Netflix Cookie to NFToken Generator - Web Version
Con sistema completo de registro y login de usuarios
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import json
import os
import hashlib
import secrets
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from functools import wraps
import uuid

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

# Archivo para almacenar usuarios
USERS_FILE = 'users.txt'

# ==================== SISTEMA DE USUARIOS ====================

def init_users_file():
    """Inicializa el archivo de usuarios si no existe"""
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            # Usuario administrador por defecto
            admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
            f.write(f"admin:{admin_password}:Administrator:admin@netflix.com:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def validate_username(username: str) -> Tuple[bool, str]:
    """Valida el nombre de usuario"""
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 20:
        return False, "Username must be less than 20 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers and underscores"
    return True, ""

def validate_password(password: str) -> Tuple[bool, str]:
    """Valida la contraseña"""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters"
    if len(password) > 50:
        return False, "Password must be less than 50 characters"
    return True, ""

def validate_email(email: str) -> Tuple[bool, str]:
    """Valida el correo electrónico"""
    if email and email.strip():
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, "Invalid email format"
    return True, ""

def user_exists(username: str) -> bool:
    """Verifica si un usuario ya existe"""
    try:
        with open(USERS_FILE, 'r') as f:
            for line in f:
                if line.startswith(f"{username}:"):
                    return True
        return False
    except Exception:
        return False

def register_user(username: str, password: str, email: str = "") -> Tuple[bool, str]:
    """Registra un nuevo usuario"""
    try:
        # Validaciones
        valid, msg = validate_username(username)
        if not valid:
            return False, msg
        
        valid, msg = validate_password(password)
        if not valid:
            return False, msg
        
        valid, msg = validate_email(email)
        if not valid:
            return False, msg
        
        # Verificar si ya existe
        if user_exists(username):
            return False, "Username already exists"
        
        # Registrar usuario
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        email_field = email if email else "N/A"
        
        with open(USERS_FILE, 'a') as f:
            f.write(f"{username}:{hashed_password}:{email_field}:{created_at}\n")
        
        return True, "User registered successfully"
        
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def verify_user(username: str, password: str) -> bool:
    """Verifica las credenciales del usuario"""
    try:
        with open(USERS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(':')
                    stored_user = parts[0]
                    stored_pass = parts[1]
                    if stored_user == username:
                        hashed_input = hashlib.sha256(password.encode()).hexdigest()
                        return hashed_input == stored_pass
        return False
    except Exception:
        return False

def get_user_info(username: str) -> Dict:
    """Obtiene información del usuario"""
    try:
        with open(USERS_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if parts[0] == username:
                    return {
                        'username': parts[0],
                        'email': parts[2] if len(parts) > 2 else 'N/A',
                        'created_at': parts[3] if len(parts) > 3 else 'Unknown'
                    }
        return None
    except Exception:
        return None

def login_required(f):
    """Decorador para rutas que requieren login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Inicializar archivo de usuarios
init_users_file()

# ==================== CLASE NETFLIX TOKEN CHECKER ====================

class NetflixTokenChecker:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'com.netflix.mediaclient/63884 (Linux; U; Android 13; ro; M2007J3SG; Build/TQ1A.230205.001.A2; Cronet/143.0.7445.0)',
            'Accept': 'multipart/mixed;deferSpec=20220824, application/graphql-response+json, application/json',
            'Content-Type': 'application/json',
            'Origin': 'https://www.netflix.com',
            'Referer': 'https://www.netflix.com/'
        }
        self.api_url = 'https://android13.prod.ftl.netflix.com/graphql'

    def parse_netscape_cookie_line(self, line: str) -> Dict[str, str]:
        parts = line.strip().split('\t')
        if len(parts) >= 7:
            name = parts[5]
            value = parts[6]
            return {name: value}
        return {}

    def parse_netscape_cookies(self, content: str) -> List[Dict[str, str]]:
        cookies_list = []
        current_cookie_set = {}
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            cookie = self.parse_netscape_cookie_line(line)
            if cookie:
                current_cookie_set.update(cookie)
                if 'NetflixId' in current_cookie_set and 'SecureNetflixId' in current_cookie_set and 'nfvdid' in current_cookie_set:
                    cookies_list.append(current_cookie_set.copy())
                    current_cookie_set = {}
        return cookies_list

    def extract_cookies_from_text(self, text: str) -> List[Dict[str, str]]:
        if '\t' in text and ('NetflixId' in text or 'nfvdid' in text):
            netscape_cookies = self.parse_netscape_cookies(text)
            if netscape_cookies:
                return netscape_cookies
        return []

    def build_cookie_string(self, cookie_dict: Dict[str, str]) -> str:
        return '; '.join([f"{k}={v}" for k, v in cookie_dict.items()])

    def generate_token(self, cookie_dict: Dict[str, str]) -> Tuple[bool, Optional[str], Optional[str]]:
        required = ['NetflixId', 'SecureNetflixId', 'nfvdid']
        missing = [c for c in required if c not in cookie_dict]
        if missing:
            return False, None, f"Missing cookies: {', '.join(missing)}"

        cookie_str = self.build_cookie_string(cookie_dict)
        payload = {
            "operationName": "CreateAutoLoginToken",
            "variables": {"scope": "WEBVIEW_MOBILE_STREAMING"},
            "extensions": {
                "persistedQuery": {
                    "version": 102,
                    "id": "76e97129-f4b5-41a0-a73c-12e674896849"
                }
            }
        }
        headers = self.headers.copy()
        headers['Cookie'] = cookie_str

        try:
            response = self.session.post(self.api_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data'] and 'createAutoLoginToken' in data['data']:
                    return True, data['data']['createAutoLoginToken'], None
                elif 'errors' in data:
                    return False, None, f"API Error: {data['errors'][0].get('message', 'Unknown error')}"
                else:
                    return False, None, f"Unexpected response: {data}"
            elif response.status_code == 401:
                return False, None, "Expired cookies (401 Unauthorized)"
            else:
                return False, None, f"HTTP {response.status_code}: {response.text[:200]}"
        except Exception as e:
            return False, None, f"Connection error: {str(e)}"

    def format_nftoken_link(self, token: str) -> str:
        return f"https://netflix.com/?nftoken={token}"

checker = NetflixTokenChecker()

# ==================== RUTAS ====================

@app.route('/')
@login_required
def index():
    """Página principal (protegida)"""
    user_info = get_user_info(session.get('username'))
    return render_template('index.html', 
                         username=session.get('username', 'User'),
                         user_email=user_info.get('email') if user_info else 'N/A')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('login.html', error='Please enter username and password')
        
        if verify_user(username, password):
            session['logged_in'] = True
            session['username'] = username
            session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro de nuevos usuarios"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        email = request.form.get('email', '').strip()
        
        # Validaciones
        if not username or not password:
            return render_template('register.html', error='Please fill all required fields')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        # Registrar usuario
        success, message = register_user(username, password, email)
        
        if success:
            return render_template('register.html', success=message)
        else:
            return render_template('register.html', error=message)
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/process', methods=['POST'])
@login_required
def process():
    """Procesa las cookies y genera tokens"""
    try:
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            content = file.read().decode('utf-8', errors='ignore')
        else:
            content = request.form.get('cookies_text', '')
            
        if not content:
            return jsonify({'error': 'No cookies provided'}), 400
            
        cookies_list = checker.extract_cookies_from_text(content)
        
        if not cookies_list:
            return jsonify({'error': 'No valid Netflix cookies found in the provided text/file'}), 400
            
        results = []
        session_id = str(uuid.uuid4())[:8]
        
        for idx, cookie_dict in enumerate(cookies_list, 1):
            success, token, error = checker.generate_token(cookie_dict)
            
            if success and token:
                results.append({
                    'index': idx,
                    'success': True,
                    'token': token,
                    'link': checker.format_nftoken_link(token),
                    'cookies': {k: v[:20] + '...' for k, v in cookie_dict.items()}
                })
            else:
                results.append({
                    'index': idx,
                    'success': False,
                    'error': error,
                    'cookies': {k: v[:20] + '...' for k, v in cookie_dict.items()}
                })
        
        return jsonify({
            'success': True,
            'total': len(cookies_list),
            'valid': len([r for r in results if r['success']]),
            'results': results,
            'session_id': session_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/export', methods=['POST'])
@login_required
def export():
    """Exporta resultados a archivo de texto"""
    try:
        data = request.json
        results = data.get('results', [])
        
        if not results:
            return jsonify({'error': 'No results to export'}), 400
            
        content = "NETFLIX TOKENS GENERATED\n"
        content += "=" * 60 + "\n"
        content += f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"User: {session.get('username', 'Unknown')}\n\n"
        
        for r in results:
            if r['success']:
                content += f"\n--- Token #{r['index']} ---\n"
                content += f"🔗 Token: {r['token']}\n"
                content += f"🔗 Link: {r['link']}\n"
                content += "Cookies used:\n"
                for k, v in r['cookies'].items():
                    content += f"  {k}: {v}\n"
                content += "\n" + "-" * 40 + "\n"
        
        return jsonify({
            'success': True,
            'content': content,
            'filename': f"netflix_tokens_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        })
        
    except Exception as e:
        return jsonify({'error': f'Export error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
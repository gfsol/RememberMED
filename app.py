from flask import Flask, request, render_template, session
from BBDD import DatabaseManager
import json
import requests
from googletrans import Translator
from datetime import datetime, timedelta
import threading  # Para programar el envío de mensajes
import re
import schedule
import time
import os

# Configuración de OpenFDA
OPENFDA_URL = "https://api.fda.gov/drug/label.json?search=openfda.substance_name:"

app = Flask(__name__)
db = DatabaseManager("database.db")
translator = Translator()
app.secret_key = os.urandom(24)  # Clave secreta para sesiones

# Diccionario para gestionar el estado de los usuarios
user_states = {}

def fetch_medication_info(medication_name):
    # Similar al código original
    search_url = f"{OPENFDA_URL}{medication_name}&limit=1"
    response = requests.get(search_url)
    if response.status_code == 200:
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            medication_name = result.get("openfda", {}).get("generic_name", ["No disponible"])[0]
            route_of_administration = result.get("openfda", {}).get("route", ["No disponible"])[0]
            warnings = result.get("warnings_and_cautions", result.get("warnings", ["No disponibles"]))
            dosage_and_administration = result.get("dosage_and_administration", ["No disponible"])
            indications = result.get("indications_and_usage", ["No disponibles"])
            
            warnings_text = warnings[0] if warnings else "No disponibles"
            dosage_text = dosage_and_administration[0] if dosage_and_administration else "No disponible"
            indications_text = indications[0] if indications else "No disponibles"

            medication_info = f"""📌 *Información del Medicamento*  
🩺 *Nombre:* `{medication_name}`  
💊 *Ruta de Administración:* `{route_of_administration}`  
⚠️ *Advertencias sobre Alergias:* {warnings_text}  
📏 *Dosis y Administración:* {dosage_text}  
📜 *Indicaciones:* {indications_text}"""
            
            try:
                translated_info = translator.translate(medication_info, src="en", dest="es").text
                return translated_info if translated_info else medication_info
            except Exception as e:
                return medication_info
    return "❌ No se encontró información sobre el medicamento."

def send_telegram_message(token, chat_id, message, reply_markup=None):
    """Envía un mensaje a Telegram usando Markdown y un teclado opcional"""
    TELEGRAM_URL = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": reply_markup
    }
    response = requests.post(TELEGRAM_URL, data=payload)
    return response.status_code == 200 and response.json().get("ok", False)

def calculate_dosage_times(start_time, hours_between, doses):
    # Comprobar si start_time es una cadena y convertirla solo si es necesario
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, "%H:%M")

    dosage_times = []
    for i in range(doses):
        dosage_times.append(start_time.strftime("%H:%M"))
        start_time = start_time + timedelta(hours=hours_between)
    
    return dosage_times


def send_reminder(token, chat_id, medication_name, dose, recordatorio_id, remaining_doses, next_dose_time):
    # Modificar el mensaje para incluir nombre del medicamento, dosis, número de dosis restantes y hora de la próxima dosis
    message = f"📌 *Recordatorio de Medicamento* \n\n" \
              f"💊 *Medicamento:* {medication_name} \n" \
              f"📏 *Dosis:* {dose} \n" \
              f"🔢 *Dosis restantes:* {remaining_doses} \n" \
              f"🕒 *Próxima dosis:* {next_dose_time}"

    db.marcar_dosis_tomada(recordatorio_id)

    # Enviar el mensaje a Telegram
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, data=data)

    if response.status_code != 200:
        print(f"Error al enviar el recordatorio: {response.text}")
    else:
        print(f"Recordatorio enviado: {message}")

import threading
from datetime import datetime, timedelta

def schedule_reminders(token, chat_id, medication_name, dose_info, dosage, doses_remaining, recordatorio_id):
    for i, dose_time in enumerate(dose_info):
        # Convertimos el horario de la dosis a un objeto datetime del día de hoy
        hour, minute = map(int, dose_time.split(":"))
        now = datetime.now()
        reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # Si la hora ya pasó hoy, la programamos para mañana
        if reminder_time < now:
            reminder_time += timedelta(days=1)

        delay = (reminder_time - now).total_seconds()

        # Ajustamos las dosis restantes
        remaining = doses_remaining - (i + 1)

        # Próxima dosis
        if i + 1 < len(dose_info):
            next_dose_time = dose_info[i + 1]
        else:
            next_dose_time = "No hay más dosis"

        print(f"✅ Programando recordatorio #{i+1} para las {reminder_time.strftime('%H:%M:%S')}")

        # Usamos threading.Timer para programar la ejecución
        threading.Timer(delay, send_reminder, kwargs={
            'token': token,
            'chat_id': chat_id,
            'medication_name': medication_name,
            'dose': dosage,
            'recordatorio_id': recordatorio_id,
            'remaining_doses': remaining,
            'next_dose_time': next_dose_time
        }).start()

def run_scheduled_tasks():
    while True:
        schedule.run_pending()
        time.sleep(60)  # Revisa las tareas programadas cada 60 segundos

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        token = request.form["token"]
        chat_id = request.form["chat_id"]
        session["chat_id"] = chat_id
        session["token"] = token
        
        # Enviar mensaje de bienvenida indicando que el usuario debe usar /start
        welcome_message = "¡Hola! Bienvenido al sistema de recordatorios y búsqueda de información sobre medicamentos. Para comenzar, por favor usa el comando /start."
        
        send_telegram_message(token, chat_id, welcome_message)

        return render_template("index.html", success=True, token=token, chat_id=chat_id)
    
    return render_template("index.html")


@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    data = request.json
    token = request.args.get("token")  # Obtenemos el token desde la URL
    session["token"] = token  # Guardamos el token en la sesión
    chat_id = data["message"]["chat"]["id"]
    text = data["message"]["text"]

    if chat_id not in user_states:
        # Crear el usuario en la base de datos si no existe
        nombre = data["message"]["chat"].get("first_name", "Desconocido")
        telefono = None  # Aquí puedes agregar un campo de teléfono si lo deseas
        db.add_usuario(chat_id, nombre, telefono)
        user_states[chat_id] = {"step": "initial"}

    if text.lower() == "/start":
        user_states[chat_id]["step"] = "menu"
        keyboard = {
            "keyboard": [
    ["1. Establecer recordatorio", "2. Obtener información medicamento"],
    ["3. Ver mis recordatorios", "4. Borrar recordatorio"],
    ["5. Suscribirse a Premium"]],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        send_telegram_message(token, chat_id, "¡Hola! Elige una opción:", reply_markup=json.dumps(keyboard))
    
    elif user_states[chat_id]["step"] == "menu" and text.lower() == "2. obtener información medicamento":
        user_states[chat_id]["step"] = "getting_medication"
        send_telegram_message(token, chat_id, "Introduce el nombre genérico del medicamento que deseas buscar.")
    
    elif user_states[chat_id]["step"] == "menu" and text.lower() == "1. establecer recordatorio":
        user_states[chat_id]["step"] = "setting_reminder"
        # Verificar límite de recordatorios si no es premium
        if not db.es_usuario_premium(chat_id):
            recordatorios_activos = db.get_recordatorios_activos(chat_id)
            if len(recordatorios_activos) >= 3:
                send_telegram_message(
                    token,
                    chat_id,
                    "❌ Has alcanzado el límite de 3 recordatorios.\n"
                    "¡Actualiza a Premium para crear recordatorios ilimitados!\n\n"
                    "Selecciona '5. Suscribirse a Premium' para más información."
                )
                 
                return "OK", 200
        send_telegram_message(token, chat_id, "Por favor, introduce el nombre del medicamento.")
    
    elif user_states[chat_id]["step"] == "getting_medication":
        medication_name = text.strip()
        medication_info = fetch_medication_info(medication_name)
        send_telegram_message(token, chat_id, medication_info)
        user_states[chat_id]["step"] = "menu"
    
    elif user_states[chat_id]["step"] == "setting_reminder":        
        user_states[chat_id]["medication_name"] = text.strip()
        send_telegram_message(token, chat_id, "Introduce la dosis (ej. 1 tableta).")
        user_states[chat_id]["step"] = "getting_dosage"
    
    elif user_states[chat_id]["step"] == "getting_dosage":
        user_states[chat_id]["dosage"] = text.strip()
        send_telegram_message(token, chat_id, "¿Cada cuántas horas debe tomarse? (ej. 4 horas).")
        user_states[chat_id]["step"] = "getting_frequency"
    
    elif user_states[chat_id]["step"] == "getting_frequency":
        try:
            user_states[chat_id]["hours_between"] = int(text.strip())
            send_telegram_message(token, chat_id, "¿Cuántas dosis necesitas?")
            user_states[chat_id]["step"] = "getting_doses"
        except ValueError:
            send_telegram_message(token, chat_id, "Introduce un número válido para la frecuencia.")
    
    elif user_states[chat_id]["step"] == "getting_doses":
        try:
            user_states[chat_id]["doses"] = int(text.strip())
            send_telegram_message(token, chat_id, "Introduce la hora de comienzo (HH:MM).")
            user_states[chat_id]["step"] = "getting_start_time"
        except ValueError:
            send_telegram_message(token, chat_id, "Introduce un número válido para la cantidad de dosis.")
    
    elif user_states[chat_id]["step"] == "getting_start_time":
        if re.match(r"^([01]?[0-9]|2[0-3]):([0-5][0-9])$", text.strip()):
            start_time = datetime.strptime(text.strip(), "%H:%M")
            doses_info = calculate_dosage_times(start_time, user_states[chat_id]["hours_between"], user_states[chat_id]["doses"])
            send_telegram_message(token, chat_id, f"Recordatorios configurados para: {', '.join(doses_info)}")
            
            hora_inicio = start_time.strftime("%H:%M")
            medicamento = user_states[chat_id]["medication_name"]
            dosis = user_states[chat_id]["dosage"]
            frecuencia = user_states[chat_id]["hours_between"]
            total_dosis = user_states[chat_id]["doses"]

            keyboard = {
                "keyboard": [["Sí", "No"]],
                "resize_keyboard": True,
                "one_time_keyboard": True
            }

            idRecordatorio = db.add_recordatorio(chat_id, medicamento, dosis, frecuencia, hora_inicio, total_dosis)
            db.programar_dosis(idRecordatorio, hora_inicio, frecuencia, total_dosis)
            schedule_reminders(token, chat_id, medicamento, doses_info, dosis, total_dosis, idRecordatorio)
            send_telegram_message(token, chat_id, "¿Deseas conocer información sobre el medicamento?", reply_markup=json.dumps(keyboard))
            user_states[chat_id]["step"] = "ask_medication_info"
        else:
            send_telegram_message(token, chat_id, "Introduce una hora válida en formato HH:MM (ej. 20:00).")
    
    elif user_states[chat_id]["step"] == "ask_medication_info":
        if text.lower() == "sí":
            medication_info = fetch_medication_info(user_states[chat_id]["medication_name"])
            send_telegram_message(token, chat_id, medication_info)
        send_telegram_message(token, chat_id, "¿Te gustaría hacer otra cosa?", reply_markup=json.dumps({
            "keyboard": [
    ["1. Establecer recordatorio", "2. Obtener información medicamento"],
    ["3. Ver mis recordatorios", "4. Borrar recordatorio"],
    ["5. Suscribirse a Premium"]
],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }))
        user_states[chat_id]["step"] = "menu"

    elif user_states[chat_id]["step"] == "menu" and text.lower() == "3. ver mis recordatorios":
        recordatorios = db.get_recordatorios_activos(chat_id)
        if not recordatorios:
            send_telegram_message(token, chat_id, "📭 No tienes recordatorios activos.")
            user_states[chat_id]["step"] = "menu"        
        else:
            for r in recordatorios:
                recordatorio_id, medicamento, dosis, frecuencia_horas, hora_inicio, dosis_totales = r
                
                # Obtener dosis restantes
                dosis_restantes = db.get_dosis_restantes(recordatorio_id)
                
                # Obtener la próxima dosis
                proxima_dosis = db.get_siguiente_dosis(recordatorio_id)
                
                # Crear el mensaje
                mensaje = f"💊 *Medicamento:* {medicamento}\n📏 *Dosis:* {dosis}\n🔢 *Dosis restantes:* {dosis_restantes}\n🕒 *Próxima dosis:* {proxima_dosis if proxima_dosis else 'No programada'}"
                
                # Enviar el mensaje
                send_telegram_message(token, chat_id, mensaje)

            send_telegram_message(token, chat_id, "¿Te gustaría hacer otra cosa?", reply_markup=json.dumps({
                "keyboard": [
                    ["1. Establecer recordatorio", "2. Obtener información medicamento"],
                    ["3. Ver mis recordatorios", "4. Borrar recordatorio"],
                    ["5. Suscribirse a Premium"]
                ],
                "resize_keyboard": True,
                "one_time_keyboard": True
            }))
            user_states[chat_id]["step"] = "menu"
                
    elif user_states[chat_id]["step"] == "menu" and text.lower() == "4. borrar recordatorio":
        # Obtener recordatorios activos del usuario
        recordatorios = db.get_recordatorios_activos(chat_id)
    
        if not recordatorios:
            send_telegram_message(token, chat_id, "📭 No tienes recordatorios activos para borrar.")
            
            
    
        # Crear mensaje con lista numerada de recordatorios
        mensaje = "📋 Tus recordatorios activos:\n\n"
        opciones = []
    
        for i, r in enumerate(recordatorios, start=1):
            recordatorio_id, medicamento, dosis, _, hora_inicio, _ = r
            dosis_restantes = db.get_dosis_restantes(recordatorio_id)
            proxima_dosis = db.get_siguiente_dosis(recordatorio_id)
        
            mensaje += f"{i}. {medicamento}\n"
            mensaje += f"   - Dosis: {dosis}\n"
            mensaje += f"   - Dosis restantes: {dosis_restantes}\n"
            mensaje += f"   - Próxima dosis: {proxima_dosis if proxima_dosis else 'No programada'}\n\n"
        
            opciones.append((i, recordatorio_id))
    
        mensaje += "\nResponde con el número del recordatorio que quieres borrar."
    
        # Guardar las opciones disponibles en el estado del usuario
        user_states[chat_id] = {
            "step": "deleting_reminder",
            "opciones": dict(opciones)
        }
    
        send_telegram_message(token, chat_id, mensaje)

    elif user_states[chat_id]["step"] == "deleting_reminder":
        try:
            # Obtener el número seleccionado
            seleccion = int(text.strip())
            recordatorio_id = user_states[chat_id]["opciones"].get(seleccion)
        
            if recordatorio_id:
                # Borrar el recordatorio y sus dosis
                db.delete_recordatorio(recordatorio_id)
                send_telegram_message(token, chat_id, "✅ Recordatorio eliminado correctamente.")
            else:
                send_telegram_message(token, chat_id, "❌ Número no válido.")
            
        except ValueError:
            send_telegram_message(token, chat_id, "❌ Por favor, introduce solo el número del    recordatorio.")
    
        # Volver al menú principal
        send_telegram_message(token, chat_id, "¿Qué más deseas hacer?", reply_markup=json.dumps({
            "keyboard": [
                ["1. Establecer recordatorio", "2. Obtener información medicamento"],
                ["3. Ver mis recordatorios", "4. Borrar recordatorio"],
                ["5. Suscribirse a Premium"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }))
        user_states[chat_id]["step"] = "menu"

    elif user_states[chat_id]["step"] == "menu" and text.lower() == "5. suscribirse a premium":
        user_states[chat_id]["step"] = "premium"
        send_telegram_message(
                token,
                chat_id,
                "Por favor, ingresa a nuestra página web para poder suscribirte a nuestro programa premium."
            )
    
    return "OK", 200

@app.route("/premium", methods=["GET", "POST"])
def premium():

    if request.method == "POST":
        nombre = request.form.get("nombre")
        telefono = request.form.get("telefono")
        plan = request.form.get("plan")
        metodo_pago = request.form.get("metodoPago")
        numero_tarjeta = request.form.get("numeroTarjeta")
        fecha_vencimiento = request.form.get("fechaVencimiento")
        cvv = request.form.get("cvv")

        chat_id = session.get("chat_id")


        if chat_id:
            try:
                # Validar datos antes de procesar
                if not all([nombre, numero_tarjeta, fecha_vencimiento, cvv]):
                    return render_template(
                        "premium_formulario.html",
                        error="Por favor completa todos los campos requeridos"
                    )
                
                #Procesar el pago
                db.agregar_cuenta_bancaria(chat_id, numero_tarjeta, nombre, fecha_vencimiento, cvv)

                db.marcar_como_premium(chat_id)

                token = session.get("token")

                send_telegram_message(
                    token,
                    chat_id,
                    "¡Felicidades! Ahora eres un usuario Premium. Disfruta de los beneficios."
                )
                # Aplicar lógica para procesar el formulario de premium
                return render_template(
                        "premium_formulario.html",
                        success=True,
                        nombre=nombre,
                        plan=plan
                    )

            except Exception as e:
                return render_template(
                    "premium_formulario.html",
                    error=f"Error al procesar el pago: {str(e)}"
                )
        

    return render_template("premium_formulario.html")


@app.route('/start', methods=['POST'])
def start():
    chat_id = request.json.get('chat_id')
    nombre = request.json.get('nombre', None)
    telefono = request.json.get('telefono', None)

    if not chat_id:
        return jsonify({"error": "El chat_id es obligatorio"}), 400

    usuario_id = db.add_usuario(chat_id, nombre, telefono)
    return jsonify({"message": "Usuario creado correctamente", "usuario_id": usuario_id}), 201

if __name__ == "__main__":
    # Iniciar en un hilo los recordatorios programados
    threading.Thread(target=run_scheduled_tasks, daemon=True).start()
    app.run(debug=True, host='0.0.0.0')

import sqlite3
from datetime import datetime, timedelta
from threading import local
import re

class DatabaseManager:
    def __init__(self, db_name="database.db"):
        self._local = local()  # Almacenamiento local por hilo
        self.db_name = db_name
        
        
        # Inicializa la conexión para el hilo principal
        self._init_connection()

    def _init_connection(self):
        """Inicializa la conexión y crea tablas si no existen"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('PRAGMA journal_mode=WAL;')

        # Crear tablas si no existen
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Usuario (
            usuario_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT UNIQUE,
            nombre TEXT,
            telefono TEXT,
            es_premium BOOLEAN DEFAULT 0
        )''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Recordatorio (
            recordatorio_id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            nombre_medicamento TEXT NOT NULL,
            dosis TEXT NOT NULL,
            frecuencia_horas INTEGER,
            hora_inicio TEXT,
            dosis_totales INTEGER,
            activo BOOLEAN DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id)
        )''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS DosisProgramada (
            dosis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            recordatorio_id INTEGER,
            hora_programada TEXT,
            tomada BOOLEAN DEFAULT 0,
            FOREIGN KEY (recordatorio_id) REFERENCES Recordatorio(recordatorio_id)
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS CuentaBancaria (
            cuenta_id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            numero_tarjeta TEXT NOT NULL,
            titular TEXT NOT NULL,
            fecha_vencimiento TEXT NOT NULL,
            cvv TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activa BOOLEAN DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id),
            UNIQUE(usuario_id, numero_tarjeta)
        )''')
        
        conn.commit()
        conn.close()

    @property
    def conn(self):
        """Obtiene o crea una conexión para el hilo actual"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_name)
            self._local.conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
        return self._local.conn

    @property
    def cursor(self):
        """Obtiene un cursor para la conexión del hilo actual"""
        return self.conn.cursor()

    # CRUD para Usuarios
    def add_usuario(self, chat_id, nombre=None, telefono=None):
        cursor = self.conn.cursor()
        # Verificar si el chat_id ya existe
        cursor.execute('SELECT COUNT(*) FROM Usuario WHERE chat_id = ?', (chat_id,))
        if cursor.fetchone()[0] > 0:
            # Si ya existe, podrías devolver un mensaje o actualizarlo
            return "Usuario ya registrado"
    
        # Si no existe, proceder a insertar el nuevo usuario
        cursor.execute('''
        INSERT INTO Usuario (chat_id, nombre, telefono) 
        VALUES (?, ?, ?)
        ''', (chat_id, nombre, telefono))
        self.conn.commit()
        return cursor.lastrowid


    # CRUD para Recordatorios
    def add_recordatorio(self, chat_id, medicamento, dosis, frecuencia, hora_inicio, total_dosis):
        """Versión simplificada que asume validación previa"""
        usuario_id = self.get_usuario_id(chat_id)
        cursor = self.conn.cursor()
    
        cursor.execute('''
        INSERT INTO Recordatorio (
            usuario_id, nombre_medicamento, dosis, frecuencia_horas,
            hora_inicio, dosis_totales
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (usuario_id, medicamento, dosis, frecuencia, hora_inicio, total_dosis))
    
        recordatorio_id = cursor.lastrowid
        self.conn.commit()
        return recordatorio_id

    def programar_dosis(self, recordatorio_id, hora_inicio, frecuencia, total_dosis):
        cursor = self.conn.cursor()
    
        try:
            # Validar que frecuencia sea un número
            try:
                frecuencia_num = int(frecuencia)
            except (ValueError, TypeError):
                raise ValueError("La frecuencia debe ser un número entero de horas")
        
            # Validar formato de hora
            if not re.match(r"^([01]?[0-9]|2[0-3]):([0-5][0-9])$", str(hora_inicio)):
                raise ValueError("Formato de hora inválido. Debe ser HH:MM")
            
            hora = datetime.strptime(str(hora_inicio), "%H:%M")
        
            for i in range(total_dosis):
                hora_dosis = hora.strftime("%H:%M")
                cursor.execute('''
                INSERT INTO DosisProgramada (recordatorio_id, hora_programada)
                VALUES (?, ?)
                ''', (recordatorio_id, hora_dosis))
                hora += timedelta(hours=frecuencia_num)  # Usar frecuencia_num que es integer
            
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Error al programar dosis: {str(e)}")

    def delete_dosis(self, dosis_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM DosisProgramada WHERE dosis_id = ?', (dosis_id,))
        self.conn.commit()

    def marcar_dosis_tomada(self, recordatorio_id):
        cursor = self.conn.cursor()
        # Obtener la siguiente dosis para este recordatorio
        cursor.execute('''
        SELECT dosis_id FROM DosisProgramada WHERE recordatorio_id = ? AND tomada = 0 LIMIT 1
        ''', (recordatorio_id,))
        dosis = cursor.fetchone()

        if dosis:
            dosis_id = dosis["dosis_id"]
            cursor.execute('''
            UPDATE DosisProgramada SET tomada = 1 WHERE dosis_id = ?
            ''', (dosis_id,))
            self.conn.commit()
            return True
        else:
            return False


    def get_dosis_restantes(self, recordatorio_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT COUNT(*) 
        FROM DosisProgramada 
        WHERE recordatorio_id = ? AND tomada = 0
        ''', (recordatorio_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_siguiente_dosis(self, recordatorio_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT hora_programada 
        FROM DosisProgramada 
        WHERE recordatorio_id = ? AND tomada = 0
        ORDER BY hora_programada 
        LIMIT 1
        ''', (recordatorio_id,))
        result = cursor.fetchone()
        return result[0] if result else None



    def get_recordatorios_activos(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT r.recordatorio_id, r.nombre_medicamento, r.dosis, 
               r.frecuencia_horas, r.hora_inicio, r.dosis_totales
        FROM Recordatorio r
        JOIN Usuario u ON r.usuario_id = u.usuario_id
        WHERE u.chat_id = ? AND r.activo = 1
        ''', (chat_id,))
        return cursor.fetchall()

    def delete_recordatorio(self, recordatorio_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM DosisProgramada WHERE recordatorio_id = ?', (recordatorio_id,))
        cursor.execute('DELETE FROM Recordatorio WHERE recordatorio_id = ?', (recordatorio_id,))
        self.conn.commit()

    def close(self):
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            del self._local.conn

    # Helper methods
    def get_usuario_id(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT usuario_id FROM Usuario WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def marcar_como_premium(self, chat_id):
        """Marca a un usuario como premium"""
        self.cursor.execute('''UPDATE Usuario SET es_premium = 1 WHERE chat_id = ?''', (chat_id,))
        self.conn.commit()

    # Métodos para Cuentas Bancarias
    def agregar_cuenta_bancaria(self, chat_id, numero_tarjeta, titular, fecha_vencimiento, cvv):
        """Añade una nueva cuenta bancaria para un usuario"""
        cursor = self.conn.cursor()
        usuario_id = self.get_usuario_id(chat_id)
        try:
            # Primero validamos los datos básicos
            if not all([numero_tarjeta, titular, fecha_vencimiento, cvv]):
                raise ValueError("Todos los campos son obligatorios")
        
            # Validar formato de fecha (MM/YY)
            if not re.match(r'^(0[1-9]|1[0-2])\/?([0-9]{2})$', fecha_vencimiento):
                raise ValueError("Formato de fecha inválido. Use MM/AA")
        
            # Validar CVV (3 o 4 dígitos)
            if not re.match(r'^[0-9]{3,4}$', cvv):
                raise ValueError("CVV debe tener 3 o 4 dígitos")
        
            # Limpiar número de tarjeta (eliminar espacios)
            numero_tarjeta_limpio = numero_tarjeta.replace(" ", "")
        
            # Validar número de tarjeta (solo dígitos, longitud válida)
            if not numero_tarjeta_limpio.isdigit() or len(numero_tarjeta_limpio) not in (15, 16):
                raise ValueError("Número de tarjeta inválido")
        
            cursor.execute('''
            INSERT INTO CuentaBancaria 
            (usuario_id, numero_tarjeta, titular, fecha_vencimiento, cvv)
            VALUES (?, ?, ?, ?, ?)
            ''', (usuario_id, numero_tarjeta_limpio, titular, fecha_vencimiento, cvv))
        
            self.conn.commit()
            return cursor.lastrowid
        
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            raise ValueError("Esta tarjeta ya está registrada para este usuario")
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Error al agregar cuenta bancaria: {str(e)}")

    def obtener_cuentas_activas(self, usuario_id):
        """Obtiene todas las cuentas bancarias activas de un usuario"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT cuenta_id, numero_tarjeta, titular, fecha_vencimiento
        FROM CuentaBancaria
        WHERE usuario_id = ? AND activa = 1
        ORDER BY fecha_registro DESC
        ''', (usuario_id,))
    
        return cursor.fetchall()

    def desactivar_cuenta(self, cuenta_id, usuario_id=None):
        """Desactiva una cuenta bancaria (borrado lógico)"""
        cursor = self.conn.cursor()
    
        try:
            if usuario_id:
                # Verificar que la cuenta pertenece al usuario
                cursor.execute('''
                UPDATE CuentaBancaria 
                SET activa = 0 
                WHERE cuenta_id = ? AND usuario_id = ?
                ''', (cuenta_id, usuario_id))
            else:
                cursor.execute('''
                UPDATE CuentaBancaria 
                SET activa = 0 
                WHERE cuenta_id = ?
                ''', (cuenta_id,))
            
            if cursor.rowcount == 0:
                raise ValueError("Cuenta no encontrada o no pertenece al usuario")
            
            self.conn.commit()
            return True
        
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Error al desactivar cuenta: {str(e)}")

    def obtener_ultima_cuenta_activa(self, usuario_id):
        """Obtiene la última cuenta activa de un usuario"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT cuenta_id, numero_tarjeta, titular, fecha_vencimiento
        FROM CuentaBancaria
        WHERE usuario_id = ? AND activa = 1
        ORDER BY fecha_registro DESC
        LIMIT 1
        ''', (usuario_id,))

    
    
        return cursor.fetchone()
        
    def es_usuario_premium(self, chat_id):
        """Verifica si un usuario tiene suscripción premium"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT es_premium FROM Usuario WHERE chat_id = ?',
            (chat_id,)
        )
        result = cursor.fetchone()
        return result is not None and result['es_premium'] == 1

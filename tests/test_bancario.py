from BBDD import DatabaseManager
import uuid
import sqlite3

def test_completo():
    print("\n=== INICIANDO PRUEBAS COMPLETAS ===")
    
    # 1. Configuración especial para pruebas
    db = DatabaseManager("file::memory:?cache=shared")  
    
    # 2. Crear tablas directamente usando la conexión del DatabaseManager
    cursor = db.conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Usuario (
        usuario_id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT UNIQUE,
        nombre TEXT,
        telefono TEXT
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
    
    db.conn.commit()
    
    # 3. Ahora usar la instancia db normalmente
    test_chat_id = f"test_{uuid.uuid4().hex[:6]}"
    
    try:
        # --- PRUEBA 1: Creación de usuario ---
        print("\n1. Probando creación de usuario...")
        usuario_id = db.add_usuario(
            chat_id=test_chat_id,
            nombre="Usuario Prueba",
            telefono="123456789"
        )
        print(f"✔ Usuario creado ID: {usuario_id}")
        
        # --- PRUEBA 2: Agregar cuenta bancaria ---
        print("\n2. Probando agregar cuenta bancaria...")
        cuenta_id = db.agregar_cuenta_bancaria(
            usuario_id=usuario_id,
            numero_tarjeta="4111111111111111",
            titular="TITULAR PRUEBA",
            fecha_vencimiento="12/25",
            cvv="123"
        )
        print(f"✔ Cuenta agregada ID: {cuenta_id}")
        
        # --- PRUEBA 3: Obtener cuentas activas ---
        print("\n3. Probando obtener cuentas activas...")
        cuentas = db.obtener_cuentas_activas(usuario_id)
        assert len(cuentas) == 1, f"Debería haber 1 cuenta, hay {len(cuentas)}"
        print(f"✔ Cuentas encontradas: {len(cuentas)}")
        
        print("\n=== PRUEBAS EXITOSAS ===")
        
    except Exception as e:
        print(f"\n❌ Error en pruebas: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_completo()

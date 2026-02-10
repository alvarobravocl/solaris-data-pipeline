import pandas as pd
import os
import shutil
from sqlalchemy import create_engine, text
from datetime import datetime

# --- IMPORTACIÓN DE CONFIGURACIÓN ---
# Aquí ocurre la magia: Importamos las variables desde src/config.py
# Si config.py no existe o falla, el script se detendrá aquí.
import config

# --- INICIALIZACIÓN DE RECURSOS ---
# Creamos el motor de base de datos usando la URL segura de config
try:
    print(
        f"🔌 Conectando a la base de datos: {config.DB_NAME} en {config.DB_HOST}...")
    engine = create_engine(config.DATABASE_URL)
    # Probamos la conexión inmediatamente (Fail Fast)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ Conexión a Base de Datos exitosa.")
except Exception as e:
    print(f"❌ Error Crítico: No se pudo conectar a la Base de Datos. Revisa tu .env")
    print(f"   Detalle: {e}")
    exit()  # Detenemos el script si no hay DB


def clean_numeric_field(value):
    """
    Limpia los errores típicos de entrada manual (Excel):
    - Convierte comas decimales a puntos.
    - Transforma textos de error ('Mantenimiento') a 0.0.
    - Maneja valores nulos.
    """
    if pd.isna(value):
        return 0.0

    str_val = str(value).strip()

    # Regla de Negocio: Si hay texto de falla/mantenimiento, la producción es 0
    if "Mantenimiento" in str_val or "Falla" in str_val or "Error" in str_val:
        return 0.0

    # Regla de Localización: Chile usa coma (,) para decimales
    if "," in str_val:
        str_val = str_val.replace(',', '.')

    try:
        return float(str_val)
    except ValueError:
        return 0.0


def process_file(filename):
    print(f"\n📄 Procesando archivo: {filename}...")

    # Construimos la ruta completa usando la variable de config
    file_path = os.path.join(config.INPUT_DIR, filename)

    # 1. EXTRACT
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"❌ Error leyendo el Excel {filename}: {e}")
        return

    # 2. TRANSFORM
    # 2.1 Renombrar columnas (Estandarización)
    column_mapping = {
        'Fecha': 'date',
        'ID_Parque': 'park_id',
        'Generacion_MWh': 'energy_generated_kwh',  # Ojo al cambio de unidad abajo
        'Irradiacion_Wm2': 'irradiation',
        'Comentarios_Operador': 'comments'
    }

    # Validamos que las columnas existan antes de renombrar
    available_cols = list(set(column_mapping.keys()).intersection(df.columns))
    if not available_cols:
        print(
            f"⚠️ El archivo {filename} no tiene las columnas esperadas. Saltando.")
        return

    df = df[available_cols].rename(columns=column_mapping)

    # 2.2 Limpieza de Datos (Data Quality)
    if 'energy_generated_kwh' in df.columns:
        df['energy_generated_kwh'] = df['energy_generated_kwh'].apply(
            clean_numeric_field)
        # Regla de Negocio: Convertir MWh a kWh (x1000)
        df['energy_generated_kwh'] = df['energy_generated_kwh'] * 1000

    if 'irradiation' in df.columns:
        df['irradiation'] = df['irradiation'].apply(clean_numeric_field)

    # 2.3 Formato de Fechas
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.date

    # 3. LOAD
    try:
        df.to_sql('production_logs', engine, if_exists='append', index=False)
        print(f"✅ {len(df)} registros insertados correctamente.")
    except Exception as e:
        print(f"❌ Error insertando en PostgreSQL: {e}")
        return  # No movemos el archivo si falló la carga

    # 4. ARCHIVE
    # Movemos el archivo a la carpeta de procesados para no duplicar carga
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"processed_{timestamp}_{filename}"

    # Usamos la ruta de destino desde config
    os.makedirs(config.PROCESSED_DIR, exist_ok=True)
    destination = os.path.join(config.PROCESSED_DIR, new_filename)

    try:
        shutil.move(file_path, destination)
        print(f"📦 Archivo archivado en: {destination}")
    except Exception as e:
        print(f"⚠️ Datos cargados, pero error al mover archivo: {e}")


def main():
    print("--- 🚀 Iniciando ETL Job: Solaris Atacama Fase 1 ---")

    # Verificación de Seguridad: ¿Existe el directorio de entrada?
    if not os.path.exists(config.INPUT_DIR):
        print(
            f"❌ Error: El directorio de entrada '{config.INPUT_DIR}' no existe.")
        print("   (Revisa tu archivo .env o tu docker-compose.yml)")
        return

    # Buscar archivos Excel (ignorando temporales de Windows que empiezan con ~$)
    files = [f for f in os.listdir(config.INPUT_DIR) if f.endswith(
        '.xlsx') and not f.startswith('~$')]

    if not files:
        print(f"ℹ️ No hay archivos nuevos en {config.INPUT_DIR}. Todo al día.")
        return

    print(f"📂 Se encontraron {len(files)} archivos para procesar.")
    for filename in files:
        process_file(filename)

    print("\n--- ✅ Proceso Finalizado ---")


if __name__ == "__main__":
    main()

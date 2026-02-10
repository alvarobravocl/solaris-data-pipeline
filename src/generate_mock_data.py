import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# Configuración
OUTPUT_PATH = "/app/data/input/produccion_abril_2026.xlsx"
PARK_ID = "SOL_CL_01"  # Sol del Desierto
DAYS_TO_GENERATE = 30
START_DATE = datetime(2026, 4, 1)


def generate_dirty_data():
    print(f"--- Iniciando Generación de Datos Sucios para {PARK_ID} ---")

    data = []

    for i in range(DAYS_TO_GENERATE):
        current_date = START_DATE + timedelta(days=i)

        # 1. Simular Irradiación (Variación aleatoria realista para el desierto)
        # En Atacama oscila entre 700 y 1100 W/m2 en horas punta
        irradiation = random.uniform(600, 1150)

        # 2. Simular Generación (Eficiencia ~18% + pérdidas)
        # Fórmula simple: Irradiación * Area ficticia * Eficiencia
        theoretical_gen = (irradiation * 5000 * 0.18) / 1000  # MWh aprox
        generation = theoretical_gen * \
            random.uniform(0.9, 1.0)  # Factor de suciedad

        # 3. Simular Horas de Operación
        hours = random.uniform(8.5, 12.0)

        # --- AQUI VIENE EL CAOS DE "DON PEDRO" ---

        # Escenario A: El día 5 hubo mantenimiento (Texto en columna numérica)
        if i == 5:
            generation = "Mantenimiento Preventivo"
            hours = 0
            comments = "Parque apagado por limpieza"

        # Escenario B: El día 12 y 25 usó coma decimal (Error de locale)
        elif i in [12, 25]:
            # Convertimos a string y cambiamos punto por coma
            generation = f"{generation:.2f}".replace('.', ',')
            irradiation = f"{irradiation:.2f}".replace('.', ',')
            comments = "Operacion normal"

        # Escenario C: El día 18 se le olvidó llenar la generación (NaN/Null)
        elif i == 18:
            generation = None
            comments = "Sin datos de medidor"

        # Escenario D: Día Normal
        else:
            comments = "Normal"

        # Guardamos la fila
        row = {
            'Fecha': current_date.strftime("%Y-%m-%d"),
            'ID_Parque': PARK_ID,
            'Generacion_MWh': generation,       # Columna Peligrosa 1
            'Irradiacion_Wm2': irradiation,     # Columna Peligrosa 2
            'Horas_Operacion': hours,
            'Comentarios_Operador': comments
        }
        data.append(row)

    # Crear DataFrame
    df = pd.DataFrame(data)

    # Guardar a Excel
    # Aseguramos que el directorio exista
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    df.to_excel(OUTPUT_PATH, index=False)
    print(f"✅ Archivo generado con éxito en: {OUTPUT_PATH}")
    print("   Contiene errores intencionales: 'Mantenimiento', comas decimales y vacíos.")


if __name__ == "__main__":
    generate_dirty_data()

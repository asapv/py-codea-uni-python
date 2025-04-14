import streamlit as st
import pandas as pd

def calculate_cutoff_grade(mining_cost, processing_cost, mineral_price, refining_cost, metallurgical_recovery):
    """Calcula la Ley de Corte usando la fórmula de Kenneth Lane."""
    recovery_decimal = metallurgical_recovery / 100
    denominator = (mineral_price - refining_cost) * recovery_decimal
    if denominator <= 0:
        st.error("El precio del mineral ajustado por refinación y recuperación debe ser mayor que 0.")
        return None
    return ((mining_cost + processing_cost) / denominator) * 100

def decide_block_action(block_grade, cutoff_grade, stock_threshold):
    """Decide si un bloque debe ser procesado, enviado a stock o descartado."""
    stock_limit = cutoff_grade * stock_threshold
    if block_grade >= cutoff_grade:
        return "Procesar"
    elif block_grade >= stock_limit:
        return "Enviar a stock"
    else:
        return "Descartar"

# Configuración de la página
st.set_page_config(page_title="Calculadora de Ley de Corte", layout="wide")
st.title("Calculadora de Ley de Corte")

# Crear columnas para organizar la interfaz
col1, col2 = st.columns([1, 1])

# Parámetros en la primera columna
with col1:
    st.subheader("Datos de Entrada")
    with st.form("input_form"):
        mining_cost = st.number_input("Costo de Minado ($/tonelada):", min_value=0.01, format="%.2f")
        processing_cost = st.number_input("Costo de Procesamiento ($/tonelada):", min_value=0.01, format="%.2f")
        mineral_price = st.number_input("Precio del Mineral ($/tonelada):", min_value=0.01, format="%.2f")
        refining_cost = st.number_input("Costo de Refinación ($/tonelada):", min_value=0.0, max_value=float(mineral_price), format="%.2f")
        recovery = st.number_input("Recuperación Metalúrgica (%):", min_value=0.1, max_value=100.0, format="%.1f")
        stock_threshold = st.number_input("Umbral para Stock (0-1):", min_value=0.0, max_value=1.0, format="%.2f")
        
        # Campo para agregar bloques
        block_grade_input = st.text_input("Leyes de Bloques (%):", 
                                         help="Ingresa las leyes separadas por comas (e.j. '1.2, 3.4, 5.6')")
        
        submitted = st.form_submit_button("Calcular")

# Segunda columna para resultados
with col2:
    st.subheader("Resultados")
    
    if submitted:
        # Calcular la ley de corte
        cutoff_grade = calculate_cutoff_grade(mining_cost, processing_cost, mineral_price, refining_cost, recovery)
        
        if cutoff_grade is not None:
            st.success(f"**Ley de Corte: {cutoff_grade:.2f}%**")
            
            # Procesar los bloques
            try:
                if block_grade_input:
                    block_grades = [float(grade.strip()) for grade in block_grade_input.split(',')]
                    
                    # Crear dataframe para resultados
                    results = []
                    for grade in block_grades:
                        action = decide_block_action(grade, cutoff_grade, stock_threshold)
                        results.append({"Ley del Bloque (%)": f"{grade:.2f}", "Acción": action})
                    
                    # Mostrar tabla de resultados
                    st.subheader("Análisis de Bloques")
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
                    
                    # Mostrar resumen
                    processed = sum(1 for r in results if r["Acción"] == "Procesar")
                    stocked = sum(1 for r in results if r["Acción"] == "Enviar a stock")
                    discarded = sum(1 for r in results if r["Acción"] == "Descartar")
                    
                    st.subheader("Resumen")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Procesados", processed)
                    col2.metric("Enviados a Stock", stocked)
                    col3.metric("Descartados", discarded)
                    
            except ValueError:
                st.error("Formato de leyes incorrecto. Usa números separados por comas.")

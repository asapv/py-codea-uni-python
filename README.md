# Calculadora de Ley de Corte Minera

Esta aplicación web permite calcular la Ley de Corte utilizando el método de Kenneth Lane, una herramienta esencial para la planificación y evaluación de proyectos mineros.

## Funcionalidades

- Cálculo de Ley de Corte basado en parámetros económicos y metalúrgicos
- Evaluación de bloques mineros individuales
- Clasificación de bloques en categorías: Procesar, Enviar a stock, o Descartar
  
## Cómo usar la aplicación

1. Ingresa los parámetros económicos:
   - Costo de Minado ($/tonelada)
   - Costo de Procesamiento ($/tonelada)
   - Precio del Mineral ($/tonelada)
   - Costo de Refinación ($/tonelada)
   - Recuperación Metalúrgica (%)
   - Umbral para Stock (valor entre 0 y 1)

2. Ingresa las leyes de los bloques a evaluar, separadas por comas (Ej: 1.2, 3.4, 5.6)
3. Haz clic en "Calcular" para obtener los resultados

## Fórmula de cálculo

La aplicación utiliza la siguiente fórmula para la Ley de Corte:

Ley de Corte = ((Cm + Cp) / ((Pm - Cr) * RM)) * 100

Donde:
- Cm = Costo de minado por tonelada
- Cp = Costo de procesamiento por tonelada
- Pm = Precio del mineral por tonelada
- Cr = Costo de refinación por tonelada
- RM = Recuperación metalúrgica (expresada como decimal)

## Despliegue

Esta aplicación está desplegada usando Streamlit Cloud. Puedes acceder a la versión en línea en https://py-codea-uni-python-paulo-verde.streamlit.app/

Proyecto-final

1. Creación de ambiente colaborativo (Christian)
2. Creación en la rama principal del app.py
3. Importación de librerías básicas : pandas, numpy, matplotlib
4. Cargar dataset


Objetivo

Tipificación de la variabilidad de los factores de ocupación del vuelo con mayor demanda  en la ruta MED BOG durante el periodo julio 2024 a junio 2025

Justificación


Proceso
Elaboración de código ejecutable en Visual Studio (Jorge)

    Cargar librerías: ok
    Cargar datos: ok
    Verificación de datos nulos: ok
    Ajustar tipos de datos: ok  
    Hacer función con tabla de frecuencias: ok      
    Tipificar días : en proceso
        Asignación básica por día de la semana
        Establecer criterios
            tipo 0 : primer dia laboral
            tipo 1 : día laboral: ok
            tipo 2 : último día laboral
            tipo 3 : día no laboral : ok                
        Ajuste por festivos
    Tipificar frecuencias del LF% para todo el año sin filtrar
    Agrupar vuelos por factor de ocupación en orden ascendente
    Crear los grupos por k medias
    Filtrar vuelo para objetivo del trabajo: ok
    Crear base total de comportamientos = permutación[tipo_día, mes]
    Tipificar frecuencias de los comportamientos
    Establecer base de comparación entre comportamientos y global
    Escoger los similares





Ajuste del código para ejecución en Streamlit (Christian)

Elaboración del informe (Juan Pablo)

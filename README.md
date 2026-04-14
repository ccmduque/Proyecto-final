Proyecto-final

1. Creación de ambiente colaborativo (Christian)
2. Creación en la rama principal del app.py
3. Importación de librerías básicas : pandas, numpy, matplotlib
4. Cargar dataset


Objetivo

Segmentación y tipificación de la variabilidad del factor de ocupación (%LF) de la ruta MDE - BOG durante el periodo julio 2024 a junio 2025

Justificación


Proceso
Elaboración de código ejecutable en Visual Studio (Jorge)

    Cargar librerías: ok
    Cargar datos: ok
    Verificación de datos nulos: ok
    Ajustar tipos de datos: ok  
    Hacer función con tabla de frecuencias: ok      
    Tipificar días : en proceso
        Asignación básica por día de la semana: ok
        Establecer criterios : ok
            tipo 0 : primer dia laboral: ok
            tipo 1 : día laboral: ok
            tipo 2 : último día laboral: ok
            tipo 3 : día no laboral : ok                
        Ajuste por festivos : ok
    Elaborar tabla de frecuencias del LF% para todo el año sin filtrar: ok
    Agrupar por K media los LF% de todo el año sin filtrar : : ok
        Obtener centroides por partición binaria: ok
        Obtener centroides finales de k medias: ok
    Agrupar vuelos por factor de ocupación en orden ascendente
    Clasificación ABC por partición binaria
    Filtrar vuelo para objetivo del trabajo (vuelos AAA) : ok (adaptarlo)
    Crear base total de comportamientos = permutación[tipo_día, mes]
    Filtrar %LF por AAA y permutación
    Crear vectores (min, q1,q2,q3,max)
    Tipificar frecuencias de los comportamientos
    Establecer base de comparación entre comportamientos y global
    Escoger los similares





Ajuste del código para ejecución en Streamlit (Christian)

Elaboración del informe (Juan Pablo)

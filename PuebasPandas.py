# Ensayo de las funcionalidades de la 
# librería pandas con el archivo datos del proyecto

#== importar librerías

import pandas as pd
import numpy as np
import matplotlib as plt



#== Carga de datos

ruta='https://github.com/ccmduque/Proyecto-final/raw/refs/heads/main/Salidas%20MED%20%20BOG%202024%2007%20a%202025%2006.csv'
df=pd.read_csv(ruta, encoding='latin1', sep=';')

# Verificación de resultados cargados
print(df) # primeros y últimos cinco registros
print(df.info()) # Información del DataFrame
print(df.describe()) # Estadigrafía de campos numéricos

# Ajuste de tipo de datos

df['%LF DEP']=df['%LF DEP'].str[:-1].astype(float) # Factor de carga como float
df['Vuelo Salida']=df['Vuelo Salida'].astype(str).str[:-2] # Vuelo salida como string
df['Fecha Salida']=pd.to_datetime(df['Fecha Salida'],format='%d/%m/%y') # Fecha Salida como fecha
df['Tipo dia']=np.where(np.is_busday(df['Fecha Salida'].values.astype('datetime64[D]')),
                     1,3
)

# Resultado del ajuste de datos

print(df.head())
print(df.info())
print(df.describe())

# Selección del vuelo con mayor porcentaje de ocupación (%LF)

vuelo_top=df.groupby('Vuelo Salida')['%LF DEP'].sum().idxmax() # vuelo con mayor ocupación
df_vuelo_top=df[df['Vuelo Salida']==vuelo_top] # variable df con datos del vuelo top
df_vuelo_top['%LF DEP']=df_vuelo_top['%LF DEP']*0.01 # Conversión de % a float
df_vuelo_top['Pax']=(df_vuelo_top['%LF DEP']*180).round(0).astype(int) # Número de pasajeros (K=180 pax)


print(df_vuelo_top.head(20))
print(df_vuelo_top.info())
print(df_vuelo_top.describe())

print(df_vuelo_top['Fecha Salida'].dtype)


# === CREACIÓN DE UNA FUNCIÓN QUE GENERA TABLA DE FRECUENCIAS ===

# Genera la tabla de frecuencias acumuladas de un campo de un DataFrame,
# ordenada de forma ascendente por valor.

# Columnas resultante:
#   n_i  → frecuencia absoluta
#   f_i  → frecuencia relativa  (n_i / N)
#   N_i  → frecuencia absoluta acumulada
#   F_i  → frecuencia relativa acumulada

def tabla_frec(df:pd.DataFrame,campo:str)->pd.DataFrame:

    # 1. Frecuencia absoluta en orden ascendente

    frec=  (df[campo] #df es la variable DataFrame que se pasa como parámetro a la función
        .value_counts() # Cuenta la frecuencia de valores únicos
        .sort_index() # Orden descendente
        .reset_index() # El índice se vuelve una columna
    )
    
    #frec.colums=[campo,'n_i'] # Renombra el campo como n_i

    N = frec[campo].sum() # total eventos

    # 2. Frecuencia relativa en orden ascendente

    frec["f_i"]=frec[campo]/N

    # 3. Frecuencia absoluta acumulada

    frec["N_i"]=frec[campo].cumsum()

    # 4. Frecuencia relativa acumulada

    frec["F_i"]=frec["f_i"].cumsum()

    if frec["F_i"].iloc[-1]!=1:
        frec["F_i"].iloc[-1]=1
    
    return frec.set_index(campo)

#=== Fin de la función

df_lf_general=tabla_frec(df,'%LF DEP')
print(df_lf_general)
print(df_lf_general['count'].sum())

plt.plot(df_lf_general['%LF DEP'],df_lf_general['F_i'])
plt.title("Distribución de Probabilidad del Factor de Carga ")
plt.xlabel('%LF DEP')
plt.ylabel('F_i')









 


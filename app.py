# Segmentación y tipificación de la variabilidad del factor de ocupación (%LF)
#  de la ruta MDE - BOG durante el periodo julio 2024 a junio 2025

# ===== Importación de  librerías =====

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import seaborn as sns
from datetime import timedelta, date
from sklearn.cluster import KMeans

# ===== Fin importación de librerías =====

# ===== FUNCIÓN QUE GENERA TABLA DE FRECUENCIAS =====

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
    
    return frec

# ===== Fin de la función tabla de frecuencias =====

# ===== Carga de datos =====

ruta='https://github.com/ccmduque/Proyecto-final/raw/refs/heads/main/Salidas%20MED%20%20BOG%202024%2007%20a%202025%2006.csv'
df=pd.read_csv(ruta, encoding='latin1', sep=';')

# ===== Fin carga de datos =====

# =====Depuración y ajuste de datos =====

df['%LF DEP']=df['%LF DEP'].str[:-1].astype(float) # Factor de carga como float
df['Vuelo Salida']=df['Vuelo Salida'].astype(str).str[:-2] # Vuelo salida como string
df['Fecha Salida']=pd.to_datetime(df['Fecha Salida'],format='%d/%m/%y') # Fecha Salida como fecha
df=df.dropna(subset=['Fecha Salida'])

# ===== Estadigrafía =====

# Agrupación
df_por_vuelos=df.groupby('Vuelo Salida')['%LF DEP']
df_por_mes=df.groupby('Mes')['%LF DEP']
df_por_dia=df.groupby('Dia Dep')['%LF DEP']

# Frecuencias acumuladas (sin agrupar)
df_lf_general=tabla_frec(df,'%LF DEP')

# ===== Fin Estadigrafía =====

# ===== Segmentación =====

# 1. Obtención de centroides iniciales por partición binaria

df_vuelos_acum=df.groupby('Vuelo Salida')['%LF DEP'].sum().sort_values().reset_index()
x=df_vuelos_acum[['%LF DEP']]


c_total=x.mean()
mitad_inf=x[x<c_total]
mitad_sup=x[x>=c_total]

c1=mitad_inf.mean()
c2=mitad_sup.mean()

# Definición de cuatro tramos

tramos=[x[(x>=x.min())&(x<c1)],
        x[(x>=c1)&(x<c_total)],
        x[(x>=c_total)&(x<c2)],
        x[(x>=c2)&(x<=x.max())]        
]

# Partición de la sección de mayor varianza

# Varianzas

varianzas=[s.var() for s in tramos]
idx_max=np.argmax(varianzas)
tramo_a_partir=tramos[idx_max]

# Bisección tramo con mayor varianza

c_nuevo=tramo_a_partir.mean()
tramo_inf=tramo_a_partir[tramo_a_partir<c_nuevo]
tramo_sup=tramo_a_partir[tramo_a_partir>=c_nuevo]

# Reemplazar tramo mayor varianza por los dos subtramos

tramos_finales=tramos.copy() # copia tramos
tramos_finales.pop(idx_max) # borra el tramo de mayor varianza
tramos_finales.insert(idx_max,tramo_inf) # inserta tramo inferior
tramos_finales.insert(idx_max+1,tramo_sup) # inserta tramo superior

# Centroides de cada tramo final
centroides_iniciales=np.array([s.mean() for s in tramos_finales]).reshape(-1,1)
print("centroides iniciales: \n",centroides_iniciales)

# 2. KMeans con centroides iniciales

kmeans=KMeans(n_clusters=5,
              init=centroides_iniciales,
              n_init=10,
              random_state=42
)
kmeans.fit(x)

# 3. Manejo de tramos resultantes de la segmentación

x['cluster']=kmeans.labels_
n_cluster=kmeans.n_clusters

# Ordenar clusters por su centroide
orden = np.argsort(kmeans.cluster_centers_.flatten())

# Calcular min y max de cada cluster en orden ascendente
limites = []
for i in range(len(orden) - 1):
    cluster_actual  = orden[i]
    cluster_siguiente = orden[i + 1]
    
    max_actual    = x['%LF DEP'][x['cluster'] == cluster_actual].max()
    min_siguiente = x['%LF DEP'][x['cluster'] == cluster_siguiente].min()
    
    limites.append((max_actual + min_siguiente) / 2)

# Construir bins
bins = np.concatenate([
    [x['%LF DEP'].min()],
    limites,
    [x['%LF DEP'].max()]
])

# Crear campo categórico

labels_posibles = ['C', 'B', 'A', 'AA', 'AAA']  # de menor a mayor
labels=labels_posibles[:kmeans.n_clusters]
print("long de labels: ",len(labels))
df_vuelos_acum['categoria'] = pd.cut(
    df_vuelos_acum['%LF DEP'],
    bins=bins,
    labels=labels,
    include_lowest=True
)

# 4. Imputación de categorías a df original (df)

df=df.merge(df_vuelos_acum[['Vuelo Salida','categoria']],
            on='Vuelo Salida',
            how='left'
)
df['categoria']=df['categoria'].astype(str)

# 5. Frecuencias acumuladas por categoría

frec_acum_categ = {}
for cat,grupo in df.groupby('categoria',observed=True):
    valores=grupo['%LF DEP'].sort_values()
    frec_acum_categ[cat]=pd.DataFrame({
        '%LF DEP':valores.values,
        'frec_acum':np.arange(1,len(valores)+1)/len(valores)
})
# ===== Fin segmentación =====

# ===== Tipificación de la variabilidad =====
resumen_cat=df.groupby('categoria')['%LF DEP'].describe().reindex(['C','B','A','AA','AAA'])

# ===== Fin de la tipificación de la variabilidad =====

# ===== CONFIGURACIÓN DE LA APLICACIÓN STREAMLIT =====

# 1. Configuración de la página

st.set_page_config(
    page_title='Ruta MED - BOG',
    layout='centered',
    initial_sidebar_state='collapsed'
)
# 2. Ancho del contenedor
st.markdown(
  '''
<style>
    .block-container{
        max-width: 1200px;
    }
</style>
''',
unsafe_allow_html=True 
)

# 3. Paleta de colores

paleta_barras=px.colors.qualitative.Antique

# ===== FIN DE LA CONFIGURACIÓN DE LA APLICACIÓN STREAMLIT =====

# ===== VISUALIZACIÓN =====
# 1. Agrupación

# 2. Segmentación

# 3. Tipificación

# 4. Pronóstico


# ===== FIN DE VISUALIZACIÓN =====

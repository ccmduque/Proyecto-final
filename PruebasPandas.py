# Ensayo de las funcionalidades de la 
# librería pandas con el archivo datos del proyecto

#== importar librerías

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import seaborn as sns
from datetime import timedelta, date
from sklearn.cluster import KMeans

# === FUNCIÓN QUE GENERA TABLA DE FRECUENCIAS ===

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

# === Fin de la función tabla de frecuencias

# === FUNCIÓN QUE GENERA FESTIVOS EN COLOMBIA ===

def tipo_dia(fecha):
    fecha_date = fecha.date() if isinstance(fecha, pd.Timestamp) else pd.Timestamp(fecha).date()
    
    if fecha_date.weekday() >= 5 or fecha_date in co_festivos:
        return 3
    
    lunes = fecha_date - timedelta(days=fecha_date.weekday())
    dias_semana = [lunes + timedelta(days=i) for i in range(5)]
    laborables = [d for d in dias_semana if d.weekday() < 5 and d not in co_festivos]
    
    if len(laborables) == 0:
        return 3
    if fecha_date == laborables[0]:
        return 0
    elif fecha_date == laborables[-1]:
        return 2
    else:
        return 1


# === Fin de la función que genera festivos en Colombia



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
df=df.dropna(subset=['Fecha Salida'])

# Ajuste de tipo de día a calendario laboral de Colombia
    # tipo 0 : primer dia laboral
    # tipo 1 : día laboral: ok
    # tipo 2 : último día laboral
    # tipo 3 : día no laboral : ok

co_festivos = {
    # 2024
    date(2024, 7, 1), date(2024, 7, 4), date(2024, 7, 20),
    date(2024, 8, 7), date(2024, 8, 19), date(2024, 10, 14), date(2024, 11, 4),
    date(2024, 11, 11), date(2024, 12, 8), date(2024, 12, 25),
    # 2025
    date(2025, 1, 1), date(2025, 1, 6), date(2025, 3, 24), date(2025, 4, 17),
    date(2025, 4, 18), date(2025, 5, 1), date(2025, 6, 2), date(2025, 6, 23),
    date(2025, 6, 30),
}

df['Tipo dia']=df['Fecha Salida'].apply(tipo_dia)

# Resultado del ajuste de datos

print(df.head())
print(df.info())
print(df.describe())

#df.to_csv('datos depurados.csv')

# Selección del vuelo con mayor porcentaje de ocupación (%LF)

vuelo_top=df.groupby('Vuelo Salida')['%LF DEP'].sum().idxmax() # vuelo con mayor ocupación
df_vuelo_top=df[df['Vuelo Salida']==vuelo_top] # variable df con datos del vuelo top
df_vuelo_top['%LF DEP']=df_vuelo_top['%LF DEP']*0.01 # Conversión de % a float
df_vuelo_top['Pax']=(df_vuelo_top['%LF DEP']*180).round(0).astype(int) # Número de pasajeros (K=180 pax)

print(df_vuelo_top)
print(df_vuelo_top.info())
print(df_vuelo_top.describe())

df_vuelos=df.groupby('Vuelo Salida')['%LF DEP'].sum().sort_values().reset_index()

print('''
  ========== Agrupados por vuelos ==========    
'''    
)
print(df_vuelos)
print(df_vuelos.info())
print(df_vuelos.describe())

df_lf_general=tabla_frec(df,'%LF DEP')
print(df_lf_general)
print(df_lf_general['count'].sum())

print(df_lf_general.columns)
plt.plot(df_lf_general['%LF DEP'],df_lf_general['F_i'])
plt.title("Distribución de Probabilidad del Factor de Ocupación ")
plt.xlabel('%LF DEP')
plt.ylabel('F_i')
plt.savefig('FDP.png',dpi=300)

# Clasificación ABC de vuelos según LF% por K medias 

# Obtención de centroides iniciales por partición binaria

x=df_vuelos[['%LF DEP']]


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

# KMeans con centroides iniciales

kmeans=KMeans(n_clusters=5,
              init=centroides_iniciales,
              n_init=10,
              random_state=42
)

kmeans.fit(x)

print(kmeans.labels_)
print(kmeans.cluster_centers_)
print(kmeans.inertia_)
print(kmeans.n_iter_)

print('=========\n')

x['cluster']=kmeans.labels_
resumen=x.groupby('cluster')['%LF DEP'].describe()
print(resumen)
n_cluster=kmeans.n_clusters
print(n_cluster)

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

print("bins :",bins)
print("len de bins :",len(bins))


# Crear campo categórico

labels_posibles = ['C', 'B', 'A', 'AA', 'AAA']  # de menor a mayor
labels=labels_posibles[:kmeans.n_clusters]
print("long de labels: ",len(labels))
df_vuelos['categoria'] = pd.cut(
    df_vuelos['%LF DEP'],
    bins=bins,
    labels=labels,
    include_lowest=True
)

print('=== clasificacion ABC de los vuelos ===')
print(df_vuelos)

df=df.merge(df_vuelos[['Vuelo Salida','categoria']],
            on='Vuelo Salida',
            how='left'
)

print('===== Categorías datos originales =====')
print(df)

# Agrupación por categorías

df['categoria']=df['categoria'].astype(str)

frec_acum_categ = {}
for cat,grupo in df.groupby('categoria',observed=True):
    valores=grupo['%LF DEP'].sort_values()
    frec_acum_categ[cat]=pd.DataFrame({
        '%LF DEP':valores.values,
        'frec_acum':np.arange(1,len(valores)+1)/len(valores)
})

print(df.columns.tolist())   # confirmar nombres de campos
print(df['categoria'].dtype) # confirmar que existe y su tipo
print(df['categoria'].unique()) # ver qué valores tiene

print("Negativos:", (df['%LF DEP'] < 0).sum())

# ===== Grafica violín por categoría =====

# Reconstruir dataframe largo desde el diccionario
df_violin = pd.concat(
    [df.assign(categoria=cat) for cat, df in frec_acum_categ.items()],
    ignore_index=True
)

# Violinplot
plt.close('all')

# Crear figura con dos elementos

ax=sns.violinplot(x='categoria', y='%LF DEP', data=df_violin, order=['C','B','A','AA','AAA'])

ax.axhline(df['%LF DEP'].mean(),   color='black', linewidth=2, 
           linestyle='--')
ax.axhline(df['%LF DEP'].median(), color='red',   linewidth=2, 
           linestyle=':')

# Crear handles manualmente
handle_media   = mlines.Line2D([], [], color='black', linewidth=2, 
                                linestyle='--', label='Media general')
handle_mediana = mlines.Line2D([], [], color='red',   linewidth=2, 
                                linestyle=':',  label='Mediana general')

plt.legend(handles=[handle_media, handle_mediana])
plt.title('Distribución de %LF DEP por categoría')
plt.xlabel('Categoría')
plt.ylabel('% LF DEP')
plt.ylim(0, df['%LF DEP'].max() + 15)
plt.savefig('FDP categorías.png',dpi=300,bbox_inches='tight')
plt.close('all')

# ===== Histograma por segmentos =====

plt.close('all')
orden_hist = ['C', 'B', 'A', 'AA', 'AAA']

# Frecuencia relativa de cada segmento
total=len(df)
frecuencias=[len(df[df['categoria']==cat])/total for cat in orden_hist]

# Calcular el ancho de cada barra según su rango
anchos=[bins[i+1]-bins[i] for i in range(len(orden_hist))]

# Centros de cada rango
centros = [(bins[i] + bins[i+1]) / 2 for i in range(len(orden_hist))]

plt.bar(centros, frecuencias, width=anchos, 
        edgecolor='black', alpha=0.7, align='center')

# Etiquetas de segmento sobre cada barra
for i, cat in enumerate(orden_hist):
    plt.text(centros[i], frecuencias[i] + 0.005, cat, 
             ha='center', fontsize=10)

plt.title('Distribución por segmento')
plt.xlabel('%LF DEP')
plt.ylabel('Frecuencia relativa')
plt.savefig('distribucion_segmentos.png', dpi=300, bbox_inches='tight')
plt.close('all')


# ===== Gráfica de frecuencias acumuladas =====

for cat in ['C','B','A','AA','AAA']:
    df_cat=frec_acum_categ[cat]
    plt.plot(df_cat['%LF DEP'], df_cat['frec_acum'], label=cat)

# Agregar la curva general
plt.plot(df_lf_general['%LF DEP'], df_lf_general['F_i'], 
         label='General', 
         color='black', 
         linewidth=2, 
         linestyle='--')  # línea punteada para diferenciarla

plt.title('Frecuencia acumulada por categoría')
plt.xlabel('%LF DEP')
plt.ylabel('Probabilidad acumulada')
plt.legend()
plt.savefig('frec_acum_categorias.png', dpi=300, bbox_inches='tight')
plt.close('all')






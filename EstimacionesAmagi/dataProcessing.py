try:
    import pandas as pd
except ImportError:
    raise ImportError("Please install pandas library using 'pip install pandas'")
import json
from unicodedata import normalize, combining

columnasParaEstimaciones = [
    'Entidad',
    'Tipo',
    'Categoría',
    'Fecha de Apertura',
    # 'Asignado a: - Grupo de Tecnicos',
    'Urgencia',
    'Impacto',
    'Prioridad',   
    'Estadísticas - Tiempo de solución'
]

casosDatosMalEscritos = {
    "Aplicaciones de Servidores": "Aplicaciones de Servidor",
    "Impresoras y escaneres": "Impresoras y Escaner",
    "Manejo de Alertas de Firewalls / Switches / Routers 7/24": "Manejo de Alertas de Firewalls / Switches / Routers",
}

sectores = [
    "Financiero",
    "Retail",
    "Manufactura",
    "Servicios",
    "Gobierno",
    "Energia",
    "Tecnologia",
]

sectoresClientes = {
    "Banplus Venezuela": "Financiero",
    "AMAGI": "Servicios",
    "CAVESPA": "Servicios",
    "Banplus International": "Financiero",
    "IUMO": "Servicios",
    "WOKI": "Servicios",
    "Grupo Austral": "Manufactura",
}

areasQueNoAplican = [
    'Infraestructura Banplus',
    'Infra-Electricidad',
    'Infra-Logistica',
    'Desarrollo de Aplicaciones'
]

testPath = 'CSVPruebaSinCeros.csv'
CLIENT_DATA_PATH = 'DataEstimaciones.csv'
VARIABLES_DE_SERVICIO_PATH = 'CSVVariablesDeServicio.csv'
COST_RATE_PATH = 'CSVCostRates.csv'
TIEMPOS_PERFILES_SETUP_PATH = 'CSVTiemposYPerfilesSetup.csv'

def setDataPath(path):
    DATA_PATH = path

def casoHoras(x):
    if 'horas' in x:
        if 'días' in x:
            return x[2]
        else:
            return x[0]
    else:
        return 0
    
def casoMinutos(x):
    if 'minutos' in x:
        if 'horas' in x:
            return x[2]
        elif 'días' in x:
            return x[4]
        else:
            return x[0]
    else:
        return 0

def writeToJsonFile(data, filePath):
    with open(filePath, "w") as outfile: 
        json.dump(data, outfile, indent = 4)

def remove_accents(input_str):
    nfkd_form = normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not combining(c)])

def readData(dataPath):
    # TODO: Agregar la opcion de leer un excel directamente en vez de csv
    if dataPath.endswith('.csv'):
        return pd.read_csv(dataPath, encoding='utf-8-sig')
    else:
        print('Error: El archivo debe ser .csv')
        return None

def clientDataPreProcessing(csvFilePath):
# TODO: sera que elimino las filas que tienen 0 en el tiempo total? Quizas solo las uso para comtar el numero de ocurrencias de cada sub-categoria
    # Read the data from the csv file
    data = readData(csvFilePath)

    # Select the columns for the estimations
    data = data[columnasParaEstimaciones]

    # Remove the rows with empty values
    data = data.dropna()

    # Entidad viene en formato "GIA > Cliente > Area", separar en Cliente y Area
    data['Cliente'] = data['Entidad'].apply(lambda x: x.split('>')[1].strip())
    data['Area'] = data['Entidad'].apply(lambda x: x.split('>')[2].strip())

    # Eliminar la columna Entidad
    data.drop('Entidad', axis=1, inplace=True)

    # En la columna Area, algunos campos tienen (texto) al final, eliminarlo
    data['Area'] = data['Area'].apply(lambda x: x.split('(')[0].strip())

    # Eliminar las filas que no aplican
    data = data[~data['Area'].isin(areasQueNoAplican)]

    # Categoria viene en formato "Categoria > Subcategoria > Otro", algunos no tienen " > Otro" y algunos no tienen "> Subcategoria", separar en Categoria y Subcategoria
    data['Categoria'] = data['Categoría'].apply(lambda x: x.split('>')[0].strip())
    data['Sub-Categoria'] = data['Categoría'].apply(lambda x: x.split('>')[1].strip() if len(x.split('>')) > 1 else '')

    # Cambiar los casos en los que los datos estan mal escritos
    for caso in casosDatosMalEscritos:
        data['Sub-Categoria'] = data['Sub-Categoria'].apply(lambda x: casosDatosMalEscritos[caso] if x == caso else x)

    # Eliminar la columna Categoría
    data.drop('Categoría', axis=1, inplace=True)

    # Eliminar filas que no tienen Subcategoria
    data = data[data['Sub-Categoria'] != '']

    # Cambiar formato de fecha de apertura a mes y año
    data['Fecha de Apertura'] = pd.to_datetime(data['Fecha de Apertura'])
    data['Fecha de Apertura'] = data['Fecha de Apertura'].apply(lambda x: x.strftime('%Y-%m'))

    # Agregar columnas de mes y año
    data['Año'] = data['Fecha de Apertura'].apply(lambda x: x.split('-')[0])
    data['Mes'] = data['Fecha de Apertura'].apply(lambda x: x.split('-')[1])
    
    # Estadisticas - Tiempo de solucion puede venir en varios formatos, 'X dias Y horas Z minutos' o 'X horas Y minutos' o 'X minutos' o 'X minuto' o 'X segundos', separar en dias, horas y minutos
    data['Estadísticas - Tiempo de solución'] = data['Estadísticas - Tiempo de solución'].apply(lambda x: x.split(' '))
    data['Dias'] = data['Estadísticas - Tiempo de solución'].apply(lambda x: x[0] if 'días' in x else 0)
    data['Horas'] = data['Estadísticas - Tiempo de solución'].apply(lambda x: casoHoras(x))
    data['Minutos'] = data['Estadísticas - Tiempo de solución'].apply(lambda x: casoMinutos(x))

    # Eliminar la columna Estadísticas - Tiempo de solución y agregar columna de tiempo total en horas
    data.drop('Estadísticas - Tiempo de solución', axis=1, inplace=True)
    data['Tiempo Total'] = round(data['Dias'].astype(int) * 24 + data['Horas'].astype(int) + data['Minutos'].astype(int) / 60, 2)

    # Eliminar las columnas Dias, Horas y Minutos
    data.drop('Dias', axis=1, inplace=True)
    data.drop('Horas', axis=1, inplace=True)
    data.drop('Minutos', axis=1, inplace=True)

    # Agregar columna de sector
    data['Sector'] = data['Cliente'].apply(lambda x: sectoresClientes[x])

    # Cambiar todos los acentos a caracteres normales
    for column in data.columns:
        data[column] = data[column].apply(lambda x: remove_accents(x) if type(x) == str else x)


    return data

def variablesDeServicioPreprocessing(csvFilePath):
    # La data la voy a poner en un json con la siguiente estructura:
    # {Area: {Setup: {Variable: Esfuerzo}}, {Ongoing: {Variable: Esfuerzo}}}
    #


    # Read the data from the csv file
    data = readData(csvFilePath)

    # Agarro las areas 
    areas = data.columns[0::2]
    esfuerzoAreas = data.columns[1::2]

    # Separo el dataframe inicial por areas
    dataPorArea = {}
    for i in range(len(areas)):
        dataPorArea[areas[i]] = data[[areas[i], esfuerzoAreas[i]]]

    # TODO: Aqui hay un peo

    # Elimino las filas que tienen NaN
    for area in dataPorArea:
        dataPorArea[area] = dataPorArea[area].copy().dropna(inplace=False)

    # Cambio el nombre de las columnas
    for area in dataPorArea:
        dataPorArea[area].columns = ['Variable', 'Esfuerzo'] 

    # Cambio el formato de la columna Esfuerzo a float
    for area in dataPorArea:
        dataPorArea[area]['Esfuerzo'] = dataPorArea[area]['Esfuerzo'].apply(lambda x: float(x))

    new_dataPorArea = {}

    for area in dataPorArea:
        setup_data = dataPorArea[area][dataPorArea[area]['Variable'].str.contains('Setup')].copy()
        ongoing_data = dataPorArea[area][dataPorArea[area]['Variable'].str.contains('Ongoing')].copy()

        setup_data.loc[:, 'Variable'] = setup_data['Variable'].str.replace('Setup ', '')
        ongoing_data.loc[:, 'Variable'] = ongoing_data['Variable'].str.replace('Ongoing ', '')

        # Convierto la data para que "Variable" sea el indice y "Esfuerzo" sea el valor
        setup_dict = dict(zip(setup_data['Variable'], setup_data['Esfuerzo']))
        ongoing_dict = dict(zip(ongoing_data['Variable'], ongoing_data['Esfuerzo']))
        
        new_dataPorArea["Setup " + area] = setup_dict
        new_dataPorArea["Ongoing " + area] = ongoing_dict
    return new_dataPorArea


def get_promedio_ocurrencias_subCategoria_por_cliente_por_mes(df, tipo):
    # Filtro por tipo (Incidencia o Requerimiento)
    df = df[df['Tipo'] == tipo]

    # Cuento el numero de ocurrencias de sub-categoria por cliente por mes y anio
    cuenta_tipo_por_cliente_por_mes = df.groupby(['Cliente', 'Area', 'Categoria', 'Sub-Categoria', 'Año', 'Mes']).size().reset_index(name='Count')

    promedio_ocurrencias_subCategoria_por_cliente_por_mes = cuenta_tipo_por_cliente_por_mes.groupby(['Cliente', 'Area', 'Categoria', 'Sub-Categoria'])['Count'].mean().reset_index()
    promedio_ocurrencias_subCategoria_por_cliente_por_mes['Count'] = promedio_ocurrencias_subCategoria_por_cliente_por_mes['Count'].round(2)

    # Build a JSON with promedio_ocurrencias_subCategoria_por_cliente_por_mes which has the following structure:
    # {Cliente: {Area: {Categoria: {Sub-Categoria: Count}}}}
    #
    nested_dict = promedio_ocurrencias_subCategoria_por_cliente_por_mes.groupby(['Cliente', 'Area', 'Categoria']).apply(
        lambda x: dict(zip(x['Sub-Categoria'], x['Count']))
    ).reset_index().groupby(['Cliente', 'Area']).apply(
        lambda x: dict(zip(x['Categoria'], x[0]))
    ).reset_index().groupby('Cliente').apply(
        lambda x: dict(zip(x['Area'], x[0]))
    ).reset_index().to_dict(orient='records')

    # Create the final JSON structure
    json_promedio_ocurrencias_subCategoria_por_cliente_por_mes = {}
    for record in nested_dict:
        json_promedio_ocurrencias_subCategoria_por_cliente_por_mes[record['Cliente']] = record[0]

    return json_promedio_ocurrencias_subCategoria_por_cliente_por_mes

def get_tiempo_promedio_solucion_por_subCategoria_general(df, tipo):
    # Filtro por tipo (Incidencia o Requerimiento)
    df = df[df['Tipo'] == tipo]

    # Eliminar filas en donde tiempo total es 0
    df = df[df['Tiempo Total'] != 0]

    # Group by 'Tipo' (Incidencia o Requerimiento), 'Cliente', 'Sub-Categoria' y calculo el tiempo promedio de solucion
    tiempo_promedio_solucion_por_subCategoria_general = df.groupby(['Tipo', 'Area', 'Categoria', 'Sub-Categoria'])['Tiempo Total'].mean().reset_index()
    tiempo_promedio_solucion_por_subCategoria_general['Tiempo Total'] = tiempo_promedio_solucion_por_subCategoria_general['Tiempo Total'].round(2)
    # Build a JSON with tiempo_promedio_solucion_por_subCategoria_general which has the following structure:
    # {Area: {Categoria: {Sub-Categoria: Tiempo Total}}}
    #

    nested_dict = tiempo_promedio_solucion_por_subCategoria_general.groupby(['Area', 'Categoria']).apply(
        lambda x: dict(zip(x['Sub-Categoria'], x['Tiempo Total']))
    ).reset_index().groupby(['Area']).apply(
        lambda x: dict(zip(x['Categoria'], x[0]))
    ).reset_index().to_dict(orient='records')

    # Create the final JSON structure
    json_promedio_solucion_por_categoria_general = {}
    for record in nested_dict:
        json_promedio_solucion_por_categoria_general[record['Area']] = record[0]

    return json_promedio_solucion_por_categoria_general

def get_tiempo_promedio_solucion_por_subCategoria_por_cliente(df, tipo):
    # Filtro por tipo (Incidencia o Requerimiento)
    df = df[df['Tipo'] == tipo]

    # Eliminar filas en donde tiempo total es 0
    df = df[df['Tiempo Total'] != 0]

    # Group by 'Tipo' (Incidencia o Requerimiento), 'Cliente', 'Sub-Categoria' y calculo el tiempo promedio de solucion
    tiempo_promedio_solucion_por_subCategoria_por_cliente = df.groupby(['Tipo', 'Cliente', 'Area', 'Categoria', 'Sub-Categoria'])['Tiempo Total'].mean().reset_index()
    tiempo_promedio_solucion_por_subCategoria_por_cliente['Tiempo Total'] = tiempo_promedio_solucion_por_subCategoria_por_cliente['Tiempo Total'].round(2)

    # Build a JSON with tiempo_promedio_solucion_por_subCategoria_por_cliente which has the following structure:
    # {Cliente: {Area: {Categoria: {Sub-Categoria: Tiempo Total}}}}
    #

    # Convert the DataFrame to a nested dictionary
    nested_dict = tiempo_promedio_solucion_por_subCategoria_por_cliente.groupby(['Cliente', 'Area', 'Categoria']).apply(
        lambda x: dict(zip(x['Sub-Categoria'], x['Tiempo Total']))
    ).reset_index().groupby(['Cliente', 'Area']).apply(
        lambda x: dict(zip(x['Categoria'], x[0]))
    ).reset_index().groupby('Cliente').apply(
        lambda x: dict(zip(x['Area'], x[0]))
    ).reset_index().to_dict(orient='records')

    # Create the final JSON structure
    json_promedio_solucion_por_categoria_por_cliente = {}
    for record in nested_dict:
        json_promedio_solucion_por_categoria_por_cliente[record['Cliente']] = record[0]
    
    return json_promedio_solucion_por_categoria_por_cliente

def get_promedio_ocurrencias_subCategoria_por_sector_por_mes(df, tipo):
    # Filtro por tipo (Incidencia o Requerimiento)
    df = df[df['Tipo'] == tipo]

    # Cuento el numero de ocurrencias de sub-categoria por cliente por mes y anio
    cuenta_tipo_por_cliente_por_mes_por_sector = df.groupby(['Area', 'Categoria', 'Sub-Categoria', 'Año', 'Mes', 'Sector']).size().reset_index(name='Count')

    promedio_ocurrencias_subCategoria_por_cliente_por_mes_por_sector = cuenta_tipo_por_cliente_por_mes_por_sector.groupby(['Area', 'Categoria', 'Sub-Categoria', 'Sector'])['Count'].mean().reset_index()
    promedio_ocurrencias_subCategoria_por_cliente_por_mes_por_sector['Count'] = promedio_ocurrencias_subCategoria_por_cliente_por_mes_por_sector['Count'].round(2)

    # Build a JSON with promedio_ocurrencias_subCategoria_por_cliente_por_mes which has the following structure:
    # {Sector: {Area: {Categoria: {Sub-Categoria: Count}}}}
    #
    nested_dict = promedio_ocurrencias_subCategoria_por_cliente_por_mes_por_sector.groupby(['Sector', 'Area', 'Categoria']).apply(
        lambda x: dict(zip(x['Sub-Categoria'], x['Count']))
    ).reset_index().groupby(['Sector', 'Area']).apply(
        lambda x: dict(zip(x['Categoria'], x[0]))
    ).reset_index().groupby('Sector').apply(
        lambda x: dict(zip(x['Area'], x[0]))
    ).reset_index().to_dict(orient='records')


    # Create the final JSON structure
    json_promedio_ocurrencias_subCategoria_por_cliente_por_mes = {}
    for record in nested_dict:
        json_promedio_ocurrencias_subCategoria_por_cliente_por_mes[record['Sector']] = record[0]

    return json_promedio_ocurrencias_subCategoria_por_cliente_por_mes

def get_estimaciones(df):
    estimaciones = {"Incidencias": {}, "Requerimientos": {}}
    estimaciones["Incidencias"]["Promedio Ocurrencias por Cliente"] = get_promedio_ocurrencias_subCategoria_por_cliente_por_mes(df, "Incidencia")
    estimaciones["Incidencias"]["Sub-Categoria General"] = get_tiempo_promedio_solucion_por_subCategoria_general(df, "Incidencia")
    estimaciones["Incidencias"]["Sub-Categoria por Cliente"] = get_tiempo_promedio_solucion_por_subCategoria_por_cliente(df, "Incidencia")
    estimaciones["Incidencias"]["Promedio Ocurrencias por Sector"] = get_promedio_ocurrencias_subCategoria_por_sector_por_mes(df, "Incidencia")
    estimaciones["Requerimientos"]["Promedio Ocurrencias por Cliente"] = get_promedio_ocurrencias_subCategoria_por_cliente_por_mes(df, "Requerimiento")
    estimaciones["Requerimientos"]["Sub-Categoria General"] = get_tiempo_promedio_solucion_por_subCategoria_general(df, "Requerimiento")
    estimaciones["Requerimientos"]["Sub-Categoria por Cliente"] = get_tiempo_promedio_solucion_por_subCategoria_por_cliente(df, "Requerimiento")
    estimaciones["Requerimientos"]["Promedio Ocurrencias por Sector"] = get_promedio_ocurrencias_subCategoria_por_sector_por_mes(df, "Requerimiento")
    return estimaciones

def get_estimaciones_por_cliente(cliente, estimaciones):
    try:
        return estimaciones[cliente]
    except:
        return {}

def costRatePreProcessing(df):
    df = df[['Perfil', 'Costo Unitario ($)']]
    # Convierto dataframe en json con estructura {Perfil: Costo Unitario}
    df = df.set_index('Perfil').T.to_dict('records')[0]
    # TODO: THIS
    # with open('costRate.json', 'w') as outfile:
    #     json.dump(df, outfile)
    return df

def tiemposYPerfilesSetup(df):
    # Csv viene en formato Area, Perfil, Horas x Equipo
    # Lo convierto a un json con la siguiente estructura:
    # {Area: {Perfil: Horas x Equipo}}
    tiemposPerfiles = {}
    for index, row in df.iterrows():
        if row['Area'] not in tiemposPerfiles:
            tiemposPerfiles[row['Area']] = {}
        tiemposPerfiles[row['Area']][row['Perfil']] = row['Horas x Equipo']

    return tiemposPerfiles

def getCostoSetupPorEquipoPorArea(costRates, PerfilesTiempo):
    costoSetupPorEquipoPorArea = {}
    for area in PerfilesTiempo:
        costoSetupPorEquipoPorArea[area] = {}
        for perfil in PerfilesTiempo[area]:
            costoSetupPorEquipoPorArea[area] = float(costRates[perfil]) * PerfilesTiempo[area][perfil]

# TODO: THIS
    # with open('costoSetupPorEquipoPorArea.json', 'w') as outfile:
    #     json.dump(costoSetupPorEquipoPorArea, outfile)

    return costoSetupPorEquipoPorArea

# La API va a usar esta funcion para pasar toda la data en un solo JSON a la pagina web
def getAllData():
    data = clientDataPreProcessing(CLIENT_DATA_PATH)
    dataJson = {}
    dataJson['Estimaciones'] = get_estimaciones(data)
    dataJson['Variables de Servicio'] = variablesDeServicioPreprocessing(VARIABLES_DE_SERVICIO_PATH)
    dataJson['Costo Setup por Equipo por Area'] = getCostoSetupPorEquipoPorArea(costRatePreProcessing(pd.read_csv(COST_RATE_PATH)), tiemposYPerfilesSetup(pd.read_csv(TIEMPOS_PERFILES_SETUP_PATH)))
    return dataJson

def getVariablesServicio():
    return variablesDeServicioPreprocessing(VARIABLES_DE_SERVICIO_PATH)

def getCostos():
    return getCostoSetupPorEquipoPorArea(costRatePreProcessing(pd.read_csv(COST_RATE_PATH)), tiemposYPerfilesSetup(pd.read_csv(TIEMPOS_PERFILES_SETUP_PATH)))

getVariablesServicio()
# data = clientDataPreProcessing(testPath)
writeToJsonFile(getAllData(), 'data.json')

from class_create_config import CreateConfig
from class_device_config import ConfigDevice
import json, os
from datetime import datetime


def main():
    print("Hello from iac-try5! \n Starting coso...")
    creador = CreateConfig()
    configurador = ConfigDevice()

    # Leer el modelo YAML
    dic_modelo = creador.read_yaml('./datos/modelo.yml')
    print(json.dumps(dic_modelo, indent= 2))

    # Generar configs para cada dispositivo
    print(f"Generando configs para cada device...")
    for device in dic_modelo.get('modelo').get('estructura').get('infra'):
        hostname = device.get('hostname')
        print(f"Generando config para {hostname}...")                                 
        for configuracion in device.get('config_spec'):
            iterable = configuracion.get('data_path')
            plantilla = configuracion.get('template')
            nombre_archivo = f"{hostname}_{configuracion.get('config_file')}"

            # Renderizar la plantilla
            print(f"====== Creando el archivo {nombre_archivo} usando la plantilla {plantilla} ======")
            templateCreada = creador.render_template(template_name= plantilla, data= {iterable: device.get(iterable)})
            creador.save_config(filename= nombre_archivo, config= templateCreada)
            print(f"====== Archivo {nombre_archivo} creado exitosamente ======")  

    # Almacenar y listar archivos de configuracion generados
    print(f"\n --> Archivos de configuracion disponibles")
    cfg_files = os.listdir('./configs')
    [print (f) for f in sorted(cfg_files) if f.endswith('.cfg')]

    # Conectar y enviar configs a cada dispositivo
    print(f"--> Conectando a los devs y enviando configs...")
    tiempo_total = datetime.now()
    hora_inicio = datetime.now()
    procesados = 0
    for device in dic_modelo.get('modelo').get('estructura').get('infra'):
        procesados += 1
        print(f"\n --> Procesando equipo {procesados} de {len(dic_modelo.get('modelo').get('estructura').get('infra'))}")
        parametros = device.get('connection')
        ip_host = parametros.get('host')
        hostname = device.get('hostname')

        # Conectando
        conexion = configurador.connect_device(parametros= parametros)
        print(f"Conectado a {hostname} en {ip_host}")
        # Leyendo archivos y enviarlos
        print(f"--> Procesando los archivos para {hostname}...")

        # Separando los archivos del host en cuestión
        archivos_host = [f for f in sorted(cfg_files) if f.startswith(hostname)]

        # Aca los ordeno segun order para mandar en secuencia
        # Crear diccionario {config_file: order}
        spec_map = { spec["config_file"]: spec.get("order", 999) for spec in device.get("config_spec") }

        # Ordenar los archivos del host según el order del YAML
        archivos_host = sorted(
            archivos_host,
            key=lambda f: spec_map.get(f.split(f"{hostname}_")[-1], 999)
        )

        for archivo in archivos_host:
            print(f"--> Aplicando config {archivo} para {hostname}...")
            output = configurador.send_config_commands(conexion= conexion, config_file= archivo)

            # Verificar errores
            hay_errores = configurador.check_output_for_errors(output= output)
            if hay_errores:
                print(f"!!! Hubo errores para '{device.get('hostname')}'. Abort the mission !!!")
                break
            else:
                print(f"Config '{archivo}' aplicada exitosamente a '{hostname}'")
       
        # Guardar la config y si ok, calcular tiempo
        if not hay_errores:
            configurador.save_running_config(conexion= conexion)
            print(f"Configuración guardada en dispositivo {hostname}")
            hora_fin = datetime.now()
            duracion = hora_fin - hora_inicio
            print(f"Tiempo de configuración para {hostname}: {duracion}")

        # Desconectar
        configurador.disconnect_device(conexion= conexion)
        print(f"... adios {hostname} \n")

    # Calcular e imprimir el tiempo total empleado
    final_total = datetime.now()
    duracion_total = final_total - hora_inicio
    print(f"\n ---> Tiempo total para configurar {procesados} dispositivos: {duracion_total} <---")




if __name__ == "__main__":
    main()

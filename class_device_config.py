from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
import yaml

class ConfigDevice():
    # Leer archivo de configuración
    def read_config_file(self, file_name: str, file_dir: str = './configs') -> str:
        try:
            file_path = f"{file_dir}/{file_name}"
            with open(file_path, 'r') as config_file:
                return config_file.read()
        except Exception as e:
            print(f"Error al leer el archivo de configuración: {e}")
            exit(1)

    # Conectar al dispositivo
    def connect_device(self, parametros: dict) -> ConnectHandler:
        try:
            conexion = ConnectHandler(**parametros)
            return conexion
        except (NetmikoAuthenticationException, NetmikoTimeoutException) as exc:
            print(f"Error de conexión al dispositivo {parametros.get('hostname')} : {exc}")
            exit(1)

    # Mandar configuración al device
    def send_config_commands(self, conexion: ConnectHandler, config_commands: list = None, config_file: str = None, config_dir: str = './configs') -> str:
        try:
            if config_commands:
                output = conexion.send_config_set(config_commands)
                return output
            elif config_file:
                file_path = f"{config_dir}/{config_file}"
                output = conexion.send_config_from_file(file_path)
                return output
        except Exception as e:
            print(f"Error al enviar comandos de configuración: {e}")
            exit(1)

    # Verificar errores en la salida
    def check_output_for_errors(self, output: str) -> bool:
        error_indicators = ['% Invalid input', '% Incomplete command', '% Ambiguous command']
        for line in output.splitlines():
            if any (error in line for error in error_indicators):
                return True
        return False
    
    # Desconectar el dispositivo
    def disconnect_device(self, conexion: ConnectHandler) -> None:
        try:
            conexion.disconnect()
        except Exception as ex:
            print(f"Error al desconectar el dispositivo: {ex}")
            exit(1)

    # Salvar la configuración
    def save_running_config(self, conexion: ConnectHandler) -> None:
        try:
            conexion.save_config()
        except Exception as ex:
            print(f"Error al guardar la configuración: {ex}")    
            exit(1)
            



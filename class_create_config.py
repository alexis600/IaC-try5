from jinja2 import Environment, FileSystemLoader
import yaml, json, os

class CreateConfig():
    # Renderizar la plantilla con datos proporcionados
    def render_template(self, template_name: str, data: dict, template_dir: str = 'templates') -> str:
        loader = FileSystemLoader(template_dir)
        env = Environment(loader= loader)
        plantilla = env.get_template(template_name) 
        return plantilla.render(data)
    
    # Leer el modelo yaml
    def read_yaml(self, file_path: str) -> dict:
        try:
            with open(file_path, 'r') as yaml_model:
                return yaml.safe_load(yaml_model)
        except Exception as e:
            print(f"Error al leer el archivo YAML: {e}")
            exit(1)

    # Guardar la configuracion generada en archivo
    def save_config(self, filename: str, config: str, file_dir: str = '.\\configs') -> None:
        os.makedirs(file_dir, exist_ok=True)
        file_path = os.path.join(file_dir, filename)
        try:
            with open(file_path, 'w') as archivo:
                archivo.write(config)
            print(f"Configuración guardada en {file_path}")
        except Exception as e:
            print(f"Error al guardar la configuracion en archivo: {e}")
            exit(1)

    # Escribir datos en formato JSON
    def write_json(self, data: dict, file_path: str) -> None:
        try:
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=10)
        except Exception as e:
            print(f"Error al escribir el archivo JSON: {e}")




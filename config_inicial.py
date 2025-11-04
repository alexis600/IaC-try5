from netmiko import ConnectHandler
import time

def configuracion_inicial():
    dispositivo = {        
          "device_type": "cisco_ios_telnet",
          "host": "192.168.1.52",
          "username" : "",
          "password" : "cisco",
          "secret" : "cisco",
        }
    conexion = ConnectHandler(**dispositivo)
    conexion.enable()
    comando = "hostname SW-CORE_2"
    salida = conexion.send_config_set([comando], exit_config_mode= True)
    time.sleep(2)

    conexion.write_channel('\n')
    conexion.read_until_prompt()

    salida = conexion.send_config_from_file("setup.cfg", delay_factor = 2, exit_config_mode = False)
    time.sleep(3)

    # ✅ Forzar volver al modo exec y sync del prompt
    conexion.write_channel("end\n")
    time.sleep(1)
    conexion.write_channel("\n")
    conexion.read_until_prompt()



    print(conexion.find_prompt())
    conexion.exit_config_mode()
    print(conexion.find_prompt())
    conexion.disconnect()

configuracion_inicial()

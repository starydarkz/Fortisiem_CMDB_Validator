# FortiSIEM CMDB Validator
![](https://github.com/starydarkz/fortisiem_cmdb-validator/blob/main/portada.png)

Este programa utiliza la API de FortiSIEM para extrare y analizar informacion sobre los equipos integrados en la CMDB.


Funciones de la herramienta:
- Extraer equipos de la CMDB de FortiSIEM a partir de un listado.
- Extraer equipos que no envian eventos por un tiempo determinado en la CMDB.
- Extraer todos los equipos de la CMDB de FortiSIEM y mostrar si han enviado eventos o no en un rango de tiempo.

## Instalacion
1. Descargar repositorio desde la web o mediante git clone:
```bash
git clone https://github.com/starydarkz/fortisiem_cmdb-validator.git
cd fortisiem_cmdb-validator
pip3 install -r requeriments.txt
```

## Uso
```bash
_python3_ cmdb_validator
```
- **IP FortiSIEM:** Dirección IP del Servidor FortiSIEM
- **Username FortiSIEM (ej: super/user):** Usuario y la organizacion.
- **Password FortiSIEM:** Contraseña del usuario de FortiSIEM.
- **LastEvent Max Hours:** Cantidad en horas en relativo para validar si los equipos enviaron eventos.



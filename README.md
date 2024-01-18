# FortiSIEM CMDB Validator
![](https://github.com/starydarkz/fortisiem_cmdb-validator/blob/main/portada.png)

Este programa utiliza la API de FortiSIEM para extrare y analizar informacion sobre los equipos integrados en la CMDB.


Actualmente es capaz de realizar las siguientes validaciones:
- Validar la CMDB a partir de un listado: Util para analizar un inventario de equipos especificos.
- Extraer equipos que no envian eventos: Util para extraer equipos que estan o no en el siem y se quiere validar si estan enviando eventos y cuando.
- Extrare toda CMDB y la ultima vez que enviaron: Util para  extraer la lista de equipos de la CMDB y la ultima vez que enviaron.

## Instalacion
1. Descargar repositorio desde la web o mediante git clone:
```bash
git clone https://github.com/starydarkz/fortisiem_cmdb-validator.git
```
2. Tener instalado Python3
3. Instalar las dependencias necesarias usando el archivo requeriments:
```bash
cd fortisiem_cmdb-validator
pip3 install -r requeriments.txt
```

## Ejecutar el script
```bash
python3 cmdb_validator
```

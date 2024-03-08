# Prueba de concepto #

## Explicación ##
Esta aplicación de prueba permite a los usuarios subir registros y observarlos, ya sea uno de ellos o todos. Esta prueba de concepto les permitirá entender como empezar a realizar el proyecto del curso de Software Verificable.

En esta prueba de concepto, un registro contiene dos parámetros:
* Texto: Es cualquier clase de texto
* Numero: un número cualquiera

Esta versión contiene 3 vistas principales:
* Ver todos los registros (```/``` o ```/register```): Esta vista permite ver todos los registros
* Ver un registro (```/register/<id>```): Esta vista permite ver el registro con id ```<id>```
* Crear un registro (```/create```): Esta vista permite crear un registro

## Como ejecutar el aplicativo ##
Para ejecutar el aplicativo se debe seguir los siguientes pasos:
* Ejecutar el docker compose que se encuentra en la carpeta ```db``` con el comando ```docker compose up```
    * Debe tener instalado ```docker``` en su maquina para poder ejecutar ese comando
* Se debe ingresar a la base de datos con algun administrador de base de datos relacional de preferencia (pgAdmin, dBeaver, etc) y crear la tabla de registros que se encuentra en la carpeta ```db``` en el archivo ```db.sql```
* Instalar las librerias que se encuentran en el archivo ```requirements.txt``` utilizando el comando ```pip install -r requirements.txt```
    * NOTA: Si el comando anterior no funciona puedes utilizarlo indicando que se ejecute desde python con ```python -m pip install -r requirements.txt```
* Crear un archivo ```.env``` que contenga lo siguiente:
    ```
    MYSQL_HOST='localhost'
    MYSQL_PORT=3306
    MYSQL_DATABASE='test_poc'
    MYSQL_USER='user'
    MYSQL_PASSWORD='pass'
    ```
* Ejecutar la aplicación desde ```main.py``` con el comando ```python .\main.py```
    * Por defecto la aplicacion se ejecuta en ```localhost``` en el puerto ```5000```

## Como ejecutar las pruebas ##
En esta prueba de concepto existe un archivo de pruebas (```test.py```) que permite evaluar la funcionalidad de cada uno de los aplicativos, se puede ejecutar el test utilizando el siguiente comando:

```pytest test.py```

Si no funciona el comando anterior, se puede ejecutar desde python con el siguiente comando:

```python -m pytest test.py```

Con las librerias ```coverage``` y ```pytest-cov``` se pueden generar reportes de covertura de código después de ejecutar los tests, para ello se debe ejecutar el siguiente comando:

```pytest --cov=. test.py --cov-report html```

Si no funciona el comando anterior, se puede ejecutar desde python con el siguiente comando:

```python3.9 -m pytest --cov=. test.py --cov-report html```

Ya con el reporte generado, se debe haber creado una carpeta llamada ```htmlcov```, dentro de esta se muestra un archivo ```index.html```, al abrirlo se mostrara la cobertura de codigo a través de los tests.

Existe un archivo llamado ```.coveragerc``` que permite configurar los reportes, en este caso, se omite medir el coverage a través de tests de los módulos que se presentan en ese archivo.
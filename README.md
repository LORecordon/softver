# Prueba de concepto #

## Explicación ##
Esta aplicación de prueba permite a los usuarios subir registros y observarlos, ya sea uno de ellos o todos. Esta prueba de concepto les permitirá entender cómo empezar a realizar el proyecto del curso de Software Verificable.

En esta prueba de concepto, un registro contiene dos parámetros:
* Texto: Es cualquier clase de texto
* Numero: un número cualquiera

Esta versión contiene 3 vistas principales:
* Ver todos los registros (```/``` o ```/register```): Esta vista permite ver todos los registros
* Ver un registro (```/register/<id>```): Esta vista permite ver el registro con id ```<id>```
* Crear un registro (```/create```): Esta vista permite crear un registro, en esta prueba de concepto se pueden crear registros de dos formas distinas:
    * Formulario: Se puede agregar un registro mediante un formulario
    * Archivo JSON: Se pueden agregar uno o varios registros mediante un archivo JSON como el adjunto en este repositorio (````test.json```)

## Cómo ejecutar el aplicativo ##
Para ejecutar el aplicativo se deben seguir los siguientes pasos:
* Ejecutar el docker compose que se encuentra en la carpeta ```db``` con el comando ```docker compose up```
    * Debe tener instalado ```docker``` en su máquina para poder ejecutar ese comando
* Se debe ingresar a la base de datos con algún administrador de base de datos relacional de preferencia (pgAdmin, dBeaver, etc) y crear la tabla de registros que se encuentra en la carpeta ```db``` en el archivo ```db.sql```
* Instalar las bibliotecas que se encuentran en el archivo ```requirements.txt``` utilizando el comando ```pip install -r requirements.txt```
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
    * Por defecto la aplicación se ejecuta en ```localhost``` en el puerto ```5000```

## Cómo ejecutar las pruebas ##
En esta prueba de concepto existe un archivo de pruebas unitarias (```test.py```) que permite evaluar la funcionalidad de cada uno de los aplicativos, se puede ejecutar el test utilizando el siguiente comando:

```pytest test.py```

Si no funciona el comando anterior, se puede ejecutar desde python con el siguiente comando:

```python -m pytest test.py```

Con las bibliotecas ```coverage``` y ```pytest-cov``` se pueden generar reportes de cobertura de código después de ejecutar los tests, para ello se debe ejecutar el siguiente comando:

```pytest --cov=. test.py --cov-report html```

Si no funciona el comando anterior, se puede ejecutar desde python con el siguiente comando:

```python3.9 -m pytest --cov=. test.py --cov-report html```

Ya con el reporte generado, se debe haber creado una carpeta llamada ```htmlcov```, dentro de ésta se muestrá un archivo ```index.html```, al abrirlo se mostrará la cobertura de codigo a través de los tests.
# Servicio de Scrapeo de Cesionarios con Serverless Framework

Este repositorio contiene el código fuente y la configuración necesaria para desplegar un servicio de scrapeo de cesiones obtenidas por una empresa, utilizando el framework Serverless y las funciones Lambda de AWS.

## Descripción del proyecto

El objetivo de este proyecto es desarrollar un servicio de scrapeo que obtenga cesiones de Simpli y posteriormente las procese mediante funciones Lambda de AWS. El framework Serverless nos permite simplificar el proceso de despliegue y gestión de nuestras funciones Lambda, así como facilitar la configuración de los diferentes stages (entornos) del proyecto.

## Estructura del repositorio

El repositorio está estructurado de la siguiente manera:

- **`src/`**: Contiene el código fuente de las funciones Lambda.
- **`serverless.yml`**: Archivo de configuración de Serverless Framework.
- **`inputs/`**: Carpeta con archivos JSON que contienen los datos de prueba para las funciones.

## Configuración de Serverless Framework

El archivo `serverless.yml` contiene la configuración de nuestro servicio y las funciones Lambda asociadas. Además, se declaran dos grupos de variables de entorno para mantener los stages de desarrollo (`dev`) y producción (`prod`). Estos stages acceden a secretos distintos, lo que permite tener diferentes configuraciones dependiendo del entorno.

## Pruebas de las funciones

Para probar las funciones Lambda, se proporcionan archivos JSON en la carpeta `inputs/`. Estos archivos contienen el mostrario de inputs necesarios para cada función. Puedes utilizar estos archivos como ejemplos de entrada para verificar el correcto funcionamiento de las funciones en diferentes escenarios.

## Despliegue del servicio

Para desplegar el servicio en AWS utilizando Serverless Framework, sigue los siguientes pasos:

1. Asegúrate de tener una cuenta de AWS y las credenciales adecuadas configuradas en tu entorno de desarrollo.
2. Instala Serverless Framework globalmente si no lo has hecho aún: `npm install -g serverless`.
3. Modifica el archivo `serverless.yml` según tus necesidades y especifica las variables de entorno requeridas.
4. Ejecuta el comando `serverless deploy --stage dev --region us-east-2` para desplegar el servicio en el stage de desarrollo.
5. Si deseas desplegar en producción, ejecuta `serverless deploy --stage prod --region us-east-2`.
6. Verifica la salida del despliegue para obtener las URLs de las funciones y otros detalles relevantes.

## Esquema de Arquitectura

![Esquema de arquitectura](https://simpliassets12daacw.s3.us-east-2.amazonaws.com/shema_architecture.jpeg)
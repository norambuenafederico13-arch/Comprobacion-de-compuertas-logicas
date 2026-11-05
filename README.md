# Comprobador automatizado de compuertas lógicas con ESP32-S3

Este sistema se basa en la comprobación de las compuertas lógicas de un circuito integrado (como las familias CMOS serie 4000 y TTL serie 74) de manera individual.

## Importante

>  Para que la totalidad del sistema funcione correctamente, es necesario compilar y subir primero el código terminado en `.ino` al ESP32 para habilitar el puerto usb nativo, luego de esto, se podrá ejecutar el script de python (`.py`) en la computadora para establecer la comunicación serial.

## Requisitos de software

Para el funcionamiento básico del programa es necesario contar con Visual Studio Code y las siguientes librerías de python instaladas:
* PySerial
* CustomTkinter

## Código de instalación en la terminal

```bash
pip install customtkinter pyserial
```

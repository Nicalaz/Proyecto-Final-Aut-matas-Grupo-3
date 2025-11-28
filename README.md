# Proyecto-Final-Autómatas-Grupo-3

## Simulador de Tráfico con Autómatas Celulares

En este proyecto se realizó la simulación de una intersección vial controlada por semáforos mediante el uso de autómatas celulares, modelando la generación de vehículos en cuatro sentidos, flujo o detención del tráfico según el color de los semáforos y colisiones.

## Funcionamiento

-	El estado de un vehículo es determinado por la disponibilidad de la celda siguiente, el color del semáforo correspondiente y otros vehículos a su alrededor.
-	Los semáforos alternan entre color rojo y verde, si están en la misma orientación (vertical u horizontal) comparten estado.
-	En la interfaz se encuentran herramientas para controlar el flujo de los vehículos, iniciar y reiniciar, y un contador de colisiones.
-	Si se alcanza el umbral de colisiones definido se detiene el movimiento.

## Reglas del Autómata Celular

- Si el semáforo está en verde el vehículo se mueve, si está en rojo se detiene.
-	Si la celda siguiente está vacía el vehículo se mueve.
- Si la celda siguiente está ocupada por un vehículo del mismo tipo se detiene.
-	Si la celda a la que desea moverse es igual a la de otro vehículo del mismo tipo, se elige uno al azar para ocuparla.
-	Si la celda siguiente está ocupada por un vehículo de otro tipo se presenta una colisión.
-	Si la celda siguiente está fuera de la cuadrícula, el vehículo desaparece.


## LINK DEL VIDEO DE YOUTUBE 
https://www.youtube.com/watch?v=QZ0dpbaYgKA


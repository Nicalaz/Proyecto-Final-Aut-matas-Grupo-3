# Proyecto-Final-Aut-matas-Grupo-3

## Simulador de tráfico y colisiones en cruces con semáforos

En este proyecto se realizó la simulación de una intersección vial controlada por semáforos mediante el uso de autómatas celulares, modelando la generación de vehículos en cuatro sentidos, flujo o detención del tráfico según el color de los semáforos y colisiones.

## Funcionamiento

- El estado de un vehículo es determinado por la disponibilidad de la celda siguiente, el color del semáforo correspondiente y si hay otros vehículos a su alrededor.
- Si la celda siguiente está ocupada por un vehículo de tipo distinto, se produce una colisión.
- Los semáforos alternan entre color rojo y verde. Los semáforos en la misma orientación (vertical u horizontal) comparten estado.
- Si se alcanza el umbral de colisiones definido se detiene el movimiento.

## Reglas del autómata celular

-	Si la celda siguiente está vacía el vehículo se mueve.
-	Si la celda siguiente está ocupada por un vehículo del mismo tipo compiten, se elige uno solo al azar para ocuparla.
-	Si la celda siguiente está ocupada por un vehículo de otro tipo se presenta una colisión.
-	Si la celda siguiente está fuera de la cuadrícula, reaparece al inicio.


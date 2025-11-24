import pygame 
import random
import sys

# --- Configuración general ---
ANCHO, ALTO = 600, 600
TAM_CELDA = 20
FPS = 8 #velocidad de los autos

COLOR_FONDO = (40, 40, 40)
COLOR_CARRETERA = (90, 90, 90)
COLOR_INTERSECCION = (120, 120, 120)
COLOR_AUTO_H = (0, 200, 255)
COLOR_AUTO_V = (255, 200, 0)
COLOR_SEM_VERDE = (0, 255, 0)
COLOR_SEM_ROJO = (255, 0, 0)
COLOR_BORDE = (60, 60, 60)

# --- Clases principales ---
class TrafficLight:
    def __init__(self, x, y, horizontal=True, cycle_length=15):
        self.x = x
        self.y = y
        self.state = 3  # 3 = verde, 4 = rojo
        self.counter = 0
        self.cycle_length = cycle_length
        self.horizontal = horizontal

    def update(self):
        self.counter += 1
        if self.counter >= self.cycle_length:
            self.counter = 0
            self.state = 4 if self.state == 3 else 3  # alternar


class Vehicle:
    def __init__(self, x, y, dx, dy, color):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color

    def move(self, grid, lights):
        next_x = self.x + self.dx
        next_y = self.y + self.dy

        # Si sale de la pantalla, reaparece al inicio
        if not (0 <= next_x < len(grid[0]) and 0 <= next_y < len(grid)):
            grid[self.y][self.x] = 0
            return True

        # Detectar si hay semáforo rojo en la trayectoria
        for light in lights:
            if light.state == 4:
                # Semáforo horizontal
                if light.horizontal and self.dy == 0 and light.y == self.y and light.x == next_x:
                    return False
                # Semáforo vertical
                if not light.horizontal and self.dx == 0 and light.x == self.x and light.y == next_y:
                    return False

        # Si la celda está vacía, avanzar
        if grid[next_y][next_x] == 0:
            grid[self.y][self.x] = 0
            grid[next_y][next_x] = 1
            self.x, self.y = next_x, next_y
        return False


class Grid:
    def __init__(self, filas, columnas):
        self.rows = filas
        self.cols = columnas
        self.grid = [[0 for _ in range(columnas)] for _ in range(filas)]
        self.vehicles = []
        self.lights = []

    def add_light(self, x, y, horizontal=True, cycle=15):
        self.lights.append(TrafficLight(x, y, horizontal, cycle))

    def add_vehicle(self, x, y, dx, dy, color):
        if self.grid[y][x] == 0:
            self.grid[y][x] = 1
            self.vehicles.append(Vehicle(x, y, dx, dy, color))

    def update(self):
        # Actualizar semáforos
        for l in self.lights:
            l.update()

        # Sincronizar: uno verde → otro rojo
        if len(self.lights) == 4:
            # Encontrar los semáforos horizontales y verticales
            h_lights = [l for l in self.lights if l.horizontal]
            v_lights = [l for l in self.lights if not l.horizontal]

            # Solo actualizar el contador y alternar el primer semáforo de un grupo (por ejemplo, h_lights[0])
            # y luego sincronizar a los demás.
            # Solo ejecutamos el .update() en uno de cada grupo para controlar el ciclo
            
            # Asegurar que todos los horizontales tengan el mismo estado que h_lights[0]
            for l in h_lights[1:]:
                l.state = h_lights[0].state 

            # Asegurar que todos los verticales tengan el estado opuesto a los horizontales
            # Esto asume que el primer semáforo vertical es v_lights[0]
            v_lights[0].state = 4 if h_lights[0].state == 3 else 3
            for l in v_lights[1:]:
                l.state = v_lights[0].state

        # Mover vehículos
        removed = []
        for v in self.vehicles:
            out = v.move(self.grid, self.lights)
            if out:
                removed.append(v)
        for v in removed:
            self.vehicles.remove(v)

        if random.random() < 0.2:
            # Horizontal - Carril superior
            self.add_vehicle(0, self.rows // 2 - 1, 1, 0, COLOR_AUTO_H) # Fila cy - 1
        if random.random() < 0.2:
            # Horizontal - Carril inferior
            self.add_vehicle(0, self.rows // 2, 1, 0, COLOR_AUTO_H) # Fila cy
        if random.random() < 0.2:
            self.add_vehicle(0, self.rows // 2-2, 1, 0, COLOR_AUTO_H)

        if random.random() < 0.2:
            # Vertical - Carril izquierdo
            self.add_vehicle(self.cols // 2, self.rows - 1, 0, -1, COLOR_AUTO_V) # Columna cx
        if random.random() < 0.2:
            # Vertical - Carril derecho
            self.add_vehicle(self.cols // 2 + 1, self.rows - 1, 0, -1, COLOR_AUTO_V) # Columna cx + 1
        if random.random() < 0.2:
            self.add_vehicle(self.cols // 2 -1, self.rows - 1, 0, -1, COLOR_AUTO_V)

    def draw(self, screen):
        screen.fill(COLOR_FONDO)
        cx, cy = self.cols // 2, self.rows // 2

        for y in range(self.rows):
            for x in range(self.cols):
                
                rect = pygame.Rect(x * TAM_CELDA, y * TAM_CELDA, TAM_CELDA, TAM_CELDA)
                color = COLOR_FONDO 

                # Carreteras
                if y == cy or x == cx:
                    color = COLOR_INTERSECCION if (x == cx and y == cy) else COLOR_CARRETERA
                
                pygame.draw.rect(screen, color, rect) 
                pygame.draw.rect(screen, COLOR_BORDE, rect, 1) 
                
        # Dibujar autos
        for v in self.vehicles:
            rect = pygame.Rect(v.x * TAM_CELDA + 3, v.y * TAM_CELDA + 3, TAM_CELDA - 4, TAM_CELDA - 4)
            pygame.draw.rect(screen, v.color, rect)

        # Dibujar semáforos
        for light in self.lights:
            color = COLOR_SEM_VERDE if light.state == 3 else COLOR_SEM_ROJO
            pygame.draw.circle(screen, color, ((light.x + 0.5) * TAM_CELDA, (light.y + 0.5) * TAM_CELDA), TAM_CELDA // 2)


# --- Bucle principal ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Simulador de Tráfico - Intersección (Autómatas Celulares)")
    clock = pygame.time.Clock()

    filas = ALTO // TAM_CELDA
    columnas = ANCHO // TAM_CELDA
    grid = Grid(filas, columnas)

    cx, cy = columnas // 2, filas // 2
    
    # Semáforos HORIZONTALES (controlan el flujo en X)
    # Carril superior (yendo a la derecha)
    grid.add_light(cx - 3, cy - 1, horizontal=True, cycle=20) 
    # Carril inferior (yendo a la derecha)
    grid.add_light(cx - 3, cy, horizontal=True, cycle=20) 
    grid.add_light(cx-3, cy-2, horizontal=True, cycle=20)

    # Semáforos VERTICALES (controlan el flujo en Y)
    # Carril izquierdo (yendo hacia arriba)
    grid.add_light(cx, cy + 2, horizontal=False , cycle=20) 
    # Carril derecho (yendo hacia arriba)
    grid.add_light(cx + 1, cy + 2, horizontal=False , cycle=20)
    grid.add_light(cx-1, cy +2, horizontal=False , cycle=20)
    

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        grid.update()
        grid.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

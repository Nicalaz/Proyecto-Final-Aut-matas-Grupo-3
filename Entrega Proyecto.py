import pygame 
import random
import sys

# --- Configuración general ---
ANCHO, ALTO = 900, 900
TAM_CELDA = 20
FPS = 6 #velocidad de los autos

COLOR_FONDO = (40, 40, 40)
COLOR_CARRETERA = (90, 90, 90)
COLOR_INTERSECCION = (120, 120, 120)
COLOR_AUTO_H = (0, 200, 255)
COLOR_AUTO_V = (255, 200, 0)
COLOR_SEM_VERDE = (0, 255, 0)
COLOR_SEM_ROJO = (255, 0, 0)
COLOR_BORDE = (60, 60, 60)

explosiones = []  # Cada explosión = [x, y, timer]

def dibujar_explosiones(screen):
    for ex in list(explosiones):
        x, y, timer = ex
        px = x * TAM_CELDA + TAM_CELDA // 2
        py = y * TAM_CELDA + TAM_CELDA // 2

        pygame.draw.circle(screen, (255, 80, 0), (px, py), TAM_CELDA)
        pygame.draw.circle(screen, (255, 200, 0), (px, py), TAM_CELDA // 2)

        ex[2] -= 1
        if ex[2] <= 0:
            explosiones.remove(ex)



# --- Clases principales ---
class TrafficLight:
    def __init__(self, x, y, horizontal=True, cycle_length=30):
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
        self.tipo = "H" if dy == 0 else "V"

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
        # ---------- DETECCIÓN DE CHOQUE ----------
        other = grid[next_y][next_x]

        if other != 0:
            # Solo chocar si son de tipo distinto (H vs V)
            if isinstance(other, Vehicle) and other.tipo != self.tipo:
                return "crash", other

            return "stop"

        # ---------- MOVER ----------
        grid[self.y][self.x] = 0
        grid[next_y][next_x] = self
        self.x, self.y = next_x, next_y
        return "move"
    
 


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
            v = Vehicle(x, y, dx, dy, color)
            self.grid[y][x] = v
            self.vehicles.append(v)


    def update(self):
        # Actualizar semáforos
        for l in self.lights:
            l.update()

        # Sincronizar: uno verde → otro rojo
        if len(self.lights) == 8:
            # Encontrar los semáforos horizontales y verticales
            h_lights = [l for l in self.lights if l.horizontal]
            v_lights = [l for l in self.lights if not l.horizontal]

            for l in h_lights[1:]:
                l.state = h_lights[0].state 

            # Asegurar que todos los verticales tengan el estado opuesto a los horizontales
            v_lights[0].state = 4 if h_lights[0].state == 3 else 3
            for l in v_lights[1:]:
                l.state = v_lights[0].state

        # Mover vehículos
        # ---------- SISTEMA DE RESERVAS (ANTI-STUCK) ----------
        deseos = {}   # (nx, ny) -> [vehículos que quieren entrar]

        # PRIMERA PASADA: cada vehículo dice a dónde quiere ir
        for v in self.vehicles:
            nx = v.x + v.dx
            ny = v.y + v.dy

            # Salida por borde
            if not (0 <= nx < self.cols and 0 <= ny < self.rows):
                deseos[(v.x, v.y)] = deseos.get((v.x, v.y), []) + [(v, "out")]
                continue

            # Semáforos
            detener = False
            for l in self.lights:
                if l.state == 4:  # Rojo
                    if l.horizontal and v.dy == 0 and l.y == v.y and l.x == nx:
                        detener = True
                        break
                    if not l.horizontal and v.dx == 0 and l.x == v.x and l.y == ny:
                        detener = True
                        break

            if detener:
                deseos[(v.x, v.y)] = deseos.get((v.x, v.y), []) + [(v, "stop")]
                continue

            # Colisión
            otro = self.grid[ny][nx]
            if isinstance(otro, Vehicle) and otro.tipo != v.tipo:
                deseos[(nx, ny)] = deseos.get((nx, ny), []) + [(v, ("crash", otro))]
            else:
                deseos[(nx, ny)] = deseos.get((nx, ny), []) + [(v, "move")]

        # SEGUNDA PASADA: resolver conflictos
        mover = []
        eliminar = set()

        for destino, lista in deseos.items():
            if len(lista) == 1:
                v, accion = lista[0]
            else:
                # Si varios quieren la misma celda → permitir solo 1
                v, accion = random.choice(lista)

            if accion == "out":
                eliminar.add(v)
            elif accion == "stop":
                pass
            elif isinstance(accion, tuple) and accion[0] == "crash":
                otro = accion[1]
                explosiones.append([v.x, v.y, 5])
                eliminar.add(v)
                eliminar.add(otro)
            elif accion == "move":
                mover.append((v, destino))

        # TERCERA PASADA: aplicar movimientos aprobados
        for v in self.vehicles:
            self.grid[v.y][v.x] = 0  # limpiar celdas antes de mover

        for v, (nx, ny) in mover:
            v.x, v.y = nx, ny
            self.grid[ny][nx] = v

        # borrar vehículos muertos
        for v in list(self.vehicles):
            if v in eliminar:
                if self.grid[v.y][v.x] == v:
                    self.grid[v.y][v.x] = 0
                self.vehicles.remove(v)

        #CARRIL 2 IZQ-DER
        if random.random() < 0.05:
            # Horizontal - Carril superior
           self.add_vehicle(0, self.rows // 2 - 1, 1, 0, COLOR_AUTO_H) # Fila cy - 1
        #CARRIL 1 IZQ-DER
        if random.random() < 0.1:
            self.add_vehicle(0, self.rows // 2-2, 1, 0, COLOR_AUTO_H)
        #CARRIL 1 DER-IZQ
        if random.random() < 0.1:
            self.add_vehicle(self.cols -1, self.rows // 2 + 1, -1, 0, COLOR_AUTO_H)
        #CARRIL 2 DER-IZQ
        if random.random() < 0.05:
            self.add_vehicle(self.cols -1, self.rows // 2 +2, -1, 0, COLOR_AUTO_H)      

        #CARRIL 1 ABAJO-ARRIBA
        if random.random() < 0.1:
           self.add_vehicle(self.cols // 2 -2, self.rows - 1, 0, -1, COLOR_AUTO_V) # Columna cx + 1
        #CARRIL 2 ABAJO-ARRIBA
        if random.random() < 0.07:
            self.add_vehicle(self.cols // 2 -1, self.rows - 1, 0, -1, COLOR_AUTO_V)
        # CARRIL 1 ARRIBA-ABAJO
        if random.random() < 0.07:
            self.add_vehicle(self.cols // 2 + 2, 0, 0, 1, COLOR_AUTO_V)
        # CARRIL 2 ARRIBA-ABAJO
        if random.random() < 0.09:
            self.add_vehicle(self.cols // 2 +1, 0, 0, 1, COLOR_AUTO_V)


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
        dibujar_explosiones(screen)

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
    
    # Semáforos HORIZONTALES 
    grid.add_light(cx - 4, cy - 1, horizontal=True, cycle=20)
    grid.add_light(cx-4, cy-2, horizontal=True, cycle=20) 
    grid.add_light(cx +4, cy+1, horizontal=True, cycle=20)
    grid.add_light(cx +4, cy+2 , horizontal=True, cycle=20) 
    

    # Semáforos VERTICALES 
    grid.add_light(cx-1, cy +3, horizontal=False , cycle=20) 
    grid.add_light(cx-2, cy +3  , horizontal=False , cycle=20)
    grid.add_light(cx + 2, cy -3, horizontal=False , cycle=20)
    grid.add_light(cx+1, cy -3, horizontal=False , cycle=20)
    

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

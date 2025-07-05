import pygame
import random
import sys
import os
import math
from auto_player import AutoPlayer

pygame.init()

WIDTH, HEIGHT = 1200, 900
FPS = 60
ANT_COUNT = 30
RESOURCE_FONT = pygame.font.SysFont("Arial", 20)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (80, 200, 120)
BROWN = (139, 69, 19)
RED = (255, 50, 50)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 100)
AQUA = (100, 200, 255)
DARK_BROWN = (100, 50, 10)
SAND = (240, 230, 140)
PINK = (255, 180, 220)

resources = {"food": 500, "wood": 500, "fish": 500}

ANT_ADULT_IMG = pygame.image.load(os.path.join('assets', 'ant_adult.png'))
ANT_CHILD_IMG = pygame.image.load(os.path.join('assets', 'ant_child.png'))
ANT_ADULT_IMG = pygame.transform.scale(ANT_ADULT_IMG, (48, 48))
ANT_CHILD_IMG = pygame.transform.scale(ANT_CHILD_IMG, (32, 32))

BUILDING_ICONS = {
    "hub": pygame.transform.scale(pygame.image.load(os.path.join('assets', 'hub.png')), (24, 24)),
    "lumber camp": pygame.transform.scale(pygame.image.load(os.path.join('assets', 'lumber_camp.png')), (24, 24)),
    "fishing hut": pygame.transform.scale(pygame.image.load(os.path.join('assets', 'fishing_hut.png')), (24, 24)),
    "school": pygame.transform.scale(pygame.image.load(os.path.join('assets', 'school.png')), (24, 24)),
    "bonfire": pygame.transform.scale(pygame.image.load(os.path.join('assets', 'campfire.png')), (24, 24)),
    "home": pygame.transform.scale(pygame.image.load(os.path.join('assets', 'home.png')), (24, 24)),
    "base": pygame.transform.scale(pygame.image.load(os.path.join('assets', 'castle.png')), (24, 24)),
}

BUILDING_IMAGES = {
    "hub": pygame.transform.scale(pygame.image.load(os.path.join('assets', 'hub.png')), (48, 48)),
    "lumber camp": pygame.transform.scale(pygame.image.load(os.path.join('assets', 'lumber_camp.png')), (48, 48)),
    "fishing hut": pygame.transform.scale(pygame.image.load(os.path.join('assets', 'fishing_hut.png')), (48, 48)),
    "school": pygame.transform.scale(pygame.image.load(os.path.join('assets', 'school.png')), (48, 48)),
    "bonfire": pygame.transform.scale(pygame.image.load(os.path.join('assets', 'campfire.png')), (48, 48)),
    "home": pygame.transform.scale(pygame.image.load(os.path.join('assets', 'home.png')), (48, 48)),
    "base": pygame.transform.scale(pygame.image.load(os.path.join('assets', 'castle.png')), (48, 48)),
}

FOOD_ICON = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'food.png')), (24, 24))
WOOD_ICON = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'wood.png')), (24, 24))

class Ant:
    def __init__(self, x, y, is_adult=False):
        self.x = x
        self.y = y
        self.speed = 1 if is_adult else 0.5
        self.target = None
        self.carrying = None
        self.stamina = 100
        self.resting = False
        self.need_food = False
        self.hunger = 0
        self.eating = False
        self.unhappy_ticks = 0
        self.age = 0
        self.is_adult = is_adult
        self.experience = 0
        self.at_school = False
        self.school_target = None
        self.last_dx = 0
        self.last_dy = -1

    def update(self, food_sources, lumber_areas, water_areas, buildings, schools_state):
        self.age += 1 / FPS
        if not self.is_adult and self.experience >= 200:
            self.is_adult = True
            self.speed = 1
            self.at_school = False
            self.school_target = None

        if not self.is_adult:
            if not self.at_school:
                available_schools = [b for b in buildings if b.type == "school" and schools_state.get(id(b), 0) < 5]
                if available_schools:
                    closest = min(available_schools, key=lambda b: (b.x - self.x) ** 2 + (b.y - self.y) ** 2)
                    self.school_target = closest
                    self.move_towards(closest.x, closest.y)
                    if abs(self.x - closest.x) < 5 and abs(self.y - closest.y) < 5:
                        self.at_school = True
                        schools_state[id(closest)] = schools_state.get(id(closest), 0) + 1
                        return
                else:
                    self.school_target = None
            else:
                self.experience += 0.1
                return

        self.hunger += 0.01
        if self.hunger > 100:
            self.hunger = 100

        if self.hunger >= 70 or self.eating:
            food_buildings = [b for b in buildings if b.type == "home"]
            if resources["food"] > 0 or resources["fish"] > 0:
                food_buildings += [b for b in buildings if b.type == "fishing hut"]
            if food_buildings:
                closest = min(food_buildings, key=lambda b: (b.x - self.x) ** 2 + (b.y - self.y) ** 2)
                self.move_towards(closest.x, closest.y)
                if abs(self.x - closest.x) < 5 and abs(self.y - closest.y) < 5:
                    if resources["food"] > 0:
                        resources["food"] -= 1
                        self.hunger = max(0, self.hunger - 15)
                        self.eating = False
                    elif resources["fish"] > 0:
                        resources["fish"] -= 1
                        self.hunger = max(0, self.hunger - 15)
                        self.eating = False
                    else:
                        self.eating = True
                else:
                    self.eating = True
                return
            else:
                self.eating = True
                return
        else:
            self.eating = False

        if self.stamina <= 20:
            self.resting = True
        if self.resting:
            hub = next((b for b in buildings if b.type == "hub"), None)
            if hub:
                self.move_towards(hub.x, hub.y)
                if abs(self.x - hub.x) < 5 and abs(self.y - hub.y) < 5:
                    self.stamina = min(100, self.stamina + 3)
                    if self.stamina >= 80:
                        self.resting = False
                    return
            else:
                self.stamina = min(100, self.stamina + 1)
                return
        else:
            self.stamina -= 0.01

        if self.carrying:
            drop_x, drop_y = 600, 450
            if self.carrying == "fish":
                huts = [b for b in buildings if b.type == "fishing hut"]
                if huts:
                    closest = min(huts, key=lambda b: (b.x - self.x) ** 2 + (b.y - self.y) ** 2)
                    drop_x, drop_y = closest.x, closest.y
            elif self.carrying == "wood":
                camps = [b for b in buildings if b.type == "lumber camp"]
                if camps:
                    closest = min(camps, key=lambda b: (b.x - self.x) ** 2 + (b.y - self.y) ** 2)
                    drop_x, drop_y = closest.x, closest.y
            self.move_towards(drop_x, drop_y)
            if abs(self.x - drop_x) < 5 and abs(self.y - drop_y) < 5:
                resources[self.carrying] += 1
                self.carrying = None
        else:
            if self.is_adult or not self.carrying:
                if self.target is None or random.random() < 0.01:
                    all_sources = food_sources + lumber_areas + water_areas
                    self.target = random.choice(all_sources)
                self.move_towards(self.target.x, self.target.y)
                if abs(self.x - self.target.x) < 5 and abs(self.y - self.target.y) < 5:
                    self.carrying = self.target.type

    def move_towards(self, tx, ty):
        dx, dy = tx - self.x, ty - self.y
        dist = max(1, (dx**2 + dy**2)**0.5)
        self.x += self.speed * dx / dist
        self.y += self.speed * dy / dist
        if abs(dx) > 1e-3 or abs(dy) > 1e-3:
            self.last_dx = dx / dist
            self.last_dy = dy / dist

    def draw(self, screen):
        angle = math.degrees(math.atan2(-self.last_dx, -self.last_dy))
        if self.is_adult:
            rotated_img = pygame.transform.rotate(ANT_ADULT_IMG, angle)
            rect = rotated_img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_img, rect.topleft)
            pygame.draw.rect(screen, RED, (rect.centerx-16, rect.top-10, 32, 4))
            pygame.draw.rect(screen, GREEN, (rect.centerx-16, rect.top-10, int(32*self.stamina/100), 4))
        else:
            rotated_img = pygame.transform.rotate(ANT_CHILD_IMG, angle)
            rect = rotated_img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_img, rect.topleft)
            pygame.draw.rect(screen, RED, (rect.centerx-12, rect.top-8, 24, 3))
            pygame.draw.rect(screen, GREEN, (rect.centerx-12, rect.top-8, int(24*self.stamina/100), 3))

    def is_happy(self):
        return self.hunger < 80 and self.stamina > 20

class FoodSource:
    def __init__(self, x, y, type="food"):
        self.x = x
        self.y = y
        self.type = type

    def draw(self, screen):
        if self.type == "food":
            pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), 8)
        elif self.type == "wood":
            pygame.draw.circle(screen, BROWN, (int(self.x), int(self.y)), 8)
        elif self.type == "fish":
            pygame.draw.circle(screen, AQUA, (int(self.x), int(self.y)), 8)

class Area:
    def __init__(self, x, y, w, h, type):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.type = type
        self.rect = pygame.Rect(x, y, w, h)
        self.points = self.generate_blob(x, y, w, h)

    def generate_blob(self, x, y, w, h, n=10):
        points = []
        for i in range(n):
            angle = (i / n) * 2 * math.pi
            radius = random.uniform(0.7, 1.0)
            px = x + w/2 + radius * w/2 * math.cos(angle)
            py = y + h/2 + radius * h/2 * math.sin(angle)
            points.append((px, py))
        return points

    def draw(self, screen):
        if self.type == "water":
            pygame.draw.polygon(screen, AQUA, self.points)
        elif self.type == "mountain":
            pygame.draw.polygon(screen, DARK_BROWN, self.points)
        elif self.type == "sand":
            pygame.draw.polygon(screen, SAND, self.points)
        elif self.type == "flowers":
            pygame.draw.polygon(screen, PINK, self.points)

class Building:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type

    def draw(self, screen):
        if self.type in BUILDING_IMAGES:
            img = BUILDING_IMAGES[self.type]
            rect = img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(img, rect.topleft)

class Queen:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lay_timer = 0
        self.status = "ready"

    def update(self, ants):
        happy_ants = sum(1 for ant in ants if ant.is_happy())
        if happy_ants == len(ants) and len(ants) > 0:
            self.status = "ready"
        else:
            self.status = "hungry"

    def can_lay(self):
        return self.status == "ready"

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 15)
        pygame.draw.circle(screen, PINK, (int(self.x), int(self.y)), 10)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ant Colony - Auto Player")
clock = pygame.time.Clock()

ants = []
for _ in range(ANT_COUNT // 2):
    ants.append(Ant(WIDTH//2, HEIGHT//2, is_adult=True))
for _ in range(ANT_COUNT - len(ants)):
    ants.append(Ant(WIDTH//2, HEIGHT//2, is_adult=False))

areas = []
base_x, base_y = WIDTH//2, HEIGHT//2
base_rect = pygame.Rect(base_x-40, base_y-40, 80, 80)

def overlaps_any(rect, area_list):
    for a in area_list:
        if rect.colliderect(a.rect):
            return True
    return False

for _ in range(random.randint(4, 8)):
    for _ in range(30):
        wx = random.randint(0, WIDTH-200)
        wy = random.randint(0, HEIGHT-200)
        ww = random.randint(100, 250)
        wh = random.randint(80, 180)
        temp_area = Area(wx, wy, ww, wh, "water")
        if not temp_area.rect.colliderect(base_rect) and not overlaps_any(temp_area.rect, areas):
            areas.append(temp_area)
            break
for _ in range(random.randint(3, 6)):
    for _ in range(30):
        mx = random.randint(0, WIDTH-180)
        my = random.randint(0, HEIGHT-180)
        mw = random.randint(80, 180)
        mh = random.randint(80, 180)
        temp_area = Area(mx, my, mw, mh, "mountain")
        if not temp_area.rect.colliderect(base_rect) and not overlaps_any(temp_area.rect, areas):
            areas.append(temp_area)
            break
for _ in range(random.randint(2, 4)):
    for _ in range(30):
        sx = random.randint(0, WIDTH-150)
        sy = random.randint(0, HEIGHT-150)
        sw = random.randint(80, 150)
        sh = random.randint(60, 120)
        temp_area = Area(sx, sy, sw, sh, "sand")
        if not temp_area.rect.colliderect(base_rect) and not overlaps_any(temp_area.rect, areas):
            areas.append(temp_area)
            break
for _ in range(random.randint(2, 4)):
    for _ in range(30):
        fx = random.randint(0, WIDTH-120)
        fy = random.randint(0, HEIGHT-120)
        fw = random.randint(60, 120)
        fh = random.randint(60, 120)
        temp_area = Area(fx, fy, fw, fh, "flowers")
        if not temp_area.rect.colliderect(base_rect) and not overlaps_any(temp_area.rect, areas):
            areas.append(temp_area)
            break

food_sources = [FoodSource(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50), random.choice(["food"])) for _ in range(25)]
lumber_areas = [FoodSource(random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100), "wood") for _ in range(15)]
water_areas = [FoodSource(random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100), "fish") for _ in range(15)]

buildings = [Building(WIDTH//2, HEIGHT//2, "base")]

building_costs = {
    "base": {"food": 0, "wood": 0},
    "home": {"food": 10, "wood": 5},
    "bonfire": {"food": 5, "wood": 10},
    "school": {"food": 15, "wood": 10},
    "fishing hut": {"food": 10, "wood": 15},
    "lumber camp": {"food": 8, "wood": 20},
    "hub": {"food": 20, "wood": 20},
}

def can_afford(building_type):
    cost = building_costs[building_type]
    return all(resources.get(r, 0) >= cost[r] for r in cost)

def pay_cost(building_type):
    cost = building_costs[building_type]
    for r in cost:
        resources[r] -= cost[r]

def point_near_polygon_edge(point, polygon, max_dist=20):
    px, py = point
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i+1)%n]
        dx, dy = x2-x1, y2-y1
        if dx == dy == 0:
            dist = ((px-x1)**2 + (py-y1)**2)**0.5
        else:
            t = max(0, min(1, ((px-x1)*dx + (py-y1)*dy)/(dx*dx+dy*dy)))
            proj_x = x1 + t*dx
            proj_y = y1 + t*dy
            dist = ((px-proj_x)**2 + (py-proj_y)**2)**0.5
        if dist <= max_dist:
            return True
    return False

def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    n = len(polygon)
    px1, py1 = polygon[0]
    for i in range(n+1):
        px2, py2 = polygon[i % n]
        if y > min(py1, py2):
            if y <= max(py1, py2):
                if x <= max(px1, px2):
                    if py1 != py2:
                        xinters = (y-py1)*(px2-px1)/(py2-py1)+px1
                    if px1 == px2 or x <= xinters:
                        inside = not inside
        px1, py1 = px2, py2
    return inside

def draw_ui(auto_player_action=None):
    y = 70
    screen.blit(FOOD_ICON, (10, y))
    txt = RESOURCE_FONT.render(f"{resources['food']}", True, BLACK)
    screen.blit(txt, (38, y+2))
    y += 28
    screen.blit(WOOD_ICON, (10, y))
    txt = RESOURCE_FONT.render(f"{resources['wood']}", True, BLACK)
    screen.blit(txt, (38, y+2))
    y += 28
    if 'fish' in resources:
        fish_txt = RESOURCE_FONT.render(f"Fish: {resources['fish']}", True, BLACK)
        screen.blit(fish_txt, (10, y))
        y += 25
    ant_txt = RESOURCE_FONT.render(f"Ants: {len(ants)}", True, BLACK)
    screen.blit(ant_txt, (10, y))
    y += 25
    happy_txt = RESOURCE_FONT.render(f"Happy: {sum(1 for a in ants if a.is_happy())} / {len(ants)}", True, (0, 150, 0))
    screen.blit(happy_txt, (10, y))
    y += 25
    queen_txt = RESOURCE_FONT.render(f"Queen: {queen.status}", True, (200, 0, 0) if queen.status == "hungry" else (0, 0, 0))
    screen.blit(queen_txt, (10, y))
    y += 25
    ca_txt = RESOURCE_FONT.render(f"Children: {sum(1 for a in ants if not a.is_adult)}  Adults: {sum(1 for a in ants if a.is_adult)}", True, (0, 0, 0))
    screen.blit(ca_txt, (10, y))
    y += 25
    homes = [b for b in buildings if b.type == "home"]
    housed = min(len(ants), len(homes)*5)
    homeless = max(0, len(ants) - len(homes)*5)
    home_txt = RESOURCE_FONT.render(f"Housed: {housed} / {len(ants)}", True, BLACK)
    screen.blit(home_txt, (10, y))
    y += 25
    homeless_txt = RESOURCE_FONT.render(f"Homeless: {homeless}", True, (200, 0, 0) if homeless else (0, 100, 0))
    screen.blit(homeless_txt, (10, y))
    y += 25
    
    if auto_player_action and auto_player_action["action"] == "build":
        action_txt = RESOURCE_FONT.render(f"AI: Building {auto_player_action['building_type']}", True, (0, 0, 200))
        screen.blit(action_txt, (10, y))
        y += 25
        reason_txt = RESOURCE_FONT.render(f"Reason: {auto_player_action['reason']}", True, (100, 100, 100))
        screen.blit(reason_txt, (10, y))
    
    y += 25
    debug_txt = RESOURCE_FONT.render(f"Food: {resources.get('food', 0)} + Fish: {resources.get('fish', 0)} = {resources.get('food', 0) + resources.get('fish', 0)}", True, (100, 100, 100))
    screen.blit(debug_txt, (10, y))
    y += 25
    avg_hunger = sum(ant.hunger for ant in ants) / max(1, len(ants))
    avg_stamina = sum(ant.stamina for ant in ants) / max(1, len(ants))
    debug2_txt = RESOURCE_FONT.render(f"Avg Hunger: {avg_hunger:.1f}, Avg Stamina: {avg_stamina:.1f}", True, (100, 100, 100))
    screen.blit(debug2_txt, (10, y))

base_building = [b for b in buildings if b.type == "base"]
if base_building:
    queen = Queen(base_building[0].x, base_building[0].y)
else:
    queen = Queen(WIDTH//2, HEIGHT//2)

auto_player = AutoPlayer()
frame_count = 0

print("Auto Player initialized!")
print("Starting automatic ant colony management...")
print("The AI will:")
print("- Prioritize homes for housing ants")
print("- Build hubs for resting")
print("- Place resource buildings near their resources")
print("- Build schools for children")
print("- Add bonfires for morale when needed")

while True:
    frame_count += 1
    screen.fill((200, 255, 200))

    for area in areas:
        area.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    auto_action = auto_player.update(ants, buildings, resources, areas, food_sources, lumber_areas, water_areas, building_costs, frame_count)
    
    if auto_action["action"] == "build":
        building_type = auto_action["building_type"]
        position = auto_action["position"]
        
        if can_afford(building_type):
            if building_type == "fishing hut":
                can_place = False
                for area in areas:
                    if area.type == "water" and point_near_polygon_edge(position, area.points, 20):
                        can_place = True
                        break
                if not can_place:
                    continue
            
            buildings.append(Building(position[0], position[1], building_type))
            pay_cost(building_type)
            print(f"AI built {building_type} at {position}")

    happy_ants = 0
    unhappy_ants = 0
    children = 0
    adults = 0
    schools_state = {}
    for ant in ants[:]:
        ant.update(food_sources, lumber_areas, water_areas, buildings, schools_state)
        ant.draw(screen)
        if ant.is_happy():
            ant.unhappy_ticks = 0
            happy_ants += 1
        else:
            ant.unhappy_ticks += 1
            unhappy_ants += 1
            if ant.unhappy_ticks > FPS * 20:
                ants.remove(ant)
        if ant.is_adult:
            adults += 1
        else:
            children += 1

    queen.update(ants)
    if happy_ants == len(ants) and len(ants) > 0 and queen.can_lay():
        queen.lay_timer += 1
        if queen.lay_timer > FPS * 10:
            ants.append(Ant(queen.x, queen.y, is_adult=False))
            queen.lay_timer = 0
    else:
        queen.lay_timer = 0

    for src in food_sources:
        src.draw(screen)
    for src in lumber_areas:
        src.draw(screen)
    for src in water_areas:
        src.draw(screen)

    for b in buildings:
        b.draw(screen)

    queen.draw(screen)

    draw_ui(auto_action)
    pygame.display.flip()
    clock.tick(FPS) 
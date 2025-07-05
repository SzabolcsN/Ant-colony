import pygame
import random
import math
from typing import List, Tuple, Dict, Any

class AutoPlayer:
    def __init__(self):
        self.last_building_time = 0
        self.building_cooldown = 60
        self.last_analysis_time = 0
        self.analysis_cooldown = 120
        
        self.building_priorities = {
            "home": 100,
            "hub": 80,
            "lumber camp": 60,
            "fishing hut": 50,
            "school": 30,
            "bonfire": 20,
        }
        
        self.resource_thresholds = {
            "food": 15,
            "wood": 10,
        }
        
        self.placement_zones = {
            "lumber camp": "mountain",
            "fishing hut": "water",
            "home": "base",
            "hub": "base",
            "school": "base",
            "bonfire": "base",
        }
    
    def analyze_colony_needs(self, ants, buildings, resources, areas, food_sources, lumber_areas, water_areas):
        analysis = {
            "total_ants": len(ants),
            "adult_ants": sum(1 for ant in ants if ant.is_adult),
            "children": sum(1 for ant in ants if not ant.is_adult),
            "happy_ants": sum(1 for ant in ants if ant.is_happy()),
            "homeless_ants": 0,
            "building_counts": {},
            "resource_shortages": [],
            "recommended_buildings": []
        }
        
        for building in buildings:
            analysis["building_counts"][building.type] = analysis["building_counts"].get(building.type, 0) + 1
        
        homes = analysis["building_counts"].get("home", 0)
        housing_capacity = homes * 5
        analysis["homeless_ants"] = max(0, len(ants) - housing_capacity)
        
        if resources["food"] < self.resource_thresholds["food"]:
            analysis["resource_shortages"].append("food")
        if resources["wood"] < self.resource_thresholds["wood"]:
            analysis["resource_shortages"].append("wood")
        
        recommendations = []
        
        if analysis["homeless_ants"] > 0:
            homes_needed = (analysis["homeless_ants"] + 4) // 5
            recommendations.append(("home", homes_needed, 100))
        
        hubs = analysis["building_counts"].get("hub", 0)
        if hubs == 0 or len(ants) > hubs * 8:
            recommendations.append(("hub", 1, 80))
        
        if "wood" in analysis["resource_shortages"]:
            lumber_camps = analysis["building_counts"].get("lumber camp", 0)
            if lumber_camps < 3:
                recommendations.append(("lumber camp", 1, 60))
        
        if "food" in analysis["resource_shortages"]:
            fishing_huts = analysis["building_counts"].get("fishing hut", 0)
            if fishing_huts < 3:
                recommendations.append(("fishing hut", 1, 50))
        
        if analysis["children"] > 0:
            schools = analysis["building_counts"].get("school", 0)
            children_per_school = 5
            schools_needed = (analysis["children"] + children_per_school - 1) // children_per_school
            if schools < schools_needed:
                recommendations.append(("school", 1, 30))
        
        unhappy_ratio = 1 - (analysis["happy_ants"] / max(1, len(ants)))
        if unhappy_ratio > 0.3:
            bonfires = analysis["building_counts"].get("bonfire", 0)
            if bonfires < 2:
                recommendations.append(("bonfire", 1, 20))
        
        recommendations.sort(key=lambda x: x[2], reverse=True)
        analysis["recommended_buildings"] = recommendations
        
        return analysis
    
    def find_optimal_placement(self, building_type, areas, buildings, food_sources, lumber_areas, water_areas):
        WIDTH, HEIGHT = 1200, 900
        base_x, base_y = WIDTH // 2, HEIGHT // 2
        
        if building_type == "lumber camp":
            best_pos = self._find_near_resource(lumber_areas, areas, "mountain", buildings)
            if best_pos:
                return best_pos
        
        elif building_type == "fishing hut":
            best_pos = self._find_near_water(areas, buildings)
            if best_pos:
                return best_pos
        
        elif building_type in ["home", "hub", "school", "bonfire"]:
            best_pos = self._find_near_base(base_x, base_y, buildings, building_type)
            if best_pos:
                return best_pos
        
        return self._find_random_position(buildings, WIDTH, HEIGHT)
    
    def _find_near_resource(self, resource_sources, areas, area_type, buildings):
        if resource_sources:
            source = random.choice(resource_sources)
            for _ in range(20):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(30, 80)
                x = source.x + distance * math.cos(angle)
                y = source.y + distance * math.sin(angle)
                
                if 50 < x < 1150 and 50 < y < 850:
                    if not self._too_close_to_buildings(x, y, buildings):
                        return (int(x), int(y))
        
        target_areas = [area for area in areas if area.type == area_type]
        if target_areas:
            area = random.choice(target_areas)
            for _ in range(20):
                edge_x = area.x + random.choice([0, area.w])
                edge_y = area.y + random.choice([0, area.h])
                
                x = edge_x + random.uniform(-50, 50)
                y = edge_y + random.uniform(-50, 50)
                
                if 50 < x < 1150 and 50 < y < 850:
                    if not self._too_close_to_buildings(x, y, buildings):
                        return (int(x), int(y))
        
        return None
    
    def _find_near_water(self, areas, buildings):
        water_areas = [area for area in areas if area.type == "water"]
        if water_areas:
            area = random.choice(water_areas)
            for _ in range(30):
                if random.random() < 0.5:
                    x = area.x + random.uniform(0, area.w)
                    y = area.y + random.choice([-30, area.h + 30])
                else:
                    x = area.x + random.choice([-30, area.w + 30])
                    y = area.y + random.uniform(0, area.h)
                
                if 50 < x < 1150 and 50 < y < 850:
                    if not self._too_close_to_buildings(x, y, buildings):
                        return (int(x), int(y))
        
        return None
    
    def _find_near_base(self, base_x, base_y, buildings, building_type):
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(40, 120)
            x = base_x + distance * math.cos(angle)
            y = base_y + distance * math.sin(angle)
            
            if 50 < x < 1150 and 50 < y < 850:
                if not self._too_close_to_buildings(x, y, buildings):
                    return (int(x), int(y))
        
        return None
    
    def _find_random_position(self, buildings, WIDTH, HEIGHT):
        for _ in range(50):
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 50)
            
            if not self._too_close_to_buildings(x, y, buildings):
                return (int(x), int(y))
        
        return (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
    
    def _too_close_to_buildings(self, x, y, buildings, min_distance=40):
        for building in buildings:
            distance = math.sqrt((x - building.x) ** 2 + (y - building.y) ** 2)
            if distance < min_distance:
                return True
        return False
    
    def can_afford_building(self, building_type, resources, building_costs):
        if building_type not in building_costs:
            return False
        
        cost = building_costs[building_type]
        return all(resources.get(resource, 0) >= cost[resource] for resource in cost)
    
    def update(self, ants, buildings, resources, areas, food_sources, lumber_areas, water_areas, building_costs, current_frame):
        if current_frame - self.last_analysis_time > self.analysis_cooldown:
            analysis = self.analyze_colony_needs(ants, buildings, resources, areas, food_sources, lumber_areas, water_areas)
            self.last_analysis_time = current_frame
            
            if current_frame - self.last_building_time > self.building_cooldown:
                for building_type, count, priority in analysis["recommended_buildings"]:
                    if self.can_afford_building(building_type, resources, building_costs):
                        position = self.find_optimal_placement(building_type, areas, buildings, food_sources, lumber_areas, water_areas)
                        if position:
                            return {
                                "action": "build",
                                "building_type": building_type,
                                "position": position,
                                "priority": priority,
                                "reason": f"Priority {priority}: {building_type}"
                            }
                
                self.last_building_time = current_frame
        
        return {"action": "none"}

def run_auto_game():
    import sys
    import os
    
    sys.path.append('.')
    
    pygame.init()
    
    WIDTH, HEIGHT = 1200, 900
    FPS = 60
    ANT_COUNT = 30
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ant Colony - Auto Player")
    clock = pygame.time.Clock()
    auto_player = AutoPlayer()
    return auto_player

if __name__ == "__main__":
    # The AI will:
    # - Prioritize homes for housing ants
    # - Build hubs for resting
    # - ~Place resource buildings near their resources
    # - Build schools
    # - Add bonfires for morale when needed
    auto_player = run_auto_game()

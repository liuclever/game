
import requests
import json

BASE_URL = "http://localhost:5000/api/beast"

def check_api_detail(beast_id):
    # We need a token or session, but maybe we can bypass or just see what's in the DB if we can't hit the API easily.
    # Actually, I'll just use the DB repo directly in a script to see what it returns to the route.
    
    import sys
    import os
    sys.path.append(os.getcwd())
    
    from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo
    from interfaces.routes.beast_routes import _calc_beast_stats
    
    repo = MySQLPlayerBeastRepo()
    beast = repo.get_by_id(beast_id)
    if not beast:
        print(f"Beast {beast_id} not found")
        return

    print(f"Original DB Physical Aptitude: {beast.physical_attack_aptitude}")
    
    # Simulate the calculation done in the route
    beast = _calc_beast_stats(beast)
    
    beast_dict = beast.to_dict()
    print(f"After _calc_beast_stats Physical Aptitude: {beast_dict['physical_attack_aptitude']}")
    
    # Check the aptitude stars calculation
    from domain.services.beast_stats import calc_beast_aptitude_stars
    aptitudes = {
        'hp': beast.hp_aptitude,
        'speed': beast.speed_aptitude,
        'physical_attack': beast.physical_attack_aptitude,
        'magic_attack': beast.magic_attack_aptitude,
        'physical_defense': beast.physical_defense_aptitude,
        'magic_defense': beast.magic_defense_aptitude,
    }
    stars = calc_beast_aptitude_stars(beast.name, beast.realm, aptitudes)
    print(f"Stars: {json.dumps(stars, indent=2)}")

if __name__ == "__main__":
    check_api_detail(696)

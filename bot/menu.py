import json
from typing import List, Dict, Any

class MenuManager:
    def __init__(self, menu_file: str):
        self.menu_file = menu_file
        self.load_menu()

    def load_menu(self):
        try:
            with open(self.menu_file, 'r', encoding='utf-8') as f:
                self.menu = json.load(f)
        except FileNotFoundError:
            self.menu = {}

    def save_menu(self):
        with open(self.menu_file, 'w', encoding='utf-8') as f:
            json.dump(self.menu, f, ensure_ascii=False, indent=4)

    def get_menu(self, path: List[str]) -> Dict[str, Any]:
        menu = self.menu
        for p in path:
            menu = menu.get(p, {}).get('sub_menu', {})
        return menu

    def add_menu_item(self, path: List[str], name: str, response: str = None):
        menu = self.menu
        for p in path:
            menu = menu.setdefault(p, {'sub_menu': {}})['sub_menu']
        if response:
            menu[name] = {'response': response}
        else:
            menu[name] = {'sub_menu': {}}
        self.save_menu()

    def delete_menu_item(self, path: List[str], name: str) -> bool:
        menu = self.menu
        for p in path:
            menu = menu.get(p, {}).get('sub_menu', {})
        if name in menu:
            del menu[name]
            self.save_menu()
            return True
        return False

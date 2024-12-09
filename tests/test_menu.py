import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from unittest.mock import patch, mock_open
import pytest

from bot.menu import MenuManager


TEST_MENU_DATA = json.dumps({
    "Образовательная программа": {
        "sub_menu": {
            "Бакалавр": {
                "sub_menu": {
                    "Документы на поступление": {
                        "response": "Для поступления нужны документы: ...",
                        "photo": "https://example.com/image.jpg"
                    },
                    "Образовательные программы": {
                        "sub_menu": {
                            "Факультет педагогики": {
                                "response": "Информация о факультете педагогики"
                            }
                        }
                    }
                }
            }
        }
    }
})


@pytest.fixture
def menu_manager():
    """Фикстура для создания экземпляра MenuManager с замоканным файлом."""
    with patch("builtins.open", mock_open(read_data=TEST_MENU_DATA)):
        m = MenuManager("some_menu.json")  # Имя файла не важно, так как мы замокали open
    return m


def test_load_menu(menu_manager):
    """Проверяем, что меню загружено корректно."""
    assert "Образовательная программа" in menu_manager.menu
    assert "sub_menu" in menu_manager.menu["Образовательная программа"]


def test_get_menu_root_level(menu_manager):
    """Проверяем, что get_menu без пути возвращает корневой уровень."""
    menu = menu_manager.get_menu([])
    assert "Образовательная программа" in menu
    assert "sub_menu" in menu["Образовательная программа"]


def test_get_menu_nested(menu_manager):
    """Проверяем переход к вложенному уровню."""
    # Спускаемся к "Образовательная программа" -> "Бакалавр"
    menu = menu_manager.get_menu(["Образовательная программа", "Бакалавр"])
    assert "Документы на поступление" in menu
    assert "Образовательные программы" in menu


def test_get_menu_non_existing_path(menu_manager):
    """Проверяем реакцию на несуществующий путь."""
    menu = menu_manager.get_menu(["Образовательная программа", "Магистратура"])
    # Если путь не существует, ожидается, что вернется пустой словарь
    assert menu == {}


def test_no_file_found():
    """Проверяем работу при отсутствии файла (меню должно быть пустым)."""
    with patch("builtins.open", side_effect=FileNotFoundError()):
        m = MenuManager("no_file.json")
        assert m.menu == {}

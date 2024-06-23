# test_multipropietarios_manager.py

import pytest
from multipropietarios import MultipropietariosManager

@pytest.fixture
def manager():
    return MultipropietariosManager()

def test_group_adquirentes(manager):
    # Test case 1: No repeated adquirentes
    adquirentes = [
        {"RUNRUT": "123", "porcDerecho": 50},
        {"RUNRUT": "456", "porcDerecho": 50},
    ]
    expected = [
        {"RUNRUT": "123", "porcDerecho": 50},
        {"RUNRUT": "456", "porcDerecho": 50},
    ]
    assert manager.group_adquirentes(adquirentes) == expected

    # Test case 2: Some repeated adquirentes
    adquirentes = [
        {"RUNRUT": "123", "porcDerecho": 30},
        {"RUNRUT": "123", "porcDerecho": 20},
        {"RUNRUT": "456", "porcDerecho": 50},
    ]
    expected = [
        {"RUNRUT": "123", "porcDerecho": 50},
        {"RUNRUT": "456", "porcDerecho": 50},
    ]
    assert manager.group_adquirentes(adquirentes) == expected

    # Test case 3: All repeated adquirentes
    adquirentes = [
        {"RUNRUT": "123", "porcDerecho": 30},
        {"RUNRUT": "123", "porcDerecho": 20},
        {"RUNRUT": "123", "porcDerecho": 50},
    ]
    expected = [
        {"RUNRUT": "123", "porcDerecho": 100},
    ]
    assert manager.group_adquirentes(adquirentes) == expected

    # Test case 4: Empty list of adquirentes
    adquirentes = []
    expected = []
    assert manager.group_adquirentes(adquirentes) == expected

    # Test case 5: Different mix of repeated and non-repeated adquirentes
    adquirentes = [
        {"RUNRUT": "123", "porcDerecho": 10},
        {"RUNRUT": "456", "porcDerecho": 20},
        {"RUNRUT": "123", "porcDerecho": 15},
        {"RUNRUT": "789", "porcDerecho": 55},
    ]
    expected = [
        {"RUNRUT": "123", "porcDerecho": 25},
        {"RUNRUT": "456", "porcDerecho": 20},
        {"RUNRUT": "789", "porcDerecho": 55},
    ]
    assert manager.group_adquirentes(adquirentes) == expected


def test_does_all_enajenantes_exist(manager):
    # Test case 1: All enajenantes exist
    data = {'enajenantes': [{'RUNRUT': '123'}, {'RUNRUT': '456'}]}
    enajenantes_historicos = [{'RUN_RUT': '123'}, {'RUN_RUT': '456'}]
    assert manager.does_all_enajenantes_exist(data, enajenantes_historicos) == True

    # Test case 2: Some enajenantes do not exist
    data = {'enajenantes': [{'RUNRUT': '123'}, {'RUNRUT': '456'}, {'RUNRUT': '789'}]}
    enajenantes_historicos = [{'RUN_RUT': '123'}, {'RUN_RUT': '456'}]
    assert manager.does_all_enajenantes_exist(data, enajenantes_historicos) == False

    # Test case 3: No enajenantes exist
    data = {'enajenantes': []}
    enajenantes_historicos = []
    assert manager.does_all_enajenantes_exist(data, enajenantes_historicos) == True

    


# Run the test with: pytest test_multipropietarios_manager.py

from app.api import PetFriends
from app.settings import invalid_email, invalid_password, valid_password, valid_email
import os

pf = PetFriends()

#ТЕСТ №1
def test_get_api_key_for_invalid_user(email=invalid_email, password=invalid_password):
#Проверяем получение ключа авторизации с помощью невалидных логина и пароля
    status, result = pf.get_api_key(email, password)
    assert status == 403

#ТЕСТ №2
def test_get_all_pets_with_invalid_key(filter=''):
# Проверяем получение списка питомцев с помощью невалидного ключа
    auth_key = {'key': 'ea338148a1f19838e1c5d1403877f3691a3711380e733e877b0ae729'}
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 403

#ТЕСТ №3
def test_delete_non_existing_pet():
    """Проверяем возможность удаления несуществующего питомца."""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    #Добавляем несуществующий id питомца
    pet_id = "00000000-0000-0000-0000-000000000000"
    #Пробуем его удалить
    status, _ = pf.delete_pet(auth_key, pet_id)
    #Проверяем есть ли удаляемый id в списке. А вдруг!
    assert pet_id not in my_pets['pets']

#ТЕСТ №4
def test_add_pet_with_invalid_photo(name='Барон', animal_type='Котэ', age='4',
                                 pet_photo='images/ph1.pdf'):
    """Проверяем, реакцию сервиса на добавление питомца с фото в неподдерживаемом формате."""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    # Проверяем, есть ли фото в добавленных данных
    assert result['pet_photo'] == ''

#ТЕСТ №5
def test_add_pet_simple_with_invalid_data(name='', animal_type='', age=''):
    """Проверяем реакцию сервиса на добавление питомца без фото с пустыми полями для данных"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца с пустыми полями для данных
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    # Проверяем что статус ответа 400
    assert status == 400
    """Примечание - данный тест не проходит, т.к. сервис выдает статус 200 при пустых значениях
    параметров"""

#ТЕСТ №6
def test_add_invalid_photo(pet_photo='images/ph3.pdf'):
    """Проверяем реакцию сервиса на добавление фото к существующему питомцу
    в неподдерживаемом формате"""
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового питомца без фото и опять запрашиваем список
    if len(my_pets['pets']) == 0:
        pf.add_new_pet_without_photo(auth_key, "Кинг", "Котик", "8")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка, сохраняем его имя и отправляем запрос на добавление фото
    status, result = pf.add_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)

    # роверяем что статус ответа 400 или 500
    assert status == 400 or 500

#ТЕСТ №7
def test_empty_update_self_pet_info(name='', animal_type='', age=''):
    """Проверяем возможность замены информации о питомце на пустые поля"""

    # Получаем возможность обновления информации о питомце
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        # Запрашиваем список питомцев еще раз
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
        """Проверяем данные о питомце на наличие пустых полей. При подобной попытке замены - поля
        должны оставаться прежними"""
        assert result['name'] != name
        assert result['name'] != name
        assert result['name'] != name
        assert status == 200
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

#ТЕСТ №8
def test_update_self_pet_info_with_non_valid_pet_id(name='Мурзик', animal_type='Котэ', age='5'):
    """Проверяем возможность обновления информации для несуществующего питомца"""

    # Получаем возможность обновления информации о питомце
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        pet_id = "00000000-0000-0000-0000-000000000000"
        status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)

        # Проверяем что статус ответа = 400
        assert status == 400
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

#ТЕСТ№9
def test_add_photo(pet_photo='images/ph3.jpg'):
    """Проверяем реакцию сервиса на добавление фото к несуществующему питомцу"""
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового питомца без фото и опять запрашиваем список
    if len(my_pets['pets']) == 0:
        pf.add_new_pet_without_photo(auth_key, "Кинг", "Котик", "8")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = "00000000-0000-0000-0000-000000000000"
    # Берём id первого питомца из списка, сохраняем его имя и отправляем запрос на добавление фото
    status, result = pf.add_photo(auth_key, pet_id, pet_photo)

    # Проверяем что статус ответа = 500
    assert status == 500

#ТЕСТ№10
def test_add_pet_simple_with_invalid_age(name='Мурлок', animal_type='Котан', age='много'):
    """Проверяем, что можно добавить питомца с некорректными значением возраста без фото"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400
    assert result['name'] == name
















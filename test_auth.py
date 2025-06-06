from auth import register_user, login_user, delete_user, get_user_id

print(register_user("usuario1", "clave123"))
print(login_user("usuario1", "clave123"))
# print(delete_user(get_user_id("empleadoPrueba")))
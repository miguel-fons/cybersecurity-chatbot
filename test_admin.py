from admin import create_user_admin_view, get_all_users, export_metrics_to_csv, delete_user_by_admin

print(create_user_admin_view("empleadoPrueba", "claveABC"))
print(get_all_users())
print(export_metrics_to_csv("data/reporte.csv"))
print(delete_user_by_admin(1))  # ID del usuario a eliminar

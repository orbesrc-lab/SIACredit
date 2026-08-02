import pandas as pd
import os

data = {
    'Área': ['Comercial', 'Operaciones', 'Tecnología'],
    'Cargo': ['Gerente de Ventas', 'Analista', 'Desarrollador'],
    'Cédula': ['123456789', '987654321', '1122334455'],
    'Nombre': ['Juan Pérez', 'Ana Gómez', 'Carlos Ruiz'],
    'Correo': ['juan.perez@empresa.com', 'ana.gomez@empresa.com', 'carlos.ruiz@empresa.com']
}

df = pd.DataFrame(data)
os.makedirs(r'c:\SIAC\static', exist_ok=True)
df.to_excel(r'c:\SIAC\static\plantilla_empleados.xlsx', index=False)
print("Plantilla creada en static/plantilla_empleados.xlsx")

import pandas as pd
import os

def procesar_instituciones():
    excel_path = r'c:\SIAC\estrategia_comercial\Instituciones.xlsx'
    csv_path = r'c:\SIAC\estrategia_comercial\leads_instituciones_filtradas.csv'
    
    print("Leyendo archivo Excel...")
    df = pd.read_excel(excel_path)
    
    # Arreglar problemas de codificación de columnas que salen raras en PowerShell
    # Las columnas reales probablemente tengan tildes.
    # Encontramos la columna que contiene "DEPARTAMENTO" o similar.
    dept_col = [c for c in df.columns if 'DEPARTAMENTO' in c or 'DEPARTAMENTO_DOMICILIO' in c][0]
    nombre_col = [c for c in df.columns if 'NOMBRE' in c][0]
    codigo_col = [c for c in df.columns if 'CDIGO_INSTITUCIN' in c or 'CÓDIGO_INSTITUCIÓN' in c][0]
    caracter_col = [c for c in df.columns if 'CARCTER' in c or 'CARÁCTER' in c][0]
    
    # Filtrar por departamentos
    departamentos_deseados = ["VALLE DEL CAUCA", "PUTUMAYO", "VAUPES", "CAUCA"]
    df_filtrado = df[df[dept_col].astype(str).str.upper().isin(departamentos_deseados)]
    
    leads = []
    
    for _, row in df_filtrado.iterrows():
        # Vamos a mapear la información al formato del CRM
        lead = {
            "Nombre": "",  # No viene en el Excel
            "Cargo": "Rector / Director",  # Cargo sugerido
            "Institucion": str(row[nombre_col]),
            "SNIES": str(row[codigo_col]),
            "Correo": "",
            "LinkedIn": "",
            "Notas": f"[{row[dept_col]}] {row[caracter_col]}"
        }
        leads.append(lead)
        
    print(f"Total instituciones filtradas: {len(leads)}")
    
    # Escribir a CSV
    df_out = pd.DataFrame(leads)
    df_out.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ Archivo CSV guardado exitosamente en: {csv_path}")

if __name__ == "__main__":
    procesar_instituciones()

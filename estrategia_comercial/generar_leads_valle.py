import csv
import os

def generar_base_pruebas():
    # Instituciones Privadas del Valle del Cauca (Prueba inicial)
    leads = [
        {
            "Nombre": "Esteban Piedrahita Uribe",
            "Cargo": "Rector",
            "Institucion": "Universidad Icesi",
            "SNIES": "1204",
            "Correo": "rectoria@icesi.edu.co",
            "LinkedIn": "https://www.linkedin.com/in/esteban-piedrahita-uribe/",
            "Notas": "IES Privada de alta calidad en Cali"
        },
        {
            "Nombre": "Vicente Durán Casas",
            "Cargo": "Rector",
            "Institucion": "Pontificia Universidad Javeriana Cali",
            "SNIES": "1202",
            "Correo": "rectoria@javerianacali.edu.co",
            "LinkedIn": "",
            "Notas": "IES Privada. Importante enfoque en acreditación institucional."
        },
        {
            "Nombre": "Diego Hernández Losada",
            "Cargo": "Rector",
            "Institucion": "Universidad Autónoma de Occidente",
            "SNIES": "2711",
            "Correo": "rectoria@uao.edu.co",
            "LinkedIn": "",
            "Notas": "IES Privada (UAO). Sede principal Cali."
        },
        {
            "Nombre": "Fray Ernesto Londoño Orozco",
            "Cargo": "Rector",
            "Institucion": "Universidad de San Buenaventura Cali",
            "SNIES": "1711",
            "Correo": "rectoria@usbcali.edu.co",
            "LinkedIn": "",
            "Notas": "IES Privada. Fuerte presencia regional."
        },
        {
            "Nombre": "",
            "Cargo": "Director de Aseguramiento de Calidad",
            "Institucion": "Universidad Libre Seccional Cali",
            "SNIES": "2104",
            "Correo": "",
            "LinkedIn": "",
            "Notas": "IES Privada. Buscar contacto de calidad en LinkedIn."
        },
        {
            "Nombre": "Hugo Alberto Valencia Porras",
            "Cargo": "Rector",
            "Institucion": "Fundación Universitaria Católica Lumen Gentium (UNICATÓLICA)",
            "SNIES": "2835",
            "Correo": "rectoria@unicatolica.edu.co",
            "LinkedIn": "",
            "Notas": "IES Privada ubicada en Cali."
        },
        {
            "Nombre": "",
            "Cargo": "Vicerrector Académico",
            "Institucion": "Corporación Universitaria Centro Superior (UNICUCES)",
            "SNIES": "2816",
            "Correo": "",
            "LinkedIn": "",
            "Notas": "IES Privada. Nuestro caso de éxito inicial o prospecto ideal."
        }
    ]

    # Guardar CSV
    output_path = os.path.join(os.path.dirname(__file__), 'leads_valle_cauca.csv')
    
    # Escribir con codificación UTF-8
    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Nombre", "Cargo", "Institucion", "SNIES", "Correo", "LinkedIn", "Notas"])
        writer.writeheader()
        writer.writerows(leads)
        
    print(f"✅ Base de datos generada exitosamente en: {output_path}")
    print(f"Total leads de prueba: {len(leads)}")

if __name__ == "__main__":
    generar_base_pruebas()

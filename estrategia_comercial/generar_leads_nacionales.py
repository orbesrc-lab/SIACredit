import csv
import os

def generar_base_ampliada():
    # Instituciones variadas (Técnicas, Tecnológicas, ETDH, Empresas) a nivel nacional y regional
    leads = [
        # Instituciones Universitarias / Universidades
        {
            "Nombre": "Esteban Piedrahita Uribe",
            "Cargo": "Rector",
            "Institucion": "Universidad Icesi",
            "SNIES": "1204",
            "Correo": "rectoria@icesi.edu.co",
            "LinkedIn": "https://www.linkedin.com/in/esteban-piedrahita-uribe/",
            "Notas": "IES Privada de alta calidad (Universidad)"
        },
        {
            "Nombre": "José Leonardo Valencia Molano",
            "Cargo": "Rector",
            "Institucion": "Fundación Universitaria del Área Andina (Areandina)",
            "SNIES": "2712",
            "Correo": "rectoria@areandina.edu.co",
            "LinkedIn": "",
            "Notas": "Institución Universitaria. Gran presencia nacional e interés en tecnología."
        },
        # Instituciones Tecnológicas
        {
            "Nombre": "",
            "Cargo": "Rector",
            "Institucion": "Tecnológico de Antioquia - Institución Universitaria",
            "SNIES": "3111",
            "Correo": "",
            "LinkedIn": "",
            "Notas": "Institución Tecnológica / Universitaria de carácter público. Alta calidad."
        },
        {
            "Nombre": "Lina Maria Escobar",
            "Cargo": "Directora de Calidad",
            "Institucion": "Politécnico Grancolombiano",
            "SNIES": "2725",
            "Correo": "",
            "LinkedIn": "",
            "Notas": "Institución Universitaria Privada. Alta virtualidad."
        },
        # Instituciones Técnicas Profesionales
        {
            "Nombre": "",
            "Cargo": "Rector",
            "Institucion": "Instituto Técnico Nacional de Comercio (INTENALCO)",
            "SNIES": "4115",
            "Correo": "",
            "LinkedIn": "",
            "Notas": "Institución Técnica Profesional Pública (Cali)."
        },
        {
            "Nombre": "",
            "Cargo": "Director Académico",
            "Institucion": "Fundación Centro de Investigación, Docencia y Consultoría Administrativa (CIDCA)",
            "SNIES": "3103",
            "Correo": "",
            "LinkedIn": "",
            "Notas": "Institución Tecnológica privada."
        },
        # ETDH (Educación para el Trabajo y Desarrollo Humano) / Públicas masivas
        {
            "Nombre": "Jorge Eduardo Londoño Ulloa",
            "Cargo": "Director General",
            "Institucion": "Servicio Nacional de Aprendizaje (SENA)",
            "SNIES": "9999", # El SENA tiene múltiples códigos según el centro
            "Correo": "direcciongeneral@sena.edu.co",
            "LinkedIn": "",
            "Notas": "La institución técnica y ETDH más grande del país. Prospecto gigante."
        },
        {
            "Nombre": "",
            "Cargo": "Director Académico",
            "Institucion": "Comfandi - Instituto de Educación",
            "SNIES": "N/A",
            "Correo": "",
            "LinkedIn": "",
            "Notas": "Caja de compensación con fuerte brazo de ETDH en el Valle del Cauca."
        },
        # Sector Empresarial (Evaluaciones de desempeño, calidad corporativa)
        {
            "Nombre": "",
            "Cargo": "Director de Recursos Humanos / Formación",
            "Institucion": "Grupo Éxito",
            "SNIES": "N/A",
            "Correo": "",
            "LinkedIn": "",
            "Notas": "Empresa privada. Uso potencial: Evaluación de desempeño y formación interna."
        },
        {
            "Nombre": "",
            "Cargo": "Gerente de Capacitación",
            "Institucion": "Bancolombia",
            "SNIES": "N/A",
            "Correo": "",
            "LinkedIn": "",
            "Notas": "Empresa privada. Gran necesidad de trazabilidad en formación de empleados."
        }
    ]

    # Guardar CSV
    output_path = os.path.join(os.path.dirname(__file__), 'leads_nacionales_ampliados.csv')
    
    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Nombre", "Cargo", "Institucion", "SNIES", "Correo", "LinkedIn", "Notas"])
        writer.writeheader()
        writer.writerows(leads)
        
    print(f"Base de datos ampliada generada en: {output_path}")

if __name__ == "__main__":
    generar_base_ampliada()

+-----------------------------------------------------------------------+
| > **Especificación de**                                               |
| >                                                                     |
| > **Requerimientos de**                                               |
| >                                                                     |
| > **Software (ERS)**                                                  |
| >                                                                     |
| > Plataforma de Gestión de Evidencias para Acreditación de Programas  |
| > Académicos                                                          |
+-----------------------------------------------------------------------+
|                                                                       |
+-----------------------------------------------------------------------+
| > Basado en el Acuerdo 01 de 2025 del CESU                            |
| >                                                                     |
| > Consejo Nacional de Educación Superior -- Colombia                  |
| >                                                                     |
| > Versión: 1.0                                                        |
| >                                                                     |
| > Fecha: Abril 2026                                                   |
| >                                                                     |
| > Tecnología: Next.js + Supabase                                      |
+-----------------------------------------------------------------------+

**Tabla de Contenido**

[1. Resumen Ejecutivo [1](#_Toc100000)](#_Toc100000)

[2. Introducción y Antecedentes [2](#_Toc100001)](#_Toc100001)

> [2.1 Propósito del documento [2](#_Toc100002)](#_Toc100002)
>
> [2.2 Alcance del sistema [2](#_Toc100003)](#_Toc100003)
>
> [2.3 Marco normativo [2](#_Toc100004)](#_Toc100004)
>
> [2.4 Definiciones, acrónimos y abreviaturas
> [3](#_Toc100005)](#_Toc100005)

[3. Descripción General del Sistema [3](#_Toc100006)](#_Toc100006)

> [3.1 Perspectiva del sistema [3](#_Toc100007)](#_Toc100007)
>
> [3.2 Funciones del sistema [3](#_Toc100008)](#_Toc100008)
>
> [3.3 Características de los usuarios [3](#_Toc100009)](#_Toc100009)
>
> [3.4 Restricciones [4](#_Toc100010)](#_Toc100010)

[4. Modelo de Acreditación: Los 12 Factores del Acuerdo 01 de 2025
[4](#_Toc100011)](#_Toc100011)

> [Factor 1: Proyecto educativo del programa e identidad institucional
> [4](#_Toc100012)](#_Toc100012)
>
> [Característica 1.1: Misión, visión y principios institucionales
> [5](#_Toc100013)](#_Toc100013)
>
> [Característica 1.2: Proyecto educativo del programa (PEP)
> [5](#_Toc100014)](#_Toc100014)
>
> [Característica 1.3: Perfil de egreso y competencias
> [5](#_Toc100015)](#_Toc100015)
>
> [Característica 1.4: Articulación programa-institución
> [6](#_Toc100016)](#_Toc100016)
>
> [Factor 2: Comunidad de estudiantes [6](#_Toc100017)](#_Toc100017)
>
> [Característica 2.1: Selección e ingreso de estudiantes
> [6](#_Toc100018)](#_Toc100018)
>
> [Característica 2.2: Caracterización de la población estudiantil
> [7](#_Toc100019)](#_Toc100019)
>
> [Característica 2.3: Representatividad y participación estudiantil
> [7](#_Toc100020)](#_Toc100020)
>
> [Característica 2.4: Desarrollo integral de los estudiantes
> [7](#_Toc100021)](#_Toc100021)
>
> [Factor 3: Comunidad de profesores [8](#_Toc100022)](#_Toc100022)
>
> [Característica 3.1: Composición y dedicación del cuerpo docente
> [8](#_Toc100023)](#_Toc100023)
>
> [Característica 3.2: Formación y capacitación docente
> [8](#_Toc100024)](#_Toc100024)
>
> [Característica 3.3: Evaluación y reconocimiento docente
> [9](#_Toc100025)](#_Toc100025)
>
> [Característica 3.4: Producción académica e investigativa
> [9](#_Toc100026)](#_Toc100026)
>
> [Factor 4: Comunidad de egresados [10](#_Toc100027)](#_Toc100027)
>
> [Característica 4.1: Seguimiento a egresados
> [10](#_Toc100028)](#_Toc100028)
>
> [Característica 4.2: Participación de egresados en la vida académica
> [10](#_Toc100029)](#_Toc100029)
>
> [Característica 4.3: Impacto profesional y social de los egresados
> [11](#_Toc100030)](#_Toc100030)
>
> [Característica 4.4: Red de egresados [11](#_Toc100031)](#_Toc100031)
>
> [Factor 5: Aspectos académicos y evaluación
> [11](#_Toc100032)](#_Toc100032)
>
> [Característica 5.1: Currículo y plan de estudios
> [12](#_Toc100033)](#_Toc100033)
>
> [Característica 5.2: Procesos pedagógicos y didácticos
> [12](#_Toc100034)](#_Toc100034)
>
> [Característica 5.3: Sistema de evaluación académica
> [12](#_Toc100035)](#_Toc100035)
>
> [Característica 5.4: Trabajo de grado o proyecto final
> [13](#_Toc100036)](#_Toc100036)
>
> [Factor 6: Permanencia y graduación [13](#_Toc100037)](#_Toc100037)
>
> [Característica 6.1: Políticas y estrategias de permanencia
> [13](#_Toc100038)](#_Toc100038)
>
> [Característica 6.2: Apoyo financiero y bienestar
> [14](#_Toc100039)](#_Toc100039)
>
> [Característica 6.3: Tasas de graduación y duración del programa
> [14](#_Toc100040)](#_Toc100040)
>
> [Característica 6.4: Seguimiento a la deserción estudiantil
> [14](#_Toc100041)](#_Toc100041)
>
> [Factor 7: Proyección e impacto social [15](#_Toc100042)](#_Toc100042)
>
> [Característica 7.1: Extensión y relaciones con el medio
> [15](#_Toc100043)](#_Toc100043)
>
> [Característica 7.2: Impacto en el contexto regional y nacional
> [15](#_Toc100044)](#_Toc100044)
>
> [Característica 7.3: Relaciones internacionales
> [16](#_Toc100045)](#_Toc100045)
>
> [Característica 7.4: Responsabilidad social universitaria
> [16](#_Toc100046)](#_Toc100046)
>
> [Factor 8: Aportes de la investigación, innovación y desarrollo
> tecnológico [17](#_Toc100047)](#_Toc100047)
>
> [Característica 8.1: Políticas y estructura de investigación
> [17](#_Toc100048)](#_Toc100048)
>
> [Característica 8.2: Grupos y proyectos de investigación
> [17](#_Toc100049)](#_Toc100049)
>
> [Característica 8.3: Innovación y desarrollo tecnológico
> [18](#_Toc100050)](#_Toc100050)
>
> [Característica 8.4: Formación investigativa en el programa
> [18](#_Toc100051)](#_Toc100051)
>
> [Factor 9: Bienestar de la comunidad académica del programa
> [18](#_Toc100052)](#_Toc100052)
>
> [Característica 9.1: Programas de bienestar universitario
> [19](#_Toc100053)](#_Toc100053)
>
> [Característica 9.2: Servicios de apoyo al bienestar
> [19](#_Toc100054)](#_Toc100054)
>
> [Característica 9.3: Clima institucional y convivencia
> [19](#_Toc100055)](#_Toc100055)
>
> [Característica 9.4: Inclusión y equidad
> [20](#_Toc100056)](#_Toc100056)
>
> [Factor 10: Recursos físicos, tecnológicos, medios educativos y
> ambientes de aprendizaje [20](#_Toc100057)](#_Toc100057)
>
> [Característica 10.1: Infraestructura física
> [20](#_Toc100058)](#_Toc100058)
>
> [Característica 10.2: Recursos tecnológicos y de información
> [21](#_Toc100059)](#_Toc100059)
>
> [Característica 10.3: Medios educativos y materiales de apoyo
> [21](#_Toc100060)](#_Toc100060)
>
> [Característica 10.4: Ambientes de aprendizaje
> [21](#_Toc100061)](#_Toc100061)
>
> [Factor 11: Organización, administración y financiación del programa
> [22](#_Toc100062)](#_Toc100062)
>
> [Característica 11.1: Estructura organizacional y de dirección
> [22](#_Toc100063)](#_Toc100063)
>
> [Característica 11.2: Procesos administrativos
> [22](#_Toc100064)](#_Toc100064)
>
> [Característica 11.3: Financiación y presupuesto
> [23](#_Toc100065)](#_Toc100065)
>
> [Característica 11.4: Gestión de la calidad administrativa
> [23](#_Toc100066)](#_Toc100066)
>
> [Factor 12: Aseguramiento de la alta calidad del programa
> [24](#_Toc100067)](#_Toc100067)
>
> [Característica 12.1: Autoevaluación y mejoramiento continuo
> [24](#_Toc100068)](#_Toc100068)
>
> [Característica 12.2: Plan de mejoramiento
> [24](#_Toc100069)](#_Toc100069)
>
> [Característica 12.3: Acreditación y reconocimiento de calidad
> [25](#_Toc100070)](#_Toc100070)
>
> [Característica 12.4: Sistema interno de aseguramiento de la calidad
> [25](#_Toc100071)](#_Toc100071)

[5. Requisitos Funcionales [25](#_Toc100072)](#_Toc100072)

> [5.1 Módulo 1: Gestión Institucional y de Programas
> [26](#_Toc100073)](#_Toc100073)
>
> [5.2 Módulo 2: Gestión de Evidencias [26](#_Toc100074)](#_Toc100074)
>
> [5.3 Módulo 3: Autoevaluación e Informes
> [26](#_Toc100075)](#_Toc100075)
>
> [5.4 Módulo 4: Planes de Mejora y Seguimiento
> [27](#_Toc100076)](#_Toc100076)
>
> [5.5 Módulo 5: Autenticación, Roles y Seguridad
> [27](#_Toc100077)](#_Toc100077)
>
> [5.6 Módulo 6: Configuración y Multi-programa
> [27](#_Toc100078)](#_Toc100078)

[6. Requisitos No Funcionales [28](#_Toc100079)](#_Toc100079)

[7. Modelo de Datos (Supabase / PostgreSQL)
[28](#_Toc100080)](#_Toc100080)

> [7.1 Políticas RLS (Row Level Security)
> [29](#_Toc100081)](#_Toc100081)

[8. Roles y Permisos del Sistema [29](#_Toc100082)](#_Toc100082)

[9. Arquitectura del Sistema [29](#_Toc100083)](#_Toc100083)

> [9.1 Arquitectura general [29](#_Toc100084)](#_Toc100084)
>
> [9.2 Stack tecnológico [30](#_Toc100085)](#_Toc100085)
>
> [9.3 Flujo de datos principal [30](#_Toc100086)](#_Toc100086)

[10. Diseño de Interfaz de Usuario [30](#_Toc100087)](#_Toc100087)

> [10.1 Vistas principales [30](#_Toc100088)](#_Toc100088)
>
> [10.2 Principios de diseño [31](#_Toc100089)](#_Toc100089)

[11. Plan de Implementación [31](#_Toc100090)](#_Toc100090)

> [11.1 Fase 1: Fundamentos (Semanas 1-6)
> [31](#_Toc100091)](#_Toc100091)
>
> [11.2 Fase 2: Evidencias y Evaluación (Semanas 7-14)
> [31](#_Toc100092)](#_Toc100092)
>
> [11.3 Fase 3: Informes y Planes de Mejora (Semanas 15-20)
> [32](#_Toc100093)](#_Toc100093)
>
> [11.4 Fase 4: Optimización y Despliegue (Semanas 21-24)
> [32](#_Toc100094)](#_Toc100094)

[12. Glosario [32](#_Toc100095)](#_Toc100095)

*Nota: Esta Tabla de Contenido se genera mediante códigos de campo. Para
garantizar la precisión de los números de página después de editar, haga
clic derecho en la tabla y seleccione \"Actualizar campo\".*

[]{#_Toc100000 .anchor}**1. Resumen Ejecutivo**

El presente documento constituye la Especificación de Requerimientos de
Software (ERS) para la Plataforma de Gestión de Evidencias para
Acreditación de Programas Académicos, una aplicación web moderna
diseñada para facilitar y sistematizar el proceso de autoevaluación y
recolección de evidencias requerido para la acreditación de programas de
educación superior en Colombia, conforme al Acuerdo 01 de 2025 del
Consejo Nacional de Educación Superior (CESU).

La plataforma abordará una necesidad crítica en las instituciones de
educación superior colombianas: la gestión eficiente, organizada y
trazable de las evidencias documentales que soportan el proceso de
acreditación. Actualmente, muchos de estos procesos se realizan de forma
manual, dispersa y con herramientas genéricas (hojas de cálculo, correo
electrónico, repositorios de archivos no estructurados), lo que genera
dificultades en la trazabilidad, la colaboración entre departamentos, la
consistencia de la información y la oportunidad en la entrega de
documentos al Consejo Nacional de Acreditación (CNA).

La solución propuesta se construirá con tecnologías modernas: Next.js
como framework de desarrollo web, Supabase como plataforma integral de
base de datos (PostgreSQL), autenticación y almacenamiento de archivos,
y una arquitectura basada en roles que permite la colaboración
coordinada entre administradores de plataforma, líderes de factor y
usuarios operativos de los diferentes departamentos de la institución.
El sistema soportará n programas académicos de forma simultánea, con
aislamiento completo de datos entre programas y la flexibilidad
necesaria para adaptarse a las particularidades de cada institución y
programa.

[]{#_Toc100001 .anchor}**2. Introducción y Antecedentes**

[]{#_Toc100002 .anchor}**2.1 Propósito del documento**

Este documento tiene como propósito definir de manera completa y
detallada los requerimientos funcionales y no funcionales de la
Plataforma de Gestión de Evidencias para Acreditación. Servirá como base
contractual y técnica para el equipo de desarrollo, los stakeholders
institucionales y los evaluadores de calidad del software. Los
requerimientos aquí especificados son la fuente primaria para el diseño,
implementación, pruebas y aceptación del sistema.

[]{#_Toc100003 .anchor}**2.2 Alcance del sistema**

La plataforma cubrirá el ciclo completo del proceso de autoevaluación
para acreditación de programas académicos, desde la configuración del
modelo de evaluación (12 factores, 48 características y sus aspectos a
evaluar) hasta la generación de informes y cuadros de autoevaluación en
los formatos requeridos por el CNA. El sistema no reemplazará los
procesos de evaluación externa realizados por pares académicos, sino que
facilitará la preparación interna y la organización documental que
antecede y acompaña dichos procesos.

[]{#_Toc100004 .anchor}**2.3 Marco normativo**

El desarrollo de esta plataforma se enmarca en el Acuerdo 01 de 2025 del
CESU, que establece el modelo nacional de acreditación para programas
académicos de educación superior en Colombia. Este acuerdo define 12
factores de evaluación, cada uno con 4 características (48 en total), y
para cada característica se establecen aspectos a evaluar o
direccionamientos que orientan la autoevaluación. El modelo busca que
las instituciones demuestren de manera documentada y verificable las
condiciones de calidad de sus programas académicos, fortalezas,
debilidades y planes de mejoramiento continuo.

[]{#_Toc100005 .anchor}**2.4 Definiciones, acrónimos y abreviaturas**

CESU: Consejo Nacional de Educación Superior. CNA: Consejo Nacional de
Acreditación. ERS: Especificación de Requerimientos de Software. PEP:
Proyecto Educativo del Programa. SNIES: Sistema Nacional de Información
de la Educación Superior. RLS: Row Level Security. RBAC: Role-Based
Access Control. TIC: Tecnologías de la Información y Comunicación. CRUD:
Create, Read, Update, Delete. UUID: Universally Unique Identifier. FK:
Foreign Key.

[]{#_Toc100006 .anchor}**3. Descripción General del Sistema**

[]{#_Toc100007 .anchor}**3.1 Perspectiva del sistema**

La Plataforma de Gestión de Evidencias para Acreditación es un sistema
web autónomo que interactúa con Supabase como servicio de backend (base
de datos PostgreSQL, autenticación, almacenamiento de archivos) y con
los usuarios finales a través de un navegador web. No requiere
integraciones con sistemas legados de la institución, aunque en futuras
versiones podría integrarse con sistemas de información académica (SGA,
plataformas LMS) para automatizar la recolección de ciertas evidencias.

[]{#_Toc100008 .anchor}**3.2 Funciones del sistema**

Las funciones principales del sistema son: (1) Gestión institucional y
de programas académicos, (2) Gestión de evidencias documentales con
flujo de trabajo de revisión, (3) Autoevaluación de factores,
características y aspectos, (4) Generación de informes y cuadros de
autoevaluación, (5) Administración de usuarios, roles y permisos, y (6)
Configuración y adaptabilidad del modelo de evaluación. Cada una de
estas funciones se detalla en los requerimientos funcionales del
presente documento.

[]{#_Toc100009 .anchor}**3.3 Características de los usuarios**

El sistema está diseñado para tres perfiles de usuario diferenciados. El
Administrador de la Plataforma es un usuario con conocimientos técnicos
avanzados que gestiona la configuración general del sistema, los
programas académicos y la asignación de roles. El Líder de Factor es un
académico o profesional con experiencia en procesos de acreditación,
responsable de coordinar y evaluar las evidencias de un factor
específico. El Usuario Operativo es personal administrativo o docente de
los diferentes departamentos que alimenta el sistema con evidencias
documentales; su interacción con el sistema debe ser intuitiva y
requerir mínima capacitación técnica.

[]{#_Toc100010 .anchor}**3.4 Restricciones**

El sistema operará exclusivamente como aplicación web (no habrá
aplicación nativa móvil). La infraestructura de backend se limita a
Supabase (no se contempla despliegue on-premise de la base de datos). El
sistema dependerá de conexión a internet para su funcionamiento (no
habrá modo offline). El tamaño máximo de archivos de evidencia será de
50 MB por archivo. El sistema deberá cumplir con la normativa colombiana
de protección de datos personales (Ley 1581 de 2012).

[]{#_Toc100011 .anchor}**4. Modelo de Acreditación: Los 12 Factores del
Acuerdo 01 de 2025**

El modelo de acreditación establecido en el Acuerdo 01 de 2025 del CESU
define 12 factores de evaluación, cada uno con 4 características (48 en
total), y para cada característica se establecen aspectos a evaluar o
direccionamientos. La plataforma debe reflejar esta estructura de manera
fiel y permitir su configuración flexible para adaptarse a futuras
actualizaciones del modelo. A continuación se presenta una tabla resumen
de los factores, seguida del detalle de cada uno con sus características
y aspectos.

***Tabla 1. Resumen de los 12 factores y sus características***

  ---------------------------------------------------------------------------------
  **Factor**        **Nombre**        **Característica**     **Aspectos a evaluar**
  ----------------- ----------------- ---------------------- ----------------------
  F1                Proyecto          1.1 Misión, visión y   Coherencia entre
                    educativo del     principios             misión, visión y
                    programa e        institucionales        principios del
                    identidad                                programa con los de la
                    institucional                            institución.
                                                             Articulación de los
                                                             fines educativo\...

                                      1.2 Proyecto educativo Definición clara de
                                      del programa (PEP)     objetivos,
                                                             competencias y
                                                             perfiles de formación.
                                                             Actualización
                                                             periódica del PEP
                                                             según necesidades
                                                             s\...

                                      1.3 Perfil de egreso y Definición del perfil
                                      competencias           de egreso con
                                                             competencias genéricas
                                                             y específicas.
                                                             Correspondencia entre
                                                             perfil de egreso y
                                                             neces\...

                                      1.4 Articulación       Consistencia entre las
                                      programa-institución   políticas
                                                             institucionales y las
                                                             del programa.
                                                             Participación del
                                                             programa en los
                                                             órganos de gobier\...

  F2                Comunidad de      2.1 Selección e        Existencia de
                    estudiantes       ingreso de estudiantes políticas y mecanismos
                                                             claros de admisión.
                                                             Criterios de selección
                                                             acordes con el perfil
                                                             de ingreso esperad\...

                                      2.2 Caracterización de Conocimiento de las
                                      la población           condiciones
                                      estudiantil            socioeconómicas,
                                                             demográficas y
                                                             académicas de los
                                                             estudiantes.
                                                             Seguimiento a la
                                                             diversid\...

                                      2.3 Representatividad  Mecanismos de
                                      y participación        participación de los
                                      estudiantil            estudiantes en los
                                                             órganos de dirección
                                                             del programa.
                                                             Existencia de espacios
                                                             de repre\...

                                      2.4 Desarrollo         Programas de
                                      integral de los        orientación académica
                                      estudiantes            y profesional.
                                                             Actividades de
                                                             formación
                                                             complementaria.
                                                             Seguimiento al
                                                             desempeño acad\...

  F3                Comunidad de      3.1 Composición y      Cantidad y proporción
                    profesores        dedicación del cuerpo  de profesores acorde
                                      docente                con las necesidades
                                                             del programa.
                                                             Dedicación horaria
                                                             suficiente para las
                                                             func\...

                                      3.2 Formación y        Nivel de formación
                                      capacitación docente   posgradual de los
                                                             profesores. Programas
                                                             de actualización y
                                                             desarrollo profesional
                                                             docente. Fomento a
                                                             \...

                                      3.3 Evaluación y       Mecanismos de
                                      reconocimiento docente evaluación del
                                                             desempeño docente.
                                                             Estímulos e incentivos
                                                             a la excelencia
                                                             académica.
                                                             Retroalimentación
                                                             para\...

                                      3.4 Producción         Producción de
                                      académica e            conocimiento y
                                      investigativa          publicaciones
                                                             científicas.
                                                             Participación en
                                                             proyectos de
                                                             investigación,
                                                             innovación y
                                                             desarr\...

  F4                Comunidad de      4.1 Seguimiento a      Existencia de
                    egresados         egresados              mecanismos de
                                                             seguimiento y
                                                             comunicación con
                                                             egresados. Análisis de
                                                             la inserción laboral y
                                                             desempeño profe\...

                                      4.2 Participación de   Involucramiento de
                                      egresados en la vida   egresados en
                                      académica              actividades
                                                             académicas, de
                                                             extensión y de
                                                             gobierno. Vinculación
                                                             de egresados como
                                                             docent\...

                                      4.3 Impacto            Reconocimiento de los
                                      profesional y social   egresados en el medio
                                      de los egresados       profesional.
                                                             Contribución de los
                                                             egresados al
                                                             desarrollo regional y
                                                             nacional\...

                                      4.4 Red de egresados   Organización y
                                                             funcionamiento de la
                                                             red o asociación de
                                                             egresados. Actividades
                                                             de actualización y
                                                             formación continua
                                                             par\...

  F5                Aspectos          5.1 Currículo y plan   Coherencia del plan de
                    académicos y      de estudios            estudios con el PEP y
                    evaluación                               el perfil de egreso.
                                                             Integración de las
                                                             áreas de formación y
                                                             flexibilidad c\...

                                      5.2 Procesos           Diversidad de
                                      pedagógicos y          estrategias
                                      didácticos             pedagógicas y
                                                             didácticas.
                                                             Incorporación de
                                                             tecnologías de la
                                                             información y
                                                             comunicación (TIC)
                                                             \...

                                      5.3 Sistema de         Políticas y normativas
                                      evaluación académica   de evaluación
                                                             académica. Diversidad
                                                             de instrumentos y
                                                             criterios de
                                                             evaluación.
                                                             Retroalimentación \...

                                      5.4 Trabajo de grado o Regulación y
                                      proyecto final         orientación del
                                                             trabajo de grado.
                                                             Diversidad de
                                                             modalidades de trabajo
                                                             de grado. Pertinencia
                                                             y calidad de l\...

  F6                Permanencia y     6.1 Políticas y        Existencia de
                    graduación        estrategias de         políticas
                                      permanencia            institucionales de
                                                             permanencia. Programas
                                                             de acompañamiento
                                                             académico y
                                                             psicosocial. Acciones
                                                             af\...

                                      6.2 Apoyo financiero y Disponibilidad de
                                      bienestar              becas, créditos y
                                                             subsidios. Convenios
                                                             para el apoyo
                                                             financiero a
                                                             estudiantes.
                                                             Articulación entre
                                                             bien\...

                                      6.3 Tasas de           Análisis de las tasas
                                      graduación y duración  de graduación por
                                      del programa           cohorte. Comparación
                                                             con los tiempos
                                                             esperados de duración
                                                             del programa.
                                                             Accione\...

                                      6.4 Seguimiento a la   Identificación de
                                      deserción estudiantil  causas y factores
                                                             asociados a la
                                                             deserción. Estrategias
                                                             de prevención y
                                                             mitigación de la
                                                             deserción. Re\...

  F7                Proyección e      7.1 Extensión y        Programas y proyectos
                    impacto social    relaciones con el      de extensión y
                                      medio                  proyección social.
                                                             Relaciones
                                                             interinstitucionales
                                                             con sectores
                                                             productivos,
                                                             gubern\...

                                      7.2 Impacto en el      Contribución del
                                      contexto regional y    programa al desarrollo
                                      nacional               regional y nacional.
                                                             Participación en la
                                                             solución de problemas
                                                             del entorno. Reco\...

                                      7.3 Relaciones         Estrategias de
                                      internacionales        internacionalización
                                                             del programa.
                                                             Movilidad académica de
                                                             estudiantes y
                                                             docentes. Convenios y
                                                             alianzas co\...

                                      7.4 Responsabilidad    Políticas y prácticas
                                      social universitaria   de responsabilidad
                                                             social. Programas de
                                                             voluntariado y
                                                             servicio social.
                                                             Compromiso con la
                                                             sostenib\...

  F8                Aportes de la     8.1 Políticas y        Existencia de
                    investigación,    estructura de          políticas
                    innovación y      investigación          institucionales y del
                    desarrollo                               programa para la
                    tecnológico                              investigación.
                                                             Estructura
                                                             organizacional de
                                                             apoyo a la in\...

                                      8.2 Grupos y proyectos Reconocimiento y
                                      de investigación       clasificación de
                                                             grupos de
                                                             investigación.
                                                             Proyectos de
                                                             investigación vigentes
                                                             y finalizados.
                                                             Productivi\...

                                      8.3 Innovación y       Iniciativas de
                                      desarrollo tecnológico innovación y
                                                             emprendimiento.
                                                             Registro de propiedad
                                                             intelectual y
                                                             patentes.
                                                             Transferencia de
                                                             resultados de\...

                                      8.4 Formación          Inclusión de
                                      investigativa en el    competencias
                                      programa               investigativas en el
                                                             currículo.
                                                             Participación de
                                                             estudiantes en
                                                             proyectos de
                                                             investigación y s\...

  F9                Bienestar de la   9.1 Programas de       Oferta de programas de
                    comunidad         bienestar              bienestar para
                    académica del     universitario          docentes, estudiantes
                    programa                                 y personal
                                                             administrativo.
                                                             Accesibilidad y
                                                             cobertura de los \...

                                      9.2 Servicios de apoyo Servicios de salud,
                                      al bienestar           orientación
                                                             psicológica y apoyo
                                                             socioeconómico.
                                                             Infraestructura para
                                                             la recreación, la
                                                             cultura y el \...

                                      9.3 Clima              Medición del clima
                                      institucional y        institucional.
                                      convivencia            Mecanismos de
                                                             resolución de
                                                             conflictos y
                                                             convivencia pacífica.
                                                             Políticas de
                                                             prevención\...

                                      9.4 Inclusión y        Políticas de inclusión
                                      equidad                y equidad de género,
                                                             étnica y de
                                                             diversidad.
                                                             Accesibilidad para
                                                             personas con
                                                             discapacidad.
                                                             Progra\...

  F10               Recursos físicos, 10.1 Infraestructura   Disponibilidad y
                    tecnológicos,     física                 estado de aulas,
                    medios educativos                        laboratorios,
                    y ambientes de                           bibliotecas y espacios
                    aprendizaje                              académicos. Adecuación
                                                             de los espacios a las
                                                             nece\...

                                      10.2 Recursos          Disponibilidad de
                                      tecnológicos y de      equipos, redes,
                                      información            conectividad y
                                                             plataformas
                                                             tecnológicas.
                                                             Actualización y
                                                             mantenimiento de los
                                                             recursos\...

                                      10.3 Medios educativos Disponibilidad y
                                      y materiales de apoyo  calidad de materiales
                                                             didácticos,
                                                             bibliográficos y
                                                             digitales. Producción
                                                             de recursos educativos
                                                             propios\...

                                      10.4 Ambientes de      Diseño de espacios que
                                      aprendizaje            favorezcan la
                                                             interacción, la
                                                             colaboración y el
                                                             aprendizaje. Ambientes
                                                             virtuales y mixtos de
                                                             apre\...

  F11               Organización,     11.1 Estructura        Claridad en la
                    administración y  organizacional y de    estructura de
                    financiación del  dirección              dirección del
                    programa                                 programa. Funciones y
                                                             responsabilidades
                                                             definidas. Mecanismos
                                                             de comunicación\...

                                      11.2 Procesos          Eficiencia y
                                      administrativos        transparencia en los
                                                             procesos
                                                             administrativos.
                                                             Sistemas de
                                                             información para la
                                                             gestión académica y
                                                             administ\...

                                      11.3 Financiación y    Asignación
                                      presupuesto            presupuestal
                                                             suficiente para el
                                                             funcionamiento del
                                                             programa.
                                                             Diversificación de
                                                             fuentes de
                                                             financiamiento. Ej\...

                                      11.4 Gestión de la     Mecanismos de control
                                      calidad administrativa y seguimiento a la
                                                             gestión. Indicadores
                                                             de gestión y
                                                             resultados. Procesos
                                                             de autoevaluación y
                                                             mejo\...

  F12               Aseguramiento de  12.1 Autoevaluación y  Procesos sistemáticos
                    la alta calidad   mejoramiento continuo  de autoevaluación del
                    del programa                             programa. Cultura de
                                                             la evaluación y la
                                                             mejora continua. Uso
                                                             de resultados d\...

                                      12.2 Plan de           Formulación de planes
                                      mejoramiento           de mejoramiento a
                                                             partir de la
                                                             autoevaluación.
                                                             Seguimiento a la
                                                             ejecución de los
                                                             planes de mejoram\...

                                      12.3 Acreditación y    Historial de
                                      reconocimiento de      acreditación o
                                      calidad                evaluación externa del
                                                             programa. Compromiso
                                                             con la acreditación de
                                                             alta calidad.
                                                             Preparación\...

                                      12.4 Sistema interno   Existencia y
                                      de aseguramiento de la funcionamiento de un
                                      calidad                sistema institucional
                                                             de aseguramiento de la
                                                             calidad. Articulación
                                                             entre el sistema
                                                             in\...
  ---------------------------------------------------------------------------------

[]{#_Toc100012 .anchor}**Factor 1: Proyecto educativo del programa e
identidad institucional**

El Factor 1, denominado \"Proyecto educativo del programa e identidad
institucional\", constituye uno de los doce pilares fundamentales del
modelo de autoevaluación establecido en el Acuerdo 01 de 2025 del CESU
para la acreditación de programas académicos de educación superior en
Colombia. Este factor evalúa las condiciones esenciales del programa en
relación con los elementos que lo componen, considerando las
particularidades del contexto institucional y las exigencias de calidad
del sistema educativo colombiano. A continuación se presentan las cuatro
características asociadas a este factor, cada una con sus respectivos
aspectos a evaluar o direccionamientos.

[]{#_Toc100013 .anchor}**Característica 1.1: Misión, visión y principios
institucionales**

Aspectos a evaluar o direccionamientos:

Coherencia entre misión, visión y principios del programa con los de la
institución. Articulación de los fines educativos con el contexto
nacional y regional. Apropiación de la comunidad académica hacia los
principios institucionales.

[]{#_Toc100014 .anchor}**Característica 1.2: Proyecto educativo del
programa (PEP)**

Aspectos a evaluar o direccionamientos:

Definición clara de objetivos, competencias y perfiles de formación.
Actualización periódica del PEP según necesidades sociales y académicas.
Integración de los ejes formativos transversales. Socialización del PEP
con la comunidad académica.

[]{#_Toc100015 .anchor}**Característica 1.3: Perfil de egreso y
competencias**

Aspectos a evaluar o direccionamientos:

Definición del perfil de egreso con competencias genéricas y
específicas. Correspondencia entre perfil de egreso y necesidades del
contexto. Evaluación del logro de las competencias del perfil de egreso.

[]{#_Toc100016 .anchor}**Característica 1.4: Articulación
programa-institución**

Aspectos a evaluar o direccionamientos:

Consistencia entre las políticas institucionales y las del programa.
Participación del programa en los órganos de gobierno. Integración del
programa con los planes de desarrollo institucional.

[]{#_Toc100017 .anchor}**Factor 2: Comunidad de estudiantes**

El Factor 2, denominado \"Comunidad de estudiantes\", constituye uno de
los doce pilares fundamentales del modelo de autoevaluación establecido
en el Acuerdo 01 de 2025 del CESU para la acreditación de programas
académicos de educación superior en Colombia. Este factor evalúa las
condiciones esenciales del programa en relación con los elementos que lo
componen, considerando las particularidades del contexto institucional y
las exigencias de calidad del sistema educativo colombiano. A
continuación se presentan las cuatro características asociadas a este
factor, cada una con sus respectivos aspectos a evaluar o
direccionamientos.

[]{#_Toc100018 .anchor}**Característica 2.1: Selección e ingreso de
estudiantes**

Aspectos a evaluar o direccionamientos:

Existencia de políticas y mecanismos claros de admisión. Criterios de
selección acordes con el perfil de ingreso esperado. Estrategias de
divulgación y atraimiento de aspirantes. Equidad e inclusión en los
procesos de admisión.

[]{#_Toc100019 .anchor}**Característica 2.2: Caracterización de la
población estudiantil**

Aspectos a evaluar o direccionamientos:

Conocimiento de las condiciones socioeconómicas, demográficas y
académicas de los estudiantes. Seguimiento a la diversidad y equidad en
la composición estudiantil. Uso de la información para la toma de
decisiones académicas y administrativas.

[]{#_Toc100020 .anchor}**Característica 2.3: Representatividad y
participación estudiantil**

Aspectos a evaluar o direccionamientos:

Mecanismos de participación de los estudiantes en los órganos de
dirección del programa. Existencia de espacios de representación
estudiantil. Participación activa en procesos de autoevaluación y
mejoramiento.

[]{#_Toc100021 .anchor}**Característica 2.4: Desarrollo integral de los
estudiantes**

Aspectos a evaluar o direccionamientos:

Programas de orientación académica y profesional. Actividades de
formación complementaria. Seguimiento al desempeño académico y personal
de los estudiantes.

[]{#_Toc100022 .anchor}**Factor 3: Comunidad de profesores**

El Factor 3, denominado \"Comunidad de profesores\", constituye uno de
los doce pilares fundamentales del modelo de autoevaluación establecido
en el Acuerdo 01 de 2025 del CESU para la acreditación de programas
académicos de educación superior en Colombia. Este factor evalúa las
condiciones esenciales del programa en relación con los elementos que lo
componen, considerando las particularidades del contexto institucional y
las exigencias de calidad del sistema educativo colombiano. A
continuación se presentan las cuatro características asociadas a este
factor, cada una con sus respectivos aspectos a evaluar o
direccionamientos.

[]{#_Toc100023 .anchor}**Característica 3.1: Composición y dedicación
del cuerpo docente**

Aspectos a evaluar o direccionamientos:

Cantidad y proporción de profesores acorde con las necesidades del
programa. Dedicación horaria suficiente para las funciones de docencia,
investigación y extensión. Distribución equilibrada de cargas
académicas.

[]{#_Toc100024 .anchor}**Característica 3.2: Formación y capacitación
docente**

Aspectos a evaluar o direccionamientos:

Nivel de formación posgradual de los profesores. Programas de
actualización y desarrollo profesional docente. Fomento a la obtención
de títulos de maestría y doctorado.

[]{#_Toc100025 .anchor}**Característica 3.3: Evaluación y reconocimiento
docente**

Aspectos a evaluar o direccionamientos:

Mecanismos de evaluación del desempeño docente. Estímulos e incentivos a
la excelencia académica. Retroalimentación para la mejora continua de la
práctica pedagógica.

[]{#_Toc100026 .anchor}**Característica 3.4: Producción académica e
investigativa**

Aspectos a evaluar o direccionamientos:

Producción de conocimiento y publicaciones científicas. Participación en
proyectos de investigación, innovación y desarrollo tecnológico.
Vinculación de la producción académica con la docencia y la extensión.

[]{#_Toc100027 .anchor}**Factor 4: Comunidad de egresados**

El Factor 4, denominado \"Comunidad de egresados\", constituye uno de
los doce pilares fundamentales del modelo de autoevaluación establecido
en el Acuerdo 01 de 2025 del CESU para la acreditación de programas
académicos de educación superior en Colombia. Este factor evalúa las
condiciones esenciales del programa en relación con los elementos que lo
componen, considerando las particularidades del contexto institucional y
las exigencias de calidad del sistema educativo colombiano. A
continuación se presentan las cuatro características asociadas a este
factor, cada una con sus respectivos aspectos a evaluar o
direccionamientos.

[]{#_Toc100028 .anchor}**Característica 4.1: Seguimiento a egresados**

Aspectos a evaluar o direccionamientos:

Existencia de mecanismos de seguimiento y comunicación con egresados.
Análisis de la inserción laboral y desempeño profesional. Uso de la
información de egresados para el mejoramiento del programa.

[]{#_Toc100029 .anchor}**Característica 4.2: Participación de egresados
en la vida académica**

Aspectos a evaluar o direccionamientos:

Involucramiento de egresados en actividades académicas, de extensión y
de gobierno. Vinculación de egresados como docentes, investigadores o
colaboradores.

[]{#_Toc100030 .anchor}**Característica 4.3: Impacto profesional y
social de los egresados**

Aspectos a evaluar o direccionamientos:

Reconocimiento de los egresados en el medio profesional. Contribución de
los egresados al desarrollo regional y nacional. Liderazgo y
participación en redes profesionales.

[]{#_Toc100031 .anchor}**Característica 4.4: Red de egresados**

Aspectos a evaluar o direccionamientos:

Organización y funcionamiento de la red o asociación de egresados.
Actividades de actualización y formación continua para egresados.
Fortalecimiento del sentido de pertenencia.

[]{#_Toc100032 .anchor}**Factor 5: Aspectos académicos y evaluación**

El Factor 5, denominado \"Aspectos académicos y evaluación\", constituye
uno de los doce pilares fundamentales del modelo de autoevaluación
establecido en el Acuerdo 01 de 2025 del CESU para la acreditación de
programas académicos de educación superior en Colombia. Este factor
evalúa las condiciones esenciales del programa en relación con los
elementos que lo componen, considerando las particularidades del
contexto institucional y las exigencias de calidad del sistema educativo
colombiano. A continuación se presentan las cuatro características
asociadas a este factor, cada una con sus respectivos aspectos a evaluar
o direccionamientos.

[]{#_Toc100033 .anchor}**Característica 5.1: Currículo y plan de
estudios**

Aspectos a evaluar o direccionamientos:

Coherencia del plan de estudios con el PEP y el perfil de egreso.
Integración de las áreas de formación y flexibilidad curricular.
Inclusión de componentes de investigación, innovación y extensión.
Actualización periódica del currículo.

[]{#_Toc100034 .anchor}**Característica 5.2: Procesos pedagógicos y
didácticos**

Aspectos a evaluar o direccionamientos:

Diversidad de estrategias pedagógicas y didácticas. Incorporación de
tecnologías de la información y comunicación (TIC) en la enseñanza.
Fomento del aprendizaje autónomo, crítico y creativo.

[]{#_Toc100035 .anchor}**Característica 5.3: Sistema de evaluación
académica**

Aspectos a evaluar o direccionamientos:

Políticas y normativas de evaluación académica. Diversidad de
instrumentos y criterios de evaluación. Retroalimentación oportuna y
significativa a los estudiantes. Evaluación de la evaluación como
mecanismo de mejora.

[]{#_Toc100036 .anchor}**Característica 5.4: Trabajo de grado o proyecto
final**

Aspectos a evaluar o direccionamientos:

Regulación y orientación del trabajo de grado. Diversidad de modalidades
de trabajo de grado. Pertinencia y calidad de los trabajos de grado
realizados.

[]{#_Toc100037 .anchor}**Factor 6: Permanencia y graduación**

El Factor 6, denominado \"Permanencia y graduación\", constituye uno de
los doce pilares fundamentales del modelo de autoevaluación establecido
en el Acuerdo 01 de 2025 del CESU para la acreditación de programas
académicos de educación superior en Colombia. Este factor evalúa las
condiciones esenciales del programa en relación con los elementos que lo
componen, considerando las particularidades del contexto institucional y
las exigencias de calidad del sistema educativo colombiano. A
continuación se presentan las cuatro características asociadas a este
factor, cada una con sus respectivos aspectos a evaluar o
direccionamientos.

[]{#_Toc100038 .anchor}**Característica 6.1: Políticas y estrategias de
permanencia**

Aspectos a evaluar o direccionamientos:

Existencia de políticas institucionales de permanencia. Programas de
acompañamiento académico y psicosocial. Acciones afirmativas para
poblaciones vulnerables. Seguimiento a indicadores de deserción y
permanencia.

[]{#_Toc100039 .anchor}**Característica 6.2: Apoyo financiero y
bienestar**

Aspectos a evaluar o direccionamientos:

Disponibilidad de becas, créditos y subsidios. Convenios para el apoyo
financiero a estudiantes. Articulación entre bienestar universitario y
la permanencia estudiantil.

[]{#_Toc100040 .anchor}**Característica 6.3: Tasas de graduación y
duración del programa**

Aspectos a evaluar o direccionamientos:

Análisis de las tasas de graduación por cohorte. Comparación con los
tiempos esperados de duración del programa. Acciones para mejorar los
indicadores de graduación oportuna.

[]{#_Toc100041 .anchor}**Característica 6.4: Seguimiento a la deserción
estudiantil**

Aspectos a evaluar o direccionamientos:

Identificación de causas y factores asociados a la deserción.
Estrategias de prevención y mitigación de la deserción. Reincorporación
de estudiantes desertores.

[]{#_Toc100042 .anchor}**Factor 7: Proyección e impacto social**

El Factor 7, denominado \"Proyección e impacto social\", constituye uno
de los doce pilares fundamentales del modelo de autoevaluación
establecido en el Acuerdo 01 de 2025 del CESU para la acreditación de
programas académicos de educación superior en Colombia. Este factor
evalúa las condiciones esenciales del programa en relación con los
elementos que lo componen, considerando las particularidades del
contexto institucional y las exigencias de calidad del sistema educativo
colombiano. A continuación se presentan las cuatro características
asociadas a este factor, cada una con sus respectivos aspectos a evaluar
o direccionamientos.

[]{#_Toc100043 .anchor}**Característica 7.1: Extensión y relaciones con
el medio**

Aspectos a evaluar o direccionamientos:

Programas y proyectos de extensión y proyección social. Relaciones
interinstitucionales con sectores productivos, gubernamentales y
sociales. Transferencia de conocimiento al sector externo.

[]{#_Toc100044 .anchor}**Característica 7.2: Impacto en el contexto
regional y nacional**

Aspectos a evaluar o direccionamientos:

Contribución del programa al desarrollo regional y nacional.
Participación en la solución de problemas del entorno. Reconocimiento
social del programa y de la institución.

[]{#_Toc100045 .anchor}**Característica 7.3: Relaciones
internacionales**

Aspectos a evaluar o direccionamientos:

Estrategias de internacionalización del programa. Movilidad académica de
estudiantes y docentes. Convenios y alianzas con instituciones
extranjeras. Incorporación de perspectivas internacionales en el
currículo.

[]{#_Toc100046 .anchor}**Característica 7.4: Responsabilidad social
universitaria**

Aspectos a evaluar o direccionamientos:

Políticas y prácticas de responsabilidad social. Programas de
voluntariado y servicio social. Compromiso con la sostenibilidad
ambiental, social y económica.

[]{#_Toc100047 .anchor}**Factor 8: Aportes de la investigación,
innovación y desarrollo tecnológico**

El Factor 8, denominado \"Aportes de la investigación, innovación y
desarrollo tecnológico\", constituye uno de los doce pilares
fundamentales del modelo de autoevaluación establecido en el Acuerdo 01
de 2025 del CESU para la acreditación de programas académicos de
educación superior en Colombia. Este factor evalúa las condiciones
esenciales del programa en relación con los elementos que lo componen,
considerando las particularidades del contexto institucional y las
exigencias de calidad del sistema educativo colombiano. A continuación
se presentan las cuatro características asociadas a este factor, cada
una con sus respectivos aspectos a evaluar o direccionamientos.

[]{#_Toc100048 .anchor}**Característica 8.1: Políticas y estructura de
investigación**

Aspectos a evaluar o direccionamientos:

Existencia de políticas institucionales y del programa para la
investigación. Estructura organizacional de apoyo a la investigación
(grupos, centros, semilleros). Financiación destinada a la actividad
investigativa.

[]{#_Toc100049 .anchor}**Característica 8.2: Grupos y proyectos de
investigación**

Aspectos a evaluar o direccionamientos:

Reconocimiento y clasificación de grupos de investigación. Proyectos de
investigación vigentes y finalizados. Productividad investigativa y su
impacto en el programa.

[]{#_Toc100050 .anchor}**Característica 8.3: Innovación y desarrollo
tecnológico**

Aspectos a evaluar o direccionamientos:

Iniciativas de innovación y emprendimiento. Registro de propiedad
intelectual y patentes. Transferencia de resultados de investigación al
sector productivo y social.

[]{#_Toc100051 .anchor}**Característica 8.4: Formación investigativa en
el programa**

Aspectos a evaluar o direccionamientos:

Inclusión de competencias investigativas en el currículo. Participación
de estudiantes en proyectos de investigación y semilleros de
investigación. Desarrollo de capacidad investigativa en estudiantes y
docentes.

[]{#_Toc100052 .anchor}**Factor 9: Bienestar de la comunidad académica
del programa**

El Factor 9, denominado \"Bienestar de la comunidad académica del
programa\", constituye uno de los doce pilares fundamentales del modelo
de autoevaluación establecido en el Acuerdo 01 de 2025 del CESU para la
acreditación de programas académicos de educación superior en Colombia.
Este factor evalúa las condiciones esenciales del programa en relación
con los elementos que lo componen, considerando las particularidades del
contexto institucional y las exigencias de calidad del sistema educativo
colombiano. A continuación se presentan las cuatro características
asociadas a este factor, cada una con sus respectivos aspectos a evaluar
o direccionamientos.

[]{#_Toc100053 .anchor}**Característica 9.1: Programas de bienestar
universitario**

Aspectos a evaluar o direccionamientos:

Oferta de programas de bienestar para docentes, estudiantes y personal
administrativo. Accesibilidad y cobertura de los programas de bienestar.
Articulación del bienestar con los procesos académicos.

[]{#_Toc100054 .anchor}**Característica 9.2: Servicios de apoyo al
bienestar**

Aspectos a evaluar o direccionamientos:

Servicios de salud, orientación psicológica y apoyo socioeconómico.
Infraestructura para la recreación, la cultura y el deporte. Programas
de prevención y promoción de la salud.

[]{#_Toc100055 .anchor}**Característica 9.3: Clima institucional y
convivencia**

Aspectos a evaluar o direccionamientos:

Medición del clima institucional. Mecanismos de resolución de conflictos
y convivencia pacífica. Políticas de prevención de acoso y
discriminación.

[]{#_Toc100056 .anchor}**Característica 9.4: Inclusión y equidad**

Aspectos a evaluar o direccionamientos:

Políticas de inclusión y equidad de género, étnica y de diversidad.
Accesibilidad para personas con discapacidad. Programas de acción
afirmativa.

[]{#_Toc100057 .anchor}**Factor 10: Recursos físicos, tecnológicos,
medios educativos y ambientes de aprendizaje**

El Factor 10, denominado \"Recursos físicos, tecnológicos, medios
educativos y ambientes de aprendizaje\", constituye uno de los doce
pilares fundamentales del modelo de autoevaluación establecido en el
Acuerdo 01 de 2025 del CESU para la acreditación de programas académicos
de educación superior en Colombia. Este factor evalúa las condiciones
esenciales del programa en relación con los elementos que lo componen,
considerando las particularidades del contexto institucional y las
exigencias de calidad del sistema educativo colombiano. A continuación
se presentan las cuatro características asociadas a este factor, cada
una con sus respectivos aspectos a evaluar o direccionamientos.

[]{#_Toc100058 .anchor}**Característica 10.1: Infraestructura física**

Aspectos a evaluar o direccionamientos:

Disponibilidad y estado de aulas, laboratorios, bibliotecas y espacios
académicos. Adecuación de los espacios a las necesidades del programa.
Plan de mantenimiento y mejoramiento de la infraestructura.

[]{#_Toc100059 .anchor}**Característica 10.2: Recursos tecnológicos y de
información**

Aspectos a evaluar o direccionamientos:

Disponibilidad de equipos, redes, conectividad y plataformas
tecnológicas. Actualización y mantenimiento de los recursos
tecnológicos. Acceso a bases de datos, repositorios y recursos
digitales.

[]{#_Toc100060 .anchor}**Característica 10.3: Medios educativos y
materiales de apoyo**

Aspectos a evaluar o direccionamientos:

Disponibilidad y calidad de materiales didácticos, bibliográficos y
digitales. Producción de recursos educativos propios. Uso de plataformas
virtuales de aprendizaje.

[]{#_Toc100061 .anchor}**Característica 10.4: Ambientes de aprendizaje**

Aspectos a evaluar o direccionamientos:

Diseño de espacios que favorezcan la interacción, la colaboración y el
aprendizaje. Ambientes virtuales y mixtos de aprendizaje. Seguridad y
accesibilidad en los ambientes de aprendizaje.

[]{#_Toc100062 .anchor}**Factor 11: Organización, administración y
financiación del programa**

El Factor 11, denominado \"Organización, administración y financiación
del programa\", constituye uno de los doce pilares fundamentales del
modelo de autoevaluación establecido en el Acuerdo 01 de 2025 del CESU
para la acreditación de programas académicos de educación superior en
Colombia. Este factor evalúa las condiciones esenciales del programa en
relación con los elementos que lo componen, considerando las
particularidades del contexto institucional y las exigencias de calidad
del sistema educativo colombiano. A continuación se presentan las cuatro
características asociadas a este factor, cada una con sus respectivos
aspectos a evaluar o direccionamientos.

[]{#_Toc100063 .anchor}**Característica 11.1: Estructura organizacional
y de dirección**

Aspectos a evaluar o direccionamientos:

Claridad en la estructura de dirección del programa. Funciones y
responsabilidades definidas. Mecanismos de comunicación y coordinación
entre las dependencias.

[]{#_Toc100064 .anchor}**Característica 11.2: Procesos administrativos**

Aspectos a evaluar o direccionamientos:

Eficiencia y transparencia en los procesos administrativos. Sistemas de
información para la gestión académica y administrativa. Oportunidad en
la atención a estudiantes, docentes y administrativos.

[]{#_Toc100065 .anchor}**Característica 11.3: Financiación y
presupuesto**

Aspectos a evaluar o direccionamientos:

Asignación presupuestal suficiente para el funcionamiento del programa.
Diversificación de fuentes de financiamiento. Ejecución presupuestal y
rendición de cuentas.

[]{#_Toc100066 .anchor}**Característica 11.4: Gestión de la calidad
administrativa**

Aspectos a evaluar o direccionamientos:

Mecanismos de control y seguimiento a la gestión. Indicadores de gestión
y resultados. Procesos de autoevaluación y mejora continua de la
gestión.

[]{#_Toc100067 .anchor}**Factor 12: Aseguramiento de la alta calidad del
programa**

El Factor 12, denominado \"Aseguramiento de la alta calidad del
programa\", constituye uno de los doce pilares fundamentales del modelo
de autoevaluación establecido en el Acuerdo 01 de 2025 del CESU para la
acreditación de programas académicos de educación superior en Colombia.
Este factor evalúa las condiciones esenciales del programa en relación
con los elementos que lo componen, considerando las particularidades del
contexto institucional y las exigencias de calidad del sistema educativo
colombiano. A continuación se presentan las cuatro características
asociadas a este factor, cada una con sus respectivos aspectos a evaluar
o direccionamientos.

[]{#_Toc100068 .anchor}**Característica 12.1: Autoevaluación y
mejoramiento continuo**

Aspectos a evaluar o direccionamientos:

Procesos sistemáticos de autoevaluación del programa. Cultura de la
evaluación y la mejora continua. Uso de resultados de la autoevaluación
para la toma de decisiones.

[]{#_Toc100069 .anchor}**Característica 12.2: Plan de mejoramiento**

Aspectos a evaluar o direccionamientos:

Formulación de planes de mejoramiento a partir de la autoevaluación.
Seguimiento a la ejecución de los planes de mejoramiento. Evaluación del
impacto de las acciones de mejoramiento.

[]{#_Toc100070 .anchor}**Característica 12.3: Acreditación y
reconocimiento de calidad**

Aspectos a evaluar o direccionamientos:

Historial de acreditación o evaluación externa del programa. Compromiso
con la acreditación de alta calidad. Preparación para procesos de
evaluación externa y renovación de acreditación.

[]{#_Toc100071 .anchor}**Característica 12.4: Sistema interno de
aseguramiento de la calidad**

Aspectos a evaluar o direccionamientos:

Existencia y funcionamiento de un sistema institucional de aseguramiento
de la calidad. Articulación entre el sistema institucional y el
aseguramiento del programa. Uso de indicadores de calidad para el
seguimiento.

[]{#_Toc100072 .anchor}**5. Requisitos Funcionales**

Los requisitos funcionales se organizan en seis módulos que corresponden
a las principales funcionalidades del sistema. Cada requisito incluye un
identificador único, su descripción, nivel de prioridad y criterio de
aceptación.

[]{#_Toc100073 .anchor}**5.1 Módulo 1: Gestión Institucional y de
Programas**

Este módulo abarca todas las funcionalidades necesarias para la
configuración de la institución, la creación y gestión de programas
académicos, y la carga automática de la estructura del modelo de
evaluación (12 factores, 48 características y sus aspectos). Es el
módulo fundacional del sistema, ya que establece el contexto sobre el
cual operan todos los demás módulos. El administrador de la plataforma
es el principal usuario de este módulo, aunque los líderes de factor
también pueden consultar la configuración de sus factores asignados.

***Tabla 2. Requisitos funcionales -- Módulo 1***

  ----------------------------------------------------------------------------
  **ID**            **Requisito**          **Prioridad**     **Criterio de
                                                             aceptación**
  ----------------- ---------------------- ----------------- -----------------
  RF-01             El sistema debe        Alta              CRUD completo de
                    permitir el registro y                   instituciones.
                    gestión de                               Validación de NIT
                    instituciones de                         único.
                    educación superior con                   
                    sus datos básicos                        
                    (nombre, NIT, ciudad,                    
                    estado).                                 

  RF-02             El sistema debe        Alta              Múltiples
                    permitir la creación                     programas por
                    de n programas                           institución. Sin
                    académicos por                           límite de
                    institución, con                         programas.
                    nombre, nivel                            
                    (pregrado/posgrado),                     
                    título, código SNIES y                   
                    estado de                                
                    acreditación.                            

  RF-03             El sistema debe cargar Alta              Estructura
                    automáticamente los 12                   completa cargada
                    factores, 48                             al crear un
                    características y                        programa. Edición
                    aspectos a evaluar del                   de aspectos
                    modelo del Acuerdo 01                    permitida.
                    de 2025 del CESU para                    
                    cada programa.                           
  ----------------------------------------------------------------------------

[]{#_Toc100074 .anchor}**5.2 Módulo 2: Gestión de Evidencias**

El módulo de gestión de evidencias es el núcleo operativo del sistema.
Permite a los usuarios operativos subir documentos, organizarlos por
factor, característica y aspecto, y gestionar el flujo de revisión por
parte de los líderes de factor. Implementa un flujo de trabajo completo
con estados definidos que garantizan la trazabilidad y la calidad de las
evidencias recolectadas. El versionamiento de documentos y el
almacenamiento seguro en Supabase Storage son componentes críticos de
este módulo.

***Tabla 3. Requisitos funcionales -- Módulo 2***

  -----------------------------------------------------------------------
  **ID**            **Requisito**     **Prioridad**     **Criterio de
                                                        aceptación**
  ----------------- ----------------- ----------------- -----------------
  RF-04             El sistema debe   Alta              Formatos
                    permitir la                         soportados: PDF,
                    subida de                           DOCX, XLSX, JPG,
                    evidencias                          PNG, MP4. Tamaño
                    documentales                        máximo: 50MB.
                    (PDF, DOCX, XLSX,                   
                    imágenes, video)                    
                    asociadas a cada                    
                    aspecto a                           
                    evaluar.                            

  RF-05             El sistema debe   Alta              Transiciones de
                    gestionar el                        estado válidas.
                    ciclo de vida de                    Historial de
                    las evidencias                      cambios por
                    con estados:                        evidencia.
                    borrador,                           
                    enviado, en                         
                    revisión,                           
                    aprobado,                           
                    observado,                          
                    rechazado.                          

  RF-06             El sistema debe   Alta              Notificación al
                    permitir al líder                   usuario
                    de factor                           operativo.
                    revisar, aprobar,                   Registro de fecha
                    observar o                          y observaciones.
                    rechazar                            
                    evidencias con                      
                    comentarios.                        

  RF-07             El sistema debe   Alta              Nueva versi00f3n
                    permitir al                         de la evidencia.
                    usuario operativo                   Se preserva el
                    corregir y                          historial de
                    reenviar                            versiones.
                    evidencias                          
                    observadas o                        
                    rechazadas.                         

  RF-08             El sistema debe   Alta              URL firmada para
                    permitir el                         acceso. Historial
                    almacenamiento y                    de versiones
                    versionamiento de                   accesible.
                    evidencias en                       
                    Supabase Storage.                   
  -----------------------------------------------------------------------

[]{#_Toc100075 .anchor}**5.3 Módulo 3: Autoevaluación e Informes**

Este módulo permite la calificación y autoevaluación de cada aspecto a
evaluar, así como la consolidación de resultados por característica, por
factor y a nivel global del programa. La generación de informes y
cuadros de autoevaluación en los formatos requeridos por el CNA es una
función esencial que automatiza un proceso actualmente manual y propenso
a errores de formato e inconsistencias. Las calificaciones se realizan
en una escala de 1 a 5, donde cada nivel tiene un significado específico
en el contexto del modelo de acreditación colombiano.

***Tabla 4. Requisitos funcionales -- Módulo 3***

  -----------------------------------------------------------------------
  **ID**            **Requisito**     **Prioridad**     **Criterio de
                                                        aceptación**
  ----------------- ----------------- ----------------- -----------------
  RF-09             El sistema debe   Alta              Formulario
                    permitir la                         completo por
                    autoevaluación de                   aspecto.
                    cada aspecto a                      Calificación
                    evaluar con                         obligatoria.
                    calificación de 1                   Guardado
                    a 5,                                automático.
                    justificación,                      
                    fortalezas,                         
                    debilidades y                       
                    plan de mejora.                     

  RF-10             El sistema debe   Alta              Promedio
                    calcular                            ponderado.
                    automáticamente                     Dashboard visual
                    la calificación                     con semáforo de
                    agregada por                        colores (rojo,
                    característica,                     amarillo, verde).
                    por factor y                        
                    global del                          
                    programa.                           

  RF-11             El sistema debe   Alta              Formato
                    permitir la                         exportable a
                    generación del                      XLSX/PDF.
                    cuadro de                           Estructura
                    autoevaluación                      conforme al
                    con la estructura                   modelo oficial.
                    definida por el                     
                    CNA.                                

  RF-12             El sistema debe   Alta              Informe
                    permitir la                         exportable.
                    consolidación del                   Incluye
                    informe de                          fortalezas,
                    autoevaluación                      debilidades y
                    por programa,                       planes de mejora.
                    factor y                            
                    característica.                     
  -----------------------------------------------------------------------

[]{#_Toc100076 .anchor}**5.4 Módulo 4: Planes de Mejora y Seguimiento**

Derivado de los resultados de la autoevaluación, este módulo permite la
formulación de planes de mejora con acciones específicas, responsables,
plazos y mecanismos de seguimiento. El seguimiento del avance de los
planes de mejora es crítico para el proceso de acreditación, ya que el
CNA evalúa no solo las condiciones actuales del programa sino también la
capacidad institucional de implementar mejoras efectivas. Las
notificaciones automáticas y los reportes de avance facilitan la
coordinación entre los diferentes actores del proceso.

***Tabla 5. Requisitos funcionales -- Módulo 4***

  -----------------------------------------------------------------------
  **ID**            **Requisito**     **Prioridad**     **Criterio de
                                                        aceptación**
  ----------------- ----------------- ----------------- -----------------
  RF-13             El sistema debe   Alta              CRUD de planes.
                    permitir la                         Seguimiento con
                    creación y                          porcentaje de
                    seguimiento de                      avance. Alertas
                    planes de mejora                    de vencimiento.
                    derivados de la                     
                    autoevaluación,                     
                    con acciones,                       
                    responsables,                       
                    fechas y                            
                    porcentaje de                       
                    avance.                             

  RF-14             El sistema debe   Media             Notificaciones
                    enviar                              in-app y por
                    notificaciones                      correo
                    automáticas                         electrónico.
                    cuando una                          Configuración de
                    evidencia es                        preferencias.
                    observada, cuando                   
                    se acerca una                       
                    fecha límite de                     
                    un plan de mejora                   
                    o cuando hay una                    
                    nueva asignación.                   

  RF-15             El sistema debe   Alta              Gráficos de
                    generar reportes                    avance.
                    de avance por                       Exportación a PDF
                    factor, por                         y XLSX.
                    programa y global                   
                    de la                               
                    institución.                        

  RF-16             El sistema debe   Alta              Formato
                    permitir la                         exportable.
                    generación de los                   Estructura
                    cuadros para la                     conforme a las
                    acreditación de                     tablas oficiales
                    calidad en el                       del CNA.
                    formato requerido                   
                    por el CNA.                         
  -----------------------------------------------------------------------

[]{#_Toc100077 .anchor}**5.5 Módulo 5: Autenticación, Roles y
Seguridad**

La seguridad del sistema se fundamenta en la gestión de roles y
permisos, la autenticación robusta a través de Supabase Auth, y la
implementación de Row Level Security (RLS) en la base de datos. Estos
mecanismos garantizan que cada usuario acceda exclusivamente a la
información correspondiente a su rol, programa y factor asignado. El
registro de auditoría permite rastrear todas las acciones realizadas en
el sistema, lo que es fundamental para la transparencia y rendición de
cuentas en un proceso de acreditación.

***Tabla 6. Requisitos funcionales -- Módulo 5***

  -------------------------------------------------------------------------
  **ID**            **Requisito**       **Prioridad**     **Criterio de
                                                          aceptación**
  ----------------- ------------------- ----------------- -----------------
  RF-17             El sistema debe     Alta              Login funcional.
                    implementar                           Recuperación de
                    autenticación                         contraseña.
                    mediante Supabase                     Verificación de
                    Auth con soporte                      email.
                    para                                  
                    correo/contraseña y                   
                    proveedores OAuth                     
                    (Google,                              
                    Microsoft).                           

  RF-18             El sistema debe     Alta              Asignación de
                    gestionar tres                        roles. RLS en
                    roles:                                Supabase por rol.
                    Administrador,                        Interfaz adaptada
                    Líder de Factor y                     al rol.
                    Usuario Operativo,                    
                    con permisos                          
                    diferenciados.                        

  RF-19             El sistema debe     Alta              Políticas RLS
                    implementar Row                       activas. Pruebas
                    Level Security                        de seguridad de
                    (RLS) en todas las                    acceso cruzado.
                    tablas para                           
                    garantizar que cada                   
                    usuario solo acceda                   
                    a los datos de su                     
                    programa y factor                     
                    asignados.                            

  RF-20             El sistema debe     Alta              Registro de
                    mantener un                           usuario,
                    registro de                           acci00f3n,
                    auditoría (log) de                    entidad, fecha y
                    todas las acciones                    detalle.
                    realizadas en el                      Consultable por
                    sistema.                              admin.
  -------------------------------------------------------------------------

[]{#_Toc100078 .anchor}**5.6 Módulo 6: Configuración y Multi-programa**

Este módulo aborda la flexibilidad del sistema para adaptarse a
múltiples programas académicos simultáneamente y a posibles
actualizaciones del modelo de evaluación del CNA. La capacidad de
gestionar n programas con aislamiento completo de datos es un requisito
fundamental, así como la posibilidad de configurar la estructura de
factores y características de manera flexible. Este módulo también
incluye la funcionalidad de comentarios y observaciones, que es
transversal a todos los módulos del sistema.

***Tabla 7. Requisitos funcionales -- Módulo 6***

  -----------------------------------------------------------------------
  **ID**            **Requisito**     **Prioridad**     **Criterio de
                                                        aceptación**
  ----------------- ----------------- ----------------- -----------------
  RF-21             El sistema debe   Media             Edición de
                    permitir la                         factores,
                    configuración de                    características y
                    los 12 factores y                   aspectos.
                    sus                                 Versionado del
                    características                     modelo.
                    de manera                           
                    flexible para                       
                    adaptarse a                         
                    actualizaciones                     
                    del modelo del                      
                    CNA.                                

  RF-22             El sistema debe   Alta              Aislamiento
                    soportar                            completo de datos
                    múltiples                           entre programas.
                    programas                           Sin filtración de
                    académicos de                       datos cruzados.
                    forma simultánea                    
                    con datos                           
                    aislados entre                      
                    programas.                          

  RF-23             El sistema debe   Media             Asignación
                    permitir la                         múltiple. Sin
                    asignación de                       conflictos de
                    líderes de factor                   acceso.
                    por programa,                       
                    pudiendo un líder                   
                    gestionar más de                    
                    un factor en                        
                    programas                           
                    distintos.                          

  RF-24             El sistema debe   Alta              Hilo de
                    permitir el                         comentarios por
                    registro de                         evidencia.
                    observaciones y                     Notificación de
                    comentarios en                      nuevas
                    cada evidencia y                    observaciones.
                    evaluación con                      
                    marca de tiempo y                   
                    usuario.                            
  -----------------------------------------------------------------------

[]{#_Toc100079 .anchor}**6. Requisitos No Funcionales**

Los requisitos no funcionales establecen las características de calidad
del sistema que deben cumplirse para garantizar una experiencia de
usuario satisfactoria y un funcionamiento confiable. Estos requisitos
son tan críticos como los funcionales, ya que un sistema que cumple sus
funciones pero es lento, inseguro o difícil de usar no será adoptado por
la comunidad académica. Los requisitos se organizan en categorías de
rendimiento, disponibilidad, seguridad, escalabilidad, usabilidad,
portabilidad, mantenibilidad y respaldo.

***Tabla 8. Requisitos no funcionales***

  ------------------------------------------------------------------------
  **ID**            **Categoría**     **Requisito**      **Prioridad**
  ----------------- ----------------- ------------------ -----------------
  RNF-01            Rendimiento       El sistema debe    Alta
                                      responder a las    
                                      peticiones del     
                                      usuario en menos   
                                      de 3 segundos para 
                                      el 95% de las      
                                      operaciones,       
                                      incluyendo la      
                                      carga de           
                                      evidencias,        
                                      consultas de       
                                      evaluaciones y     
                                      generación de      
                                      reportes.          

  RNF-02            Disponibilidad    El sistema debe    Alta
                                      garantizar una     
                                      disponibilidad     
                                      mínima del 99.5%,  
                                      lo que equivale a  
                                      un máximo de 43.8  
                                      horas de           
                                      inactividad no     
                                      programada por     
                                      año.               

  RNF-03            Seguridad         Toda la            Alta
                                      comunicación entre 
                                      cliente y servidor 
                                      debe estar cifrada 
                                      mediante HTTPS/TLS 
                                      1.3. Las           
                                      contraseñas deben  
                                      almacenarse con    
                                      hash seguro        
                                      (bcrypt/Argon2)    
                                      vía Supabase Auth. 

  RNF-04            Escalabilidad     El sistema debe    Alta
                                      soportar al menos  
                                      500 usuarios       
                                      concurrentes sin   
                                      degradación del    
                                      rendimiento, con   
                                      capacidad de       
                                      escalamiento       
                                      horizontal         
                                      automático en      
                                      Supabase.          

  RNF-05            Usabilidad        La interfaz debe   Media
                                      ser responsiva y   
                                      accesible desde    
                                      dispositivos       
                                      móviles y de       
                                      escritorio. Debe   
                                      cumplir con los    
                                      estándares WCAG    
                                      2.1 nivel AA.      

  RNF-06            Portabilidad      La aplicación debe Media
                                      funcionar          
                                      correctamente en   
                                      los navegadores    
                                      Chrome, Firefox,   
                                      Safari y Edge en   
                                      sus últimas dos    
                                      versiones.         

  RNF-07            Mantenibilidad    El código debe     Media
                                      seguir principios  
                                      SOLID y contar con 
                                      cobertura de       
                                      pruebas unitarias  
                                      mínima del 70%.    
                                      Documentación      
                                      técnica con        
                                      Swagger/OpenAPI.   

  RNF-08            Respaldo          Se debe realizar   Alta
                                      respaldo           
                                      automático diario  
                                      de la base de      
                                      datos con          
                                      retención de 30    
                                      días. Restauración 
                                      punto-en-tiempo    
                                      disponible.        
  ------------------------------------------------------------------------

[]{#_Toc100080 .anchor}**7. Modelo de Datos (Supabase / PostgreSQL)**

El modelo de datos se implementa en PostgreSQL a través de Supabase. El
diseño sigue principios de normalización hasta la tercera forma normal
(3NF) e incluye mecanismos de seguridad a nivel de fila (RLS) para
garantizar el aislamiento de datos entre programas y el acceso
controlado según el rol del usuario. A continuación se presenta un
resumen de las tablas principales del sistema con sus campos más
relevantes. Las relaciones entre tablas se establecen mediante claves
foráneas (FK) que garantizan la integridad referencial del modelo.

***Tabla 9. Modelo de datos -- Tablas principales***

  ---------------------------------------------------------------------------------------------------------
  **Tabla**               **Descripción**         **Campos principales**
  ----------------------- ----------------------- ---------------------------------------------------------
  instituciones           Instituciones de        id (UUID), nombre, nit, ciudad, estado, created_at
                          educación superior      

  programas               Programas académicos de id (UUID), institucion_id (FK), nombre, nivel
                          formación               (pregrado/posgrado), titulo_otorga, codigo_snies,
                                                  estado_acreditacion, created_at

  factores                Los 12 factores del     id (UUID), numero (1-12), nombre, descripcion
                          modelo de               
                          autoevaluación          

  caracteristicas         48 características (4   id (UUID), factor_id (FK), numero, nombre, descripcion
                          por factor)             

  aspectos_evaluar        Aspectos a evaluar por  id (UUID), caracteristica_id (FK), numero, descripcion
                          cada característica     

  evidencias              Evidencias documentales id (UUID), programa_id (FK), aspecto_id (FK), usuario_id
                          subidas por los         (FK), titulo, descripcion, archivo_url, tipo_archivo,
                          usuarios                tamano, estado (borrador/revisado/aprobado/observado),
                                                  created_at, updated_at

  evaluaciones            Autoevaluación de cada  id (UUID), programa_id (FK), aspecto_id (FK),
                          aspecto por programa    calificacion (1-5), justificacion, fortalezas,
                                                  debilidades, plan_mejora, usuario_id (FK), created_at

  planes_mejora           Planes de mejora        id (UUID), programa_id (FK), evaluacion_id (FK), accion,
                          derivados de la         responsable, fecha_limite, estado, avance (%), created_at
                          autoevaluación          

  usuarios                Usuarios del sistema    id (UUID, auth), institucion_id (FK), nombre, email, rol
                          con roles               (admin/lider_factor/operativo), programa_id (FK),
                                                  factor_id (FK nullable), estado, created_at

  notificaciones          Notificaciones internas id (UUID), usuario_id (FK), tipo, titulo, mensaje, leido,
                          del sistema             created_at

  logs_actividad          Registro de actividades id (UUID), usuario_id (FK), accion, entidad, registro_id,
                          del sistema (auditoría) detalle, ip_address, created_at

  documentos_generados    Informes y documentos   id (UUID), programa_id (FK), tipo
                          generados por el        (informe_autoevaluacion/cuadro_resumen/informe_factor),
                          sistema                 archivo_url, generado_por (FK), created_at
  ---------------------------------------------------------------------------------------------------------

[]{#_Toc100081 .anchor}**7.1 Políticas RLS (Row Level Security)**

La seguridad a nivel de fila es un componente crítico del modelo de
datos. Cada tabla implementará políticas RLS que restrinjan el acceso a
los datos según el rol del usuario y su asignación
institucional/programática. A continuación se describen las políticas
principales: la tabla de evidencias solo es accesible por usuarios del
programa correspondiente y líderes del factor asociado; la tabla de
evaluaciones sigue la misma lógica de acceso; la tabla de usuarios
permite que cada usuario vea solo su propio perfil (excepto el
administrador, que tiene visibilidad total); las tablas de planes de
mejora son accesibles por el administrador, el líder del factor
correspondiente y los usuarios operativos asignados; las tablas de
configuración (factores, características, aspectos) son de lectura para
todos los usuarios autenticados, y de escritura solo para el
administrador.

[]{#_Toc100082 .anchor}**8. Roles y Permisos del Sistema**

El sistema implementa un modelo de control de acceso basado en roles
(RBAC) con tres roles predefinidos. Cada rol tiene un conjunto
específico de permisos que determina qué funcionalidades puede utilizar
y a qué datos puede acceder. La asignación de roles es realizada
exclusivamente por el Administrador de la Plataforma, quien puede
modificar las asignaciones según las necesidades organizacionales. Este
modelo garantiza la separación de responsabilidades y el principio de
mínimo privilegio, aspectos fundamentales para la seguridad y la
integridad del proceso de acreditación.

***Tabla 10. Roles y permisos del sistema***

  -----------------------------------------------------------------------
  **Rol**                 **Descripción**         **Permisos
                                                  principales**
  ----------------------- ----------------------- -----------------------
  Administrador           Gestiona la plataforma  Crear/editar/eliminar
                          a nivel institucional.  programas. Asignar
                          Configura programas,    líderes de factor.
                          asigna líderes de       Gestionar usuarios y
                          factor y usuarios       roles. Ver todas las
                          operativos. Tiene       evidencias y
                          visibilidad total sobre evaluaciones. Generar
                          todas las evidencias,   informes consolidados.
                          evaluaciones y planes   Configurar parámetros
                          de mejora.              del sistema. Acceso
                                                  total a datos de la
                                                  institución.

  Líder de Factor         Responsable de un       Ver evidencias de su
                          factor específico del   factor asignado.
                          modelo de               Revisar y
                          autoevaluación.         aprobar/rechazar
                          Coordina la recolección evidencias. Calificar
                          de evidencias, revisa   aspectos de su factor.
                          las evaluaciones de las Consolidar evaluaciones
                          características y       del factor. Generar
                          aspectos de su factor,  informe del factor.
                          y aprueba o devuelve    Asignar tareas a
                          evidencias con          usuarios operativos de
                          observaciones.          su factor.

  Usuario Operativo       Personal de los         Subir evidencias a los
                          diferentes              aspectos asignados.
                          departamentos de la     Editar evidencias
                          institución que         propias en estado
                          alimenta el sistema con borrador. Ver estado de
                          evidencias              sus evidencias.
                          documentales. Sube      Responder observaciones
                          archivos, registra      del líder. Consultar
                          información sobre los   sus asignaciones y
                          aspectos a evaluar y da tareas pendientes.
                          seguimiento a las       
                          observaciones del líder 
                          de factor.              
  -----------------------------------------------------------------------

[]{#_Toc100083 .anchor}**9. Arquitectura del Sistema**

[]{#_Toc100084 .anchor}**9.1 Arquitectura general**

La arquitectura del sistema sigue el patrón de aplicación web moderna de
tres capas: capa de presentación (frontend), capa de lógica de negocio
(API routes / backend) y capa de datos (Supabase). El frontend se
construye con Next.js 14+ utilizando App Router, React Server Components
y Client Components según corresponda. El backend se implementa mediante
API Routes de Next.js (Route Handlers) que actúan como intermediarios
entre el frontend y Supabase, implementando la lógica de negocio,
validaciones y autorizaciones. Supabase proporciona la base de datos
PostgreSQL, el sistema de autenticación (Supabase Auth), el
almacenamiento de archivos (Supabase Storage) y las funciones de tiempo
real (Supabase Realtime para notificaciones).

[]{#_Toc100085 .anchor}**9.2 Stack tecnológico**

El stack tecnológico seleccionado es el siguiente: Framework web:
Next.js 14+ con App Router. Lenguaje: TypeScript. Biblioteca UI: React
18+ con Server Components. Componentes: shadcn/ui (basado en Radix UI y
Tailwind CSS). Estilos: Tailwind CSS 4. Base de datos: PostgreSQL (a
través de Supabase). ORM/Cliente: Supabase JS Client v2. Autenticación:
Supabase Auth con JWT. Almacenamiento: Supabase Storage. Despliegue:
Vercel (frontend) + Supabase Cloud (backend). Control de versiones:
Git + GitHub. CI/CD: GitHub Actions. Monitoreo: Sentry (errores) +
Vercel Analytics (rendimiento).

[]{#_Toc100086 .anchor}**9.3 Flujo de datos principal**

El flujo de datos principal del sistema sigue el siguiente patrón: (1)
El usuario accede a la aplicación web a través de su navegador, (2)
Next.js renderiza la interfaz con los componentes apropiados según el
rol del usuario, (3) Las operaciones de lectura utilizan Server
Components que consultan directamente Supabase, (4) Las operaciones de
escritura pasan por API Routes que validan permisos, ejecutan la lógica
de negocio y luego interactúan con Supabase, (5) Los archivos de
evidencia se suben a Supabase Storage y se registra la referencia en la
base de datos, (6) Las notificaciones se generan mediante Supabase
Realtime o triggers de base de datos, y (7) Los informes se generan
mediante funciones serverless que consultan los datos y producen
documentos en PDF/XLSX.

[]{#_Toc100087 .anchor}**10. Diseño de Interfaz de Usuario**

La interfaz de usuario se diseña siguiendo principios de usabilidad,
accesibilidad y diseño centrado en el usuario. Se utiliza un sistema de
diseño basado en shadcn/ui con personalización de tema para reflejar la
identidad institucional. La navegación principal se estructura en un
sidebar lateral con acceso a los módulos según el rol del usuario. El
dashboard principal muestra un resumen del estado de la autoevaluación
con indicadores visuales (semáforos, barras de progreso, gráficos). Las
vistas de gestión de evidencias permiten la subida drag-and-drop de
archivos, la visualización previa de documentos y la organización por
factor, característica y aspecto.

[]{#_Toc100088 .anchor}**10.1 Vistas principales**

Las vistas principales del sistema incluyen: Dashboard con indicadores
de avance general del proceso de autoevaluación; Vista de Programa con
la estructura de los 12 factores y el estado de cada uno; Vista de
Factor con las 4 características y sus aspectos, evidencias y
evaluaciones; Vista de Evidencias con lista, filtros, subida y detalle
de cada evidencia; Vista de Evaluación con formulario de calificación y
justificación; Vista de Planes de Mejora con seguimiento de acciones;
Vista de Informes con generación y descarga de documentos; y Vista de
Administración con gestión de usuarios, programas y configuración.

[]{#_Toc100089 .anchor}**10.2 Principios de diseño**

Los principios de diseño que guían la interfaz son: Consistencia visual
y funcional en toda la aplicación. Retroalimentación inmediata ante las
acciones del usuario (toasts, estados de carga, confirmaciones).
Navegación intuitiva con migas de pan y contextual help. Diseño
responsivo que se adapte a pantallas de escritorio, tablet y móvil.
Accesibilidad WCAG 2.1 nivel AA con contraste adecuado, navegación por
teclado y lectores de pantalla. Rendimiento percibido con carga
progresiva y skeleton loaders. Personalización institucional con
colores, logo y nombre de la institución.

[]{#_Toc100090 .anchor}**11. Plan de Implementación**

El plan de implementación se estructura en cuatro fases incrementales
que permiten entregas parciales funcionales y retroalimentación continua
de los stakeholders. Cada fase tiene entregables definidos, criterios de
aceptación y una duración estimada basada en la complejidad de los
módulos involucrados.

[]{#_Toc100091 .anchor}**11.1 Fase 1: Fundamentos (Semanas 1-6)**

La primera fase se enfoca en la configuración del proyecto, la
implementación del modelo de datos en Supabase, el sistema de
autenticación con roles, y la gestión básica de instituciones y
programas. Los entregables incluyen: repositorio configurado con Next.js
y TypeScript, esquema de base de datos desplegado en Supabase con
políticas RLS, sistema de autenticación funcional con Supabase Auth, y
CRUD de instituciones y programas académicos.

[]{#_Toc100092 .anchor}**11.2 Fase 2: Evidencias y Evaluación (Semanas
7-14)**

La segunda fase aborda el núcleo funcional del sistema: la gestión de
evidencias con flujo de trabajo completo y la autoevaluación de
factores, características y aspectos. Los entregables incluyen: subida y
gestión de evidencias con versionamiento, flujo de trabajo de revisión
(borrador, revisión, aprobación, observación), formulario de
autoevaluación por aspecto, calificación agregada por característica y
factor, y dashboard de avance del proceso.

[]{#_Toc100093 .anchor}**11.3 Fase 3: Informes y Planes de Mejora
(Semanas 15-20)**

La tercera fase completa la funcionalidad del sistema con la generación
de informes y cuadros de autoevaluación, y la gestión de planes de
mejora. Los entregables incluyen: generación de cuadro de autoevaluación
en XLSX/PDF, informe consolidado por programa, gestión de planes de
mejora con seguimiento, notificaciones automáticas (in-app y email), y
reportes de avance.

[]{#_Toc100094 .anchor}**11.4 Fase 4: Optimización y Despliegue (Semanas
21-24)**

La cuarta y última fase se dedica a la optimización del rendimiento, las
pruebas exhaustivas, la documentación y el despliegue en producción. Los
entregables incluyen: pruebas unitarias e integración con cobertura
mayor al 70%, pruebas de rendimiento y seguridad, documentación técnica
y manual de usuario, despliegue en producción (Vercel + Supabase Cloud),
capacitación a usuarios finales, y plan de mantenimiento y soporte.

[]{#_Toc100095 .anchor}**12. Glosario**

Acreditación: Reconocimiento público que el Estado otorga a un programa
académico de educación superior que demuestra condiciones de calidad de
manera voluntaria. Aspecto a evaluar: Elemento específico dentro de una
característica que se debe valorar durante la autoevaluación.
Autoevaluación: Proceso mediante el cual una institución de educación
superior examina críticamente sus condiciones y procesos en relación con
los factores y características definidos en el modelo de acreditación.
Característica: Componente específico de un factor que permite
identificar y valorar una condición de calidad del programa académico.
CESU: Consejo Nacional de Educación Superior, máximo órgano de dirección
de la educación superior en Colombia. CNA: Consejo Nacional de
Acreditación, organismo encargado de la acreditación de programas e
instituciones de educación superior. Evidencia: Documento, dato o
información que soporta y demuestra las condiciones de calidad del
programa en relación con un aspecto a evaluar. Factor: Categoría macro
del modelo de acreditación que agrupa un conjunto de características
relacionadas con una dimensión de calidad del programa. Plan de mejora:
Conjunto de acciones y compromisos que una institución adopta para
superar las debilidades identificadas en el proceso de autoevaluación.
RLS: Row Level Security, mecanismo de PostgreSQL que permite definir
políticas de acceso a nivel de fila en las tablas de la base de datos.
SNIES: Sistema Nacional de Información de la Educación Superior,
registro oficial de programas académicos en Colombia.

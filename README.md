![Logo de ConsentLex](https://github.com/bladealex9848/Consentlex/blob/main/assets/logo.jpg)

# ConsentLex ⚖️ - Sistema Experto en Consentimiento Informado

[![Version](https://img.shields.io/badge/versión-1.0.0-darkgreen.svg)](https://github.com/consentlex/consentlex-expert-system)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30.0-ff4b4b.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI_API-v2-00C244.svg)](https://platform.openai.com/)
[![Licencia](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](LICENSE)

## ⚖️ Descripción

ConsentLex es un sistema experto avanzado diseñado para el análisis, evaluación y creación de consentimientos informados médico-legales. Esta plataforma integra la capacidad analítica de los modelos más avanzados de OpenAI con un profundo conocimiento de la normativa colombiana y estándares internacionales sobre consentimiento informado, ofreciendo una solución integral para profesionales de la salud, jurídicos e instituciones médicas.

Basado en la "Guía Completa para el Control de Legalidad y Elaboración de Consentimientos Informados", ConsentLex proporciona asesoramiento especializado en:

- Evaluación de conformidad legal de consentimientos existentes
- Creación de nuevos formatos personalizados según procedimiento médico
- Asesoría sobre normativa aplicable y jurisprudencia relevante
- Identificación de riesgos y vulnerabilidades en documentos
- Optimización de lenguaje para garantizar la comprensión del paciente

## 🔍 Características Principales

### 1. Análisis Integral de Conformidad Legal
- **Control de Legalidad Exhaustivo**: Verificación contra estándares normativos vigentes
- **Detección de Deficiencias**: Identificación de elementos faltantes o inadecuados
- **Evaluación de Riesgos**: Análisis de vulnerabilidades jurídicas potenciales
- **Informes Detallados**: Reportes estructurados con hallazgos y recomendaciones
- **Verificación de Jurisprudencia**: Contraste con decisiones judiciales relevantes

### 2. Diseño Personalizado de Documentos
- **Creación por Especialidad**: Formatos específicos según tipo de procedimiento
- **Adaptación por Contexto**: Versiones para diferentes perfiles de pacientes
- **Lenguaje Comprensible**: Redacción clara sin sacrificar precisión técnica
- **Estructura Normativa Completa**: Inclusión de todos los elementos legalmente requeridos
- **Formatos Editables**: Documentos listos para implementación institucional

### 3. Plataforma Técnicamente Robusta
- **Arquitectura Resiliente**: Diseño con manejo avanzado de errores y recuperación automática
- **Procesamiento IA Optimizado**: Integración con OpenAI Assistants API v2
- **Sistema de Diagnóstico Integrado**: Herramientas internas para resolución de problemas
- **Compatibilidad Multiplataforma**: Funcionamiento en diversos entornos de despliegue
- **Seguridad en el Manejo de Datos**: Protección de información sensible

### 4. Áreas de Especialización
- **Procedimientos Quirúrgicos**: Consentimientos para diversas intervenciones quirúrgicas
- **Procedimientos Diagnósticos**: Documentos para estudios con y sin medios de contraste
- **Transfusiones**: Formatos especializados para hemoderivados
- **Anestesia**: Consentimientos específicos para procedimientos anestésicos
- **Casos Especiales**: Adaptaciones para menores, situaciones de urgencia e investigación clínica

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- Pip (administrador de paquetes de Python)
- Cuenta en OpenAI con acceso a la API
- Asistente ConsentLex configurado en OpenAI

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/bladealex9848/Consentlex.git
   cd consentlex-expert-system
   ```

2. **Crear un entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar credenciales de OpenAI**

   **Opción A: Usando variables de entorno**
   ```bash
   # En Windows
   set OPENAI_API_KEY=tu-api-key-aqui
   set ASSISTANT_ID=tu-assistant-id-aqui
   set OPENAI_API_MODEL=gpt-4o-mini
   
   # En macOS/Linux
   export OPENAI_API_KEY=tu-api-key-aqui
   export ASSISTANT_ID=tu-assistant-id-aqui
   export OPENAI_API_MODEL=gpt-4o-mini
   ```

   **Opción B: Usando archivo secrets.toml**
   
   Crea un archivo `.streamlit/secrets.toml` con el siguiente contenido:
   ```toml
   OPENAI_API_KEY = "tu-api-key-aqui"
   ASSISTANT_ID = "tu-assistant-id-aqui"
   OPENAI_API_MODEL = "gpt-4o-mini"
   ```

   **Opción C: Configuración por interfaz**
   
   También puedes introducir las credenciales directamente en la interfaz de usuario al ejecutar la aplicación.

## ⚖️ Uso

1. **Iniciar la aplicación**
   ```bash
   streamlit run app.py
   ```

2. **Acceder a la interfaz web**
   
   Abre tu navegador y dirígete a `http://localhost:8501`

3. **Interactuar con ConsentLex**
   
   - **Evaluación de documentos**: Carga un consentimiento existente para su análisis
   - **Creación de consentimientos**: Especifica el tipo de procedimiento, perfil de pacientes y contexto institucional
   - **Consulta normativa**: Solicita información sobre legislación específica
   - **Diagnóstico técnico**: Utiliza el panel de diagnóstico si experimentas problemas

## ⚙️ Configuración Avanzada

### Personalización del Modelo de IA

Configura diferentes modelos de OpenAI editando el valor de `OPENAI_API_MODEL` en tu archivo `.streamlit/secrets.toml`:


# Opciones recomendadas según caso de uso
```
OPENAI_API_MODEL = "gpt-4o-mini"    # Balance efectividad/economía (predeterminado)
OPENAI_API_MODEL = "gpt-4o"         # Análisis legal más profundo
OPENAI_API_MODEL = "gpt-4-turbo"    # Alternativa para análisis complejos
```

### Optimización de Rendimiento

Para adaptar el sistema a diferentes entornos de ejecución:

# En el archivo app.py
timeout = 60  # Aumenta para análisis más exhaustivos, reduce para mayor responsividad
max_retries = 3  # Configura número de reintentos en caso de errores de conexión
recovery_delay = 1.0  # Ajusta el tiempo entre reintentos (backoff exponencial)


### Personalización Visual y de Interfaz

Para modificar los colores y estilos de la interfaz, edita el diccionario `COLORS` en el archivo `app.py`:

```
COLORS = {
    "primary": "#2F4F4F",     # Verde oscuro (profesional legal)
    "secondary": "#192841",   # Azul marino (confianza)
    "accent1": "#6B8E23",     # Verde oliva (documentos legales)
    "accent2": "#CD853F",     # Marrón (sellos legales)
    # ... otros colores
}
```

## 🔍 Diagnóstico y Solución de Problemas

### Panel de Diagnóstico Integrado

ConsentLex incluye un panel de diagnóstico completo accesible desde el menú de navegación que permite:

- Verificar el estado de todos los componentes del sistema
- Probar la conectividad con servicios externos
- Examinar la información de sesión y entorno
- Realizar operaciones de mantenimiento como limpieza de caché

### Problemas Comunes y Soluciones

| Problema | Posible Causa | Solución |
|----------|---------------|----------|
| Error "API key no configurada" | Credenciales de OpenAI no proporcionadas | Verifica la configuración en `.streamlit/secrets.toml` o variables de entorno |
| Error "No se pudo inicializar thread" | Problemas de conexión a OpenAI | Verifica tu conectividad a Internet y la validez de tu API key |
| Falla en la carga de documentos | Formato no soportado o tamaño excesivo | Utiliza formatos compatibles (PDF, DOCX, TXT) y verifica el tamaño |
| Errores en la renderización | Problemas con componentes visuales | Utiliza el botón "Limpieza de Caché" en el panel de diagnóstico |
| Error "openai_client_error" | Problemas específicos de conexión con OpenAI | Consulta los logs detallados y utiliza la opción "Reintentar conexión" |

### Logs y Monitoreo

El sistema genera logs detallados para diagnóstico y auditoría:

```
2025-03-30 10:15:22,531 - consentlex - INFO - Thread creado: thread_abc123xyz...
2025-03-30 10:15:24,108 - consentlex - INFO - Documento cargado: consentimiento_cirugia.pdf
```

Para mejorar el diagnóstico, puedes ajustar el nivel de detalle de los logs:


# Configuración para logs más detallados
```
logging.basicConfig(
    level=logging.DEBUG,  # Cambia a DEBUG para información más detallada
    format="%(asctime)s - consentlex - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d",
    handlers=[logging.StreamHandler(), logging.FileHandler("consentlex.log")]
)
```

## 🔄 Actualizaciones y Versiones

### Historial de Versiones

- **v1.0.0**: Lanzamiento inicial con funcionalidades básicas (actual)
  - Sistema de análisis de documentos
  - Creación de consentimientos personalizados
  - Compatibilidad con OpenAI Assistants API v2
  - Panel de diagnóstico integrado

### Próximas Mejoras Planificadas

- [ ] **v1.1.0**: Biblioteca ampliada de plantillas por especialidad
- [ ] **v1.2.0**: Sistema de exportación en múltiples formatos (PDF, DOCX, HTML)
- [ ] **v1.3.0**: Análisis comparativo contra múltiples estándares normativos
- [ ] **v2.0.0**: Implementación de panel administrativo multiusuario
- [ ] **v2.1.0**: Integración con sistemas de gestión hospitalaria

## 🛡️ Seguridad y Privacidad

ConsentLex implementa medidas robustas para proteger la información sensible:

- **Transmisión Segura**: Comunicaciones cifradas con la API de OpenAI
- **Manejo Local de Documentos**: Los archivos cargados se procesan localmente
- **No Persistencia de Datos**: La información no se almacena permanentemente
- **Sanitización de Entrada**: Validación de todas las entradas de usuario
- **Gestión Segura de Credenciales**: Las claves API nunca se exponen en la interfaz

## 👥 Contribuciones

Las contribuciones son bienvenidas y valoradas. Para contribuir al desarrollo de ConsentLex:

1. Realiza un fork del repositorio
2. Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`)
3. Implementa tus cambios con pruebas adecuadas
4. Documenta las modificaciones siguiendo el estándar del proyecto
5. Envía un Pull Request con una descripción detallada

Antes de contribuir, consulta nuestras guías de contribución para asegurar la coherencia del código y la documentación.

## 📝 Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- **OpenAI** por proporcionar la tecnología que impulsa el análisis avanzado
- **Streamlit** por facilitar el desarrollo de interfaces intuitivas con Python
- **Expertos legales y médicos** por sus valiosas contribuciones a la base de conocimiento

## 👤 Autor

Creado con ❤️ por [Alexander Oviedo Fadul](https://github.com/bladealex9848)

[GitHub](https://github.com/bladealex9848) | [Website](https://alexanderoviedofadul.dev) | [LinkedIn](https://www.linkedin.com/in/alexander-oviedo-fadul/) | [Instagram](https://www.instagram.com/alexander.oviedo.fadul) | [Twitter](https://twitter.com/alexanderofadul) | [Facebook](https://www.facebook.com/alexanderof/) | [WhatsApp](https://api.whatsapp.com/send?phone=573015930519&text=Hola%20!Quiero%20conversar%20contigo!%20)

---

## 💼 Mensaje Final

ConsentLex representa un puente entre la complejidad normativa y la práctica médica, transformando el proceso de gestión de consentimientos informados. Nuestro compromiso es garantizar que estos documentos cumplan su verdadera función: proteger tanto los derechos de los pacientes como la seguridad jurídica de los profesionales de la salud.

*"Un consentimiento informado efectivo no es solo un documento legal, sino el fundamento de una relación médico-paciente basada en la transparencia y el respeto mutuo."*
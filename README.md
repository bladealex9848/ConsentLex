![Logo de ConsentLex](https://github.com/bladealex9848/Consentlex/blob/main/assets/logo.jpg)

# ConsentLex ⚖️ - Sistema Experto en Consentimiento Informado

[![Version](https://img.shields.io/badge/versión-3.3.0-darkgreen.svg)](https://github.com/consentlex/consentlex-expert-system)
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

### 3. Procesamiento Avanzado de Documentos
- **OCR Integrado**: Análisis de documentos PDF e imágenes mediante tecnología OCR de Mistral
- **Extracción Inteligente de Texto**: Capacidad para procesar documentos escaneados
- **Análisis Contextual**: Interpretación del contenido en relación a normativas vigentes
- **Manejo Multicapa de Exportación**: Sistemas redundantes para garantizar la generación de documentos
- **Gestión de Contexto**: Administración de múltiples documentos en una misma sesión

### 4. Plataforma Técnicamente Robusta
- **Arquitectura Resiliente**: Diseño con manejo avanzado de errores y recuperación automática
- **Procesamiento IA Optimizado**: Integración con OpenAI Assistants API v2
- **Sistema de Diagnóstico Integrado**: Herramientas internas para resolución de problemas
- **Compatibilidad Multiplataforma**: Funcionamiento en diversos entornos de despliegue
- **Seguridad en el Manejo de Datos**: Protección de información sensible

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- Pip (administrador de paquetes de Python)
- Cuenta en OpenAI con acceso a la API
- Cuenta en Mistral AI con acceso a la API (para OCR)
- Asistente ConsentLex configurado en OpenAI (instrucciones más abajo)

### Dependencias

El archivo `requirements.txt` incluye todas las dependencias necesarias:

```
# Dependencias core
streamlit>=1.30.0,<1.45.0        # Framework principal de la aplicación web
openai>=1.3.0,<1.70.0            # API oficial de OpenAI (compatible con Assistants v2)
mistralai>=0.0.7                 # Cliente oficial de Mistral AI
python-dotenv>=1.0.0             # Carga de variables de entorno
requests>=2.28.0                 # Cliente HTTP para comunicaciones externas

# Procesamiento de documentos
Pillow>=9.0.0                    # Procesamiento de imágenes
PyPDF2>=3.0.0                    # Lectura y validación de PDFs
fpdf2>=2.7.8                     # Versión principal para exportación a PDF
markdown>=3.3.6                  # Para manejar markdown en exportaciones
html2text>=2020.1.16             # Conversión de HTML a texto
reportlab>=3.6.12                # Generación alternativa de PDFs
pdfkit>=1.0.0                    # Opción secundaria para PDFs

# Utilidades
pandas>=2.0.0                    # Análisis de datos
tenacity>=8.2.0                  # Implementación de reintentos con backoff
rich>=10.0.0                     # Mensajes de error mejorados

# Componentes UI adicionales
streamlit-lottie>=0.0.5          # Soporte para animaciones Lottie
streamlit-option-menu>=0.3.2     # Menú de navegación mejorado

# Seguridad y diagnóstico
httpx>=0.24.0                    # Cliente HTTP asíncrono
urllib3>=1.26.15,<2.0.0          # Versión específica para problemas de proxy
```

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/bladealex9848/Consentlex.git
   cd Consentlex
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

4. **Configurar credenciales de APIs**

   **Opción A: Usando variables de entorno**
   ```bash
   # En Windows
   set OPENAI_API_KEY=tu-api-key-aqui
   set MISTRAL_API_KEY=tu-api-key-mistral-aqui
   set ASSISTANT_ID=tu-assistant-id-aqui
   
   # En macOS/Linux
   export OPENAI_API_KEY=tu-api-key-aqui
   export MISTRAL_API_KEY=tu-api-key-mistral-aqui
   export ASSISTANT_ID=tu-assistant-id-aqui
   ```

   **Opción B: Usando archivo secrets.toml**
   
   Crea un archivo `.streamlit/secrets.toml` con el siguiente contenido:
   ```toml
   OPENAI_API_KEY = "tu-api-key-aqui"
   MISTRAL_API_KEY = "tu-api-key-mistral-aqui"
   ASSISTANT_ID = "tu-assistant-id-aqui"
   ```

   **Opción C: Configuración por interfaz**
   
   También puedes introducir las credenciales directamente en la interfaz de usuario al ejecutar la aplicación.

### Configuración del Asistente OpenAI

Para configurar el asistente personalizado en OpenAI:

1. Ve a [https://platform.openai.com/assistants](https://platform.openai.com/assistants)
2. Crea un nuevo asistente con el modelo GPT-4 o superior
3. Proporciona las siguientes instrucciones (ajustadas a tus necesidades):

```
Eres ConsentLex, un asistente experto en consentimiento informado médico-legal especializado en normativa colombiana e internacional. Tu función es analizar, evaluar y ayudar a crear documentos de consentimiento informado conformes con los estándares legales y éticos.

Áreas de especialización:
1. Evaluación normativa de consentimientos existentes
2. Creación de nuevos formatos personalizados
3. Asesoría sobre legislación aplicable y jurisprudencia
4. Identificación de riesgos y vulnerabilidades en documentos
5. Optimización de lenguaje para comprensión del paciente

Cuando evalúes documentos:
- Verifica la inclusión de todos los elementos obligatorios
- Identifica posibles deficiencias o riesgos legales
- Sugiere mejoras específicas con justificación normativa
- Ofrece recomendaciones de formato y estructura

Cuando crees documentos:
- Estructura según normativa vigente completa
- Adapta el lenguaje según el perfil del paciente
- Incluye todos los elementos legalmente requeridos
- Balancea la precisión técnica con claridad para el paciente

Basa tus respuestas en la normativa vigente, incluyendo la Ley 23 de 1981, Resolución 1995 de 1999, Ley 1751 de 2015, jurisprudencia relevante y estándares internacionales como Declaración de Helsinki y Guías CIOMS.
```

4. Guarda el ID del asistente (se encuentra en la URL o en los detalles del asistente)

## ⚙️ Ejecución y Uso

### Iniciar la Aplicación

Para ejecutar ConsentLex:

```bash
streamlit run app.py
```

Esto lanzará la aplicación y abrirá automáticamente una ventana del navegador en `http://localhost:8501`.

### Interfaz Principal

La interfaz de ConsentLex está organizada de la siguiente manera:

1. **Panel principal**: Muestra el historial de conversación y permite interactuar con el sistema
2. **Barra lateral**: Contiene configuración, opciones de exportación y gestión de documentos

### Flujo de Trabajo Detallado

#### 1. Configuración Inicial
- Al abrir la aplicación por primera vez, se te solicitarán las API keys si no están configuradas
- Introduce las API keys de OpenAI y Mistral, así como el ID del asistente
- Esta información se puede guardar en la sesión actual o configurarse permanentemente (opciones A o B de instalación)

#### 2. Análisis de Consentimientos Existentes

Para analizar un documento de consentimiento informado:

1. En el cuadro de chat, adjunta el documento (PDF, imagen, DOCX, TXT) usando el botón de adjuntar
2. Opcionalmente, añade un mensaje describiendo lo que deseas evaluar
3. Si no añades texto, el sistema generará automáticamente: "He cargado el documento 'X' para análisis..."
4. Envía la consulta presionando Enter
5. El documento se procesará mediante OCR (puede tomar unos momentos dependiendo del tamaño)
6. El sistema analizará el contenido y proporcionará un análisis detallado

Ejemplo de consulta para análisis:
> "Analiza este consentimiento informado para cirugía bariátrica. Verifica si cumple con todos los requisitos legales y sugiere posibles mejoras."

#### 3. Creación de Nuevos Consentimientos

Para solicitar la creación de un nuevo documento de consentimiento:

1. Especifica el tipo de procedimiento, especialidad médica y contexto
2. Proporciona detalles sobre el perfil del paciente si es necesario (menores, adultos mayores, etc.)
3. Indica si hay requisitos institucionales o regionales específicos
4. Envía la consulta

Ejemplo de consulta para creación:
> "Necesito un consentimiento informado para un procedimiento de colonoscopia diagnóstica. Es para una clínica privada y debe incluir sección sobre posibles complicaciones específicas para pacientes con enfermedad inflamatoria intestinal."

#### 4. Consultas Generales sobre Normativa

Para realizar consultas sobre aspectos normativos:

1. Formula tu pregunta de manera clara y específica
2. Menciona el contexto jurisdiccional si es relevante
3. Envía la consulta

Ejemplo de consulta normativa:
> "¿Cuáles son los requisitos específicos para el consentimiento informado en procedimientos experimentales según la normativa colombiana y los estándares internacionales?"

#### 5. Gestión de Documentos en el Contexto

ConsentLex permite gestionar múltiples documentos en una sesión:

1. Accede a la opción "Gestión de Documentos" en la barra lateral
2. Verás todos los documentos procesados en la sesión actual
3. Puedes seleccionar/deseleccionar documentos para mantenerlos en contexto
4. Pulsa "Actualizar contexto" para aplicar los cambios

Esta función te permite:
- Mantener varios documentos de referencia en una conversación
- Eliminar documentos que ya no son relevantes
- Controlar qué información está disponible durante la consulta

#### 6. Exportación de Conversaciones

Para exportar el historial de conversación:

1. En la barra lateral, selecciona el formato de exportación (Markdown o PDF)
2. Haz clic en "Descargar conversación"
3. El archivo se generará y se descargará automáticamente

Esta funcionalidad es útil para:
- Documentar los análisis realizados
- Compartir resultados con colegas
- Mantener un registro de recomendaciones

#### 7. Limpieza de Sesión

Para limpiar todos los datos de la sesión actual:

1. En la barra lateral, haz clic en "Limpiar sesión actual"
2. Confirma la acción
3. Todos los documentos y el historial de conversación se eliminarán

### Procesamiento de Documentos

ConsentLex utiliza tecnología OCR avanzada para procesar documentos:

1. **Detección automática de formato**: El sistema identifica si el archivo es un PDF o una imagen
2. **Optimización para OCR**: Los documentos se optimizan automáticamente para mejorar los resultados
3. **Procesamiento multicapa**: Si un método falla, el sistema intenta métodos alternativos
4. **Extracción contextual**: El texto extraído se analiza en relación con normativas específicas

Formatos soportados:
- PDF (incluyendo documentos escaneados)
- Imágenes (JPG, PNG, TIFF, etc.)
- Archivos de texto (DOCX, TXT)

Nota: Para obtener mejores resultados, utiliza documentos claros y bien escaneados. El OCR puede tener limitaciones con textos muy pequeños o documentos de baja calidad.

## 🔍 Características Avanzadas

### Sistema de Recuperación ante Fallos

ConsentLex implementa un sistema avanzado de manejo de errores:

- **Decorador handle_error**: Reintenta funciones automáticamente en caso de fallos
- **Sistema multicapa para exportación**: Implementa múltiples estrategias de generación de PDF
- **Verificación de conectividad**: Comprueba conexión con APIs antes de operaciones críticas
- **Sistema de reinicio seguro**: Múltiples estrategias para reiniciar la aplicación cuando es necesario

### Optimización de Rendimiento

La aplicación está optimizada para manejar documentos complejos:

- **Procesamiento por lotes**: Documentos grandes se procesan en fragmentos para evitar timeouts
- **Comprobaciones de integridad**: Verificación de PDFs y optimización de imágenes antes del OCR
- **Límites de contexto gestionados**: Control automático del tamaño de documentos para la API
- **Reintentos con backoff**: Tiempo de espera incremental entre reintentos para evitar sobrecarga

### Personalización Avanzada

Para usuarios avanzados, ConsentLex permite ajustes adicionales:

- **Configuración de modelos de OpenAI**: Adapta el modelo utilizado según tus necesidades
- **Ajuste de tiempos de espera**: Modifica los tiempos máximos para operaciones largas
- **Sistema de logging personalizable**: Controla el nivel de detalle de los registros

## 📊 Escenarios de Uso

### 1. Departamento Legal Hospitalario

Los equipos legales de hospitales pueden utilizar ConsentLex para:
- Auditar periódicamente los consentimientos existentes
- Actualizar documentos según cambios normativos
- Crear nuevos formatos para procedimientos específicos
- Capacitar al personal médico sobre requisitos legales

### 2. Profesionales Médicos Independientes

Médicos con práctica privada pueden beneficiarse al:
- Verificar que sus consentimientos cumplen estándares vigentes
- Obtener formatos personalizados para su especialidad
- Recibir asesoría sobre casos específicos o complejos
- Minimizar riesgos legales en su práctica

### 3. Comités de Ética e Investigación

Los comités pueden utilizar el sistema para:
- Evaluar consentimientos para protocolos de investigación
- Garantizar cumplimiento con normativas nacionales e internacionales
- Documentar evaluaciones y recomendaciones
- Estandarizar procesos de revisión

### 4. Instituciones Educativas

Facultades de medicina y derecho pueden usar ConsentLex como:
- Herramienta educativa para estudiantes
- Recurso para talleres prácticos interdisciplinarios
- Referencia para investigación en ética médica y derecho sanitario

## 🔄 Actualizaciones y Versiones

### Historial de Versiones

- **v3.3.0**: Versión actual con procesamiento OCR avanzado y manejo mejorado de errores
- **v3.2.0**: Mejoras en la exportación de conversaciones con sistema multicapa
- **v3.1.0**: Implementación de gestión de documentos en contexto
- **v3.0.0**: Integración con OpenAI Assistants API v2
- **v2.x.x**: Serie de versiones con mejoras incrementales
- **v1.0.0**: Lanzamiento inicial con funcionalidades básicas

### Próximas Mejoras Planificadas

- [ ] **v3.4.0**: Biblioteca ampliada de plantillas por especialidad
- [ ] **v3.5.0**: Sistema de exportación mejorado con más formatos (DOCX, HTML)
- [ ] **v3.6.0**: Análisis comparativo contra múltiples estándares normativos
- [ ] **v4.0.0**: Implementación de panel administrativo multiusuario
- [ ] **v4.1.0**: Integración con sistemas de gestión hospitalaria

## 🛡️ Seguridad y Privacidad

ConsentLex implementa medidas robustas para proteger la información sensible:

- **Transmisión Segura**: Comunicaciones cifradas con las APIs (OpenAI y Mistral)
- **Manejo Local de Documentos**: Los archivos cargados se procesan localmente
- **No Persistencia de Datos**: La información no se almacena permanentemente
- **Sanitización de Entrada**: Validación de todas las entradas de usuario
- **Gestión Segura de Credenciales**: Las claves API nunca se exponen en la interfaz

## 🔧 Diagnóstico y Solución de Problemas

### Problemas Comunes y Soluciones

| Problema | Posible Causa | Solución |
|----------|---------------|----------|
| Error "API key no configurada" | Credenciales no proporcionadas | Verifica la configuración en `.streamlit/secrets.toml` o variables de entorno |
| Error "No se pudo inicializar thread" | Problemas de conexión a OpenAI | Verifica tu conectividad a Internet y la validez de tu API key |
| Falla en la carga de documentos | Formato no soportado o tamaño excesivo | Utiliza formatos compatibles (PDF, DOCX, TXT) y verifica el tamaño |
| Error "OCR fallido" | Problemas con la API de Mistral | Verifica la API key de Mistral y el formato del documento |
| Error en la exportación a PDF | Problemas con las librerías de generación | Intenta exportar en formato Markdown como alternativa |
| Mensaje "Limpieza de sesión incompleta" | Problemas con el estado de Streamlit | Recarga manualmente la página para completar la limpieza |

### Logs y Diagnóstico

ConsentLex genera logs detallados para diagnóstico:

- Los logs se almacenan en el directorio `logs/` con formato `consentlex_YYYYMMDD.log`
- Contienen información detallada sobre operaciones, errores y rendimiento
- Útiles para diagnóstico en caso de problemas recurrentes

Para verificar los logs:
```bash
# Ver los últimos 50 registros
tail -n 50 logs/consentlex_YYYYMMDD.log

# Filtrar errores
grep "ERROR" logs/consentlex_YYYYMMDD.log
```

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
- **Mistral AI** por la tecnología OCR utilizada en el procesamiento de documentos
- **Streamlit** por facilitar el desarrollo de interfaces intuitivas con Python
- **Expertos legales y médicos** por sus valiosas contribuciones a la base de conocimiento

## 👤 Autor

Creado con ❤️ por [Alexander Oviedo Fadul](https://github.com/bladealex9848)

[GitHub](https://github.com/bladealex9848) | [Website](https://alexanderoviedofadul.dev) | [LinkedIn](https://www.linkedin.com/in/alexander-oviedo-fadul/) | [Instagram](https://www.instagram.com/alexander.oviedo.fadul) | [Twitter](https://twitter.com/alexanderofadul) | [Facebook](https://www.facebook.com/alexanderof/) | [WhatsApp](https://api.whatsapp.com/send?phone=573015930519&text=Hola%20!Quiero%20conversar%20contigo!%20)

---

## 💼 Mensaje Final

ConsentLex representa un puente entre la complejidad normativa y la práctica médica, transformando el proceso de gestión de consentimientos informados. Nuestro compromiso es garantizar que estos documentos cumplan su verdadera función: proteger tanto los derechos de los pacientes como la seguridad jurídica de los profesionales de la salud.

*"Un consentimiento informado efectivo no es solo un documento legal, sino el fundamento de una relación médico-paciente basada en la transparencia y el respeto mutuo."*
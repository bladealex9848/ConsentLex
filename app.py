import os
import streamlit as st
import time
import base64
import json
import requests
import tempfile
import logging
import traceback
import io
import sys
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image
from openai import OpenAI
import uuid
import streamlit.components.v1 as components

# Configuración avanzada de logging - Implementación multi-destino
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"consentlex_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - consentlex - %(levelname)s [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file)
    ]
)

# Versión de la aplicación
APP_VERSION = "3.3.0"

# Configuración de página Streamlit
st.set_page_config(
    page_title="ConsentLex | Experto en Consentimiento Informado",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",  # Menú lateral contraído por defecto
    menu_items={
        "Get Help": "https://www.consentlex.com/help",
        "Report a bug": None,
        "About": "ConsentLex: Sistema experto para análisis y creación de consentimientos informados médico-legales.",
    },
)

# Decorador para manejo de errores con retries
def handle_error(max_retries=2):
    """
    Decorador avanzado para manejo de errores con capacidad de reintento
    
    Parámetros:
        max_retries: Número máximo de reintentos ante fallos
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            last_exception = None
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_msg = f"Error en {func.__name__} (intento {retries+1}/{max_retries+1}): {str(e)}"
                    logging.error(error_msg)
                    
                    if retries < max_retries:
                        logging.info(f"Reintentando {func.__name__}...")
                        retries += 1
                        time.sleep(1)  # Espera antes de reintentar
                    else:
                        logging.error(f"Error final después de {max_retries+1} intentos: {traceback.format_exc()}")
                        st.error(error_msg)
                        break
                        
            return None
        return wrapper
    return decorator

# Sistema multicapa para reinicio de la aplicación
def rerun_app():
    """
    Sistema multicapa para reiniciar la aplicación Streamlit.
    Implementa múltiples estrategias de recuperación en caso de fallo.
    """
    try:
        # Método 1 (preferido): Función actual en Streamlit
        st.rerun()
    except (AttributeError, Exception) as e:
        logging.warning(f"Método primario de reinicio falló: {str(e)}")
        
        # Método 2: Mensaje al usuario con opción manual
        st.info("Por favor, recarga la página para ver los cambios")
        
        # Método 3: Intento con JavaScript nativo
        try:
            html_code = """
            <script>
                // Reintento con un retraso para permitir renderización
                setTimeout(function() {
                    window.parent.location.reload();
                }, 2000);
            </script>
            """
            st.components.v1.html(html_code, height=0, width=0)
        except Exception as e3:
            logging.error(f"Reinicio con JavaScript falló: {str(e3)}")

# Detectar entorno de ejecución
def is_streamlit_cloud():
    """
    Detecta si la aplicación se está ejecutando en Streamlit Cloud
    con verificación multi-indicador
    """
    try:
        # Múltiples indicadores para una detección más robusta
        indicators = [
            os.environ.get("STREAMLIT_SHARING_MODE") is not None,
            os.environ.get("STREAMLIT_SERVER_BASE_URL_IS_SET") is not None,
            os.environ.get("IS_STREAMLIT_CLOUD") == "true",
            os.path.exists("/.streamlit/config.toml"),
            "STREAMLIT_RUNTIME" in os.environ
        ]
        
        # Si al menos dos indicadores son positivos, consideramos que es Cloud
        return sum(indicators) >= 2
    except Exception as e:
        logging.warning(f"Error al detectar entorno: {str(e)}")
        return False

# Crear cliente OpenAI para Assistants
@handle_error(max_retries=1)
def create_openai_client(api_key):
    """
    Crea un cliente OpenAI con encabezados compatibles con Assistants API v2
    y verificación de conectividad
    """
    try:
        client = OpenAI(api_key=api_key, default_headers={"OpenAI-Beta": "assistants=v2"})
        
        # Verificar conectividad con una llamada simple
        models = client.models.list()
        if not models:
            raise Exception("No se pudo obtener la lista de modelos")
            
        logging.info("Cliente OpenAI inicializado correctamente")
        return client
    except Exception as e:
        logging.error(f"Error inicializando cliente OpenAI: {str(e)}")
        st.error(f"No se pudo conectar a OpenAI: {str(e)}")
        return None

# Sistema multicapa para exportación de conversaciones
def export_chat_to_pdf(messages):
    """
    Sistema multicapa para exportación de conversaciones a PDF.
    Implementa múltiples estrategias de generación con manejo de fallos.
    """
    try:
        # Método 1 (preferido): FPDF con manejo mejorado
        return _export_chat_to_pdf_primary(messages)
    except Exception as e:
        logging.warning(f"Método primario de exportación a PDF falló: {str(e)}")
        try:
            # Método 2: ReportLab como alternativa
            return _export_chat_to_pdf_secondary(messages)
        except Exception as e2:
            logging.warning(f"Método secundario de exportación a PDF falló: {str(e2)}")
            try:
                # Método 3: Conversión simple como último recurso
                return _export_chat_to_pdf_fallback(messages)
            except Exception as e3:
                logging.error(f"Todos los métodos de exportación a PDF fallaron: {str(e3)}")
                # Último recurso: Devolver contenido en markdown codificado
                md_content = export_chat_to_markdown(messages)
                st.warning("No fue posible generar un PDF. Se ha creado un archivo markdown en su lugar.")
                return base64.b64encode(md_content.encode()).decode(), "markdown"

def _export_chat_to_pdf_primary(messages):
    """
    Método primario: FPDF optimizado con manejo de errores mejorado
    y división inteligente de texto para evitar problemas de espacio
    """
    from fpdf import FPDF
    import re
    
    class CustomPDF(FPDF):
        def header(self):
            self.set_font('helvetica', 'B', 12)
            self.cell(0, 10, 'ConsentLex - Historial de Conversación', 0, new_y="NEXT", align='C')
            self.ln(5)
            
        def footer(self):
            self.set_y(-15)
            self.set_font('helvetica', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
            
        def add_message(self, role, content):
            # Añadir título del mensaje
            self.set_font('helvetica', 'B', 11)
            self.cell(0, 10, role, 0, new_y="NEXT", align='L')
            self.ln(2)
            
            # Añadir contenido con procesamiento seguro
            self.set_font('helvetica', '', 10)
            self._safe_add_content(content)
            self.ln(5)
            
        def _safe_add_content(self, content):
            # Procesar markdown básico
            content = self._process_markdown(content)
            
            # Dividir en párrafos
            paragraphs = content.split('\n\n')
            
            for paragraph in paragraphs:
                if not paragraph.strip():
                    self.ln(5)
                    continue
                
                # Dividir párrafos largos en líneas seguras
                lines = self._safe_wrap_text(paragraph, max_width=180)
                
                for line in lines:
                    if not line.strip():
                        continue
                        
                    if line.startswith('- ') or line.startswith('* '):
                        # Elemento de lista
                        self.cell(5, 10, '', 0, 0)
                        self.cell(5, 10, '•', 0, 0)
                        self._safe_multi_cell(0, 10, line[2:])
                    else:
                        # Párrafo normal
                        self._safe_multi_cell(0, 10, line)
                        
                # Espacio entre párrafos
                self.ln(2)
                
        def _process_markdown(self, text):
            # Simplificar encabezados
            text = re.sub(r'^#{1,6}\s+(.*?)$', r'\1', text, flags=re.MULTILINE)
            
            # Eliminar elementos multimedia
            text = re.sub(r'!\[.*?\]\(.*?\)', '[IMAGEN]', text)
            
            # Simplificar enlaces
            text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
            
            return text
            
        def _safe_wrap_text(self, text, max_width=180):
            """Divide texto en líneas seguras para renderizar"""
            lines = []
            for raw_line in text.split('\n'):
                if len(raw_line) < max_width:
                    lines.append(raw_line)
                    continue
                    
                # Dividir líneas largas en palabras
                words = raw_line.split(' ')
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    
                    if len(test_line) <= max_width:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word
                        
                if current_line:
                    lines.append(current_line)
                    
            return lines
            
        def _safe_multi_cell(self, w, h, txt, border=0, align='J', fill=False):
            """Versión segura de multi_cell con manejo de errores integrado"""
            try:
                # Eliminar caracteres no ASCII si es necesario
                if not all(ord(c) < 128 for c in txt):
                    txt = ''.join(c if ord(c) < 128 else '?' for c in txt)
                    
                # Limitar longitud de línea si es necesario
                if len(txt) > 200:
                    chunks = [txt[i:i+200] for i in range(0, len(txt), 200)]
                    for chunk in chunks:
                        self.multi_cell(w, h, chunk, border, align, fill)
                else:
                    self.multi_cell(w, h, txt, border, align, fill)
            except Exception as e:
                logging.warning(f"Error en multi_cell: {str(e)}. Intentando versión simplificada.")
                # Versión de respaldo extremadamente simplificada
                safe_txt = ''.join(c for c in txt if c.isalnum() or c in ' .,;:-?!()')
                self.multi_cell(w, h, safe_txt[:100] + "...", border, align, fill)
    
    # Crear el PDF
    pdf = CustomPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Añadir fecha
    pdf.set_font("helvetica", 'I', 10)
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, new_y="NEXT")
    pdf.ln(5)
    
    # Añadir mensajes
    for msg in messages:
        role = "Usuario" if msg["role"] == "user" else "ConsentLex"
        pdf.add_message(role, msg['content'])
    
    # Generar PDF
    output = io.BytesIO()
    pdf.output(output)
    return output.getvalue(), "pdf"

def _export_chat_to_pdf_secondary(messages):
    """
    Método secundario: ReportLab para generación alternativa de PDF
    con manejo mejorado de texto extenso
    """
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    
    # Crear buffer y documento
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=72)
    
    # Configurar estilos
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Title', 
                             fontName='Helvetica-Bold',
                             fontSize=14,
                             alignment=1,
                             spaceAfter=12))
    styles.add(ParagraphStyle(name='User', 
                             fontName='Helvetica-Bold',
                             fontSize=12,
                             textColor=colors.blue,
                             spaceAfter=6))
    styles.add(ParagraphStyle(name='Assistant', 
                             fontName='Helvetica-Bold',
                             fontSize=12,
                             textColor=colors.green,
                             spaceAfter=6))
    
    # Elementos del documento
    elements = []
    
    # Título y fecha
    elements.append(Paragraph("ConsentLex - Historial de Conversación", styles['Title']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Italic"]))
    elements.append(Spacer(1, 0.25*inch))
    
    # Función de seguridad para procesar texto
    def safe_process_text(text, max_chunk=2000):
        # Escapar caracteres especiales HTML
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Convertir newlines a <br/>
        text = text.replace('\n', '<br/>')
        
        # Dividir texto muy largo en secciones manejables
        if len(text) > max_chunk:
            chunks = []
            for i in range(0, len(text), max_chunk):
                chunks.append(text[i:i+max_chunk])
            return chunks
        return [text]
    
    # Procesar mensajes
    for msg in messages:
        role = "Usuario" if msg["role"] == "user" else "ConsentLex"
        style = styles["User"] if msg["role"] == "user" else styles["Assistant"]
        
        # Título del mensaje
        elements.append(Paragraph(role, style))
        
        # Contenido procesado en porciones seguras
        content_chunks = safe_process_text(msg['content'])
        for i, chunk in enumerate(content_chunks):
            try:
                elements.append(Paragraph(chunk, styles["Normal"]))
                if i < len(content_chunks) - 1:
                    elements.append(Spacer(1, 0.1*inch))
            except Exception as e:
                logging.warning(f"Error al procesar chunk {i}: {str(e)}")
                # Versión ultra simplificada como respaldo
                elements.append(Paragraph("[Contenido simplificado debido a error de formato]", styles["Normal"]))
        
        elements.append(Spacer(1, 0.2*inch))
    
    # Generar documento con manejo de errores
    try:
        doc.build(elements)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data, "pdf"
    except Exception as e:
        logging.error(f"Error en ReportLab: {str(e)}")
        raise e

def _export_chat_to_pdf_fallback(messages):
    """
    Método de último recurso: PDF simple sin formato avanzado
    diseñado para máxima compatibilidad y robustez
    """
    from fpdf import FPDF
    
    # PDF básico con manejo mínimo
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    
    # Título
    pdf.set_font("helvetica", style='B', size=16)
    pdf.cell(200, 10, "ConsentLex - Historial de Conversación", ln=True, align='C')
    pdf.ln(5)
    
    # Fecha
    pdf.set_font("helvetica", style='I', size=10)
    pdf.cell(200, 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)
    
    # Mensajes - formato mínimo con máxima seguridad
    pdf.set_font("helvetica", size=11)
    for msg in messages:
        role = "Usuario" if msg["role"] == "user" else "ConsentLex"
        
        # Encabezado del mensaje
        pdf.set_font("helvetica", style='B', size=12)
        pdf.cell(200, 10, role, ln=True)
        pdf.ln(2)
        
        # Contenido ultra-simple, sin formato
        pdf.set_font("helvetica", size=10)
        
        # Extraer texto plano con máxima seguridad
        simple_text = ''.join(c if ord(c) < 128 else '?' for c in msg['content'])
        simple_text = simple_text.replace('\n', ' ').replace('\r', '')
        
        # Dividir texto en líneas muy cortas para evitar errores
        line_length = 50  # Longitud muy conservadora
        for i in range(0, len(simple_text), line_length):
            chunk = simple_text[i:i+line_length]
            try:
                pdf.cell(0, 10, chunk, ln=True)
            except:
                # Si falla incluso con texto simplificado, usar solo alfanuméricos
                ultra_safe = ''.join(c for c in chunk if c.isalnum() or c == ' ')
                try:
                    pdf.cell(0, 10, ultra_safe, ln=True)
                except:
                    # Abandonar este chunk si todo falla
                    pass
        
        pdf.ln(10)
    
    # Generar PDF
    try:
        output = io.BytesIO()
        pdf.output(output)
        return output.getvalue(), "pdf"
    except Exception as e:
        logging.error(f"Error incluso en fallback: {str(e)}")
        raise e

def export_chat_to_markdown(messages):
    """
    Exporta el historial de chat a formato markdown
    con mejoras de formato y legibilidad
    """
    md_content = "# ConsentLex - Historial de Conversación\n\n"
    md_content += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for msg in messages:
        role = "Usuario" if msg["role"] == "user" else "ConsentLex"
        md_content += f"## {role}\n\n{msg['content']}\n\n"
        md_content += "---\n\n"  # Separador para mejorar legibilidad
    
    return md_content

# Funciones de OCR con Mistral
@handle_error(max_retries=1)
def detect_document_type(file):
    """
    Detecta automáticamente si un archivo es un PDF o una imagen
    con múltiples verificaciones para mayor precisión
    
    Parámetros:
        file: Objeto de archivo cargado por el usuario mediante Streamlit
        
    Retorno:
        string: Tipo de documento detectado ("PDF" o "Imagen")
    """
    # 1. Verificar por MIME type
    if hasattr(file, "type"):
        mime_type = file.type
        if mime_type.startswith("application/pdf"):
            return "PDF"
        elif mime_type.startswith("image/"):
            return "Imagen"

    # 2. Verificar por extensión del nombre
    if hasattr(file, "name"):
        name = file.name.lower()
        if name.endswith(".pdf"):
            return "PDF"
        elif name.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp")):
            return "Imagen"

    # 3. Verificar contenido con análisis de bytes
    try:
        # Guardar posición del cursor
        position = file.tell()
        # Leer los primeros bytes
        header = file.read(8)
        file.seek(position)  # Restaurar posición
        
        # Verificar firmas de archivo comunes
        if header.startswith(b'%PDF'):
            return "PDF"
        elif header.startswith(b'\x89PNG') or header.startswith(b'\xff\xd8'):
            return "Imagen"
    except:
        pass
        
    # 4. Intentar abrir como imagen (último recurso)
    try:
        Image.open(file)
        file.seek(0)  # Restaurar el puntero
        return "Imagen"
    except:
        file.seek(0)  # Restaurar el puntero
        
    # Asumir PDF por defecto
    return "PDF"

@handle_error(max_retries=1)
def prepare_image_for_ocr(file_data):
    """
    Prepara una imagen para ser procesada con OCR,
    optimizando formato y calidad para mejorar resultados
    
    Parámetros:
        file_data: Datos binarios de la imagen
        
    Retorno:
        tuple: (datos_optimizados, mime_type)
    """
    try:
        # Abrir la imagen con PIL
        img = Image.open(BytesIO(file_data))

        # Optimizaciones avanzadas para OCR
        # 1. Convertir a escala de grises si tiene más de un canal
        if img.mode != 'L' and img.mode != '1':
            img = img.convert('L')
            
        # 2. Ajustar tamaño si es muy grande (límite 4000px)
        max_dimension = 4000
        if img.width > max_dimension or img.height > max_dimension:
            ratio = min(max_dimension / img.width, max_dimension / img.height)
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            
        # 3. Evaluar y determinar mejor formato
        # JPEG para imágenes fotográficas, PNG para documentos/texto
        save_format = "JPEG"
        save_quality = 95
        
        # Detectar si es más probable que sea un documento (blanco/negro predominante)
        histogram = img.histogram()
        if img.mode == 'L' and (histogram[0] + histogram[-1]) > sum(histogram) * 0.8:
            save_format = "PNG"
            
        # 4. Guardar con parámetros optimizados
        buffer = BytesIO()
        if save_format == "JPEG":
            img.save(buffer, format=save_format, quality=save_quality, optimize=True)
        else:
            img.save(buffer, format=save_format, optimize=True)

        buffer.seek(0)
        return buffer.read(), f"image/{save_format.lower()}"

    except Exception as e:
        logging.warning(f"Optimización de imagen fallida: {str(e)}")
        return file_data, "image/jpeg"  # Formato por defecto

@handle_error(max_retries=1)
def extract_text_from_ocr_response(response):
    """
    Extrae texto de diferentes formatos de respuesta OCR
    con soporte para múltiples estructuras de datos
    
    Parámetros:
        response: Respuesta JSON del servicio OCR
        
    Retorno:
        dict: Diccionario con el texto extraído
    """
    # Registro para diagnóstico
    logging.info(f"Procesando respuesta OCR de tipo: {type(response)}")
    
    # Caso 1: Si hay páginas con markdown (formato preferido)
    if "pages" in response and isinstance(response["pages"], list):
        pages = response["pages"]
        if pages and "markdown" in pages[0]:
            markdown_text = "\n\n".join(page.get("markdown", "") for page in pages)
            if markdown_text.strip():
                return {"text": markdown_text, "format": "markdown"}

    # Caso 2: Si hay un texto plano en la respuesta
    if "text" in response:
        return {"text": response["text"], "format": "text"}

    # Caso 3: Si hay elementos estructurados
    if "elements" in response:
        elements = response["elements"]
        if isinstance(elements, list):
            text_parts = []
            for element in elements:
                if "text" in element:
                    text_parts.append(element["text"])
            return {"text": "\n".join(text_parts), "format": "elements"}

    # Caso 4: Si hay un campo 'content' principal
    if "content" in response:
        return {"text": response["content"], "format": "content"}

    # Caso 5: Extracción recursiva de todos los campos de texto
    try:
        response_str = json.dumps(response, indent=2)
        # Si la respuesta es muy grande, limitar extracción
        if len(response_str) > 10000:
            response_str = response_str[:10000] + "... [truncado]"
            
        extracted_text = extract_all_text_fields(response)
        if extracted_text:
            return {"text": extracted_text, "format": "extracted"}

        return {
            "text": "No se pudo encontrar texto estructurado en la respuesta OCR. Vea los detalles técnicos.",
            "format": "unknown",
            "raw_response": response_str,
        }
    except Exception as e:
        logging.error(f"Error al procesar respuesta OCR: {str(e)}")
        return {"error": f"Error al procesar la respuesta: {str(e)}"}

@handle_error(max_retries=0)
def extract_all_text_fields(data, prefix="", max_depth=5, current_depth=0):
    """
    Función recursiva optimizada para extraer todos los campos de texto 
    de un diccionario anidado con límites de profundidad
    
    Parámetros:
        data: Diccionario o lista de datos
        prefix: Prefijo para la ruta de acceso (uso recursivo)
        max_depth: Profundidad máxima de recursión
        current_depth: Profundidad actual (uso recursivo)
        
    Retorno:
        string: Texto extraído
    """
    # Evitar recursión infinita
    if current_depth > max_depth:
        return []
    
    result = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key

            if isinstance(value, str) and len(value) > 1:
                result.append(f"{new_prefix}: {value}")
            elif isinstance(value, (dict, list)) and value:  # Solo recursión si hay contenido
                child_results = extract_all_text_fields(
                    value, new_prefix, max_depth, current_depth + 1
                )
                result.extend(child_results)

    elif isinstance(data, list):
        # Limitar número de elementos procesados en listas muy grandes
        max_items = 20
        for i, item in enumerate(data[:max_items]):
            new_prefix = f"{prefix}[{i}]"
            if isinstance(item, (dict, list)) and item:
                child_results = extract_all_text_fields(
                    item, new_prefix, max_depth, current_depth + 1
                )
                result.extend(child_results)
            elif isinstance(item, str) and len(item) > 1:
                result.append(f"{new_prefix}: {item}")
        
        # Indicar si se truncó la lista
        if len(data) > max_items:
            result.append(f"{prefix}: [... {len(data) - max_items} elementos adicionales omitidos]")

    return "\n".join(result)

@handle_error(max_retries=1)
def process_document_with_mistral_ocr(api_key, file_bytes, file_type, file_name):
    """
    Procesa un documento con OCR de Mistral
    con sistema de recuperación ante fallos
    
    Parámetros:
        api_key: API key de Mistral
        file_bytes: Bytes del archivo
        file_type: Tipo de archivo ("PDF" o "Imagen")
        file_name: Nombre del archivo
        
    Retorno:
        dict: Texto extraído del documento
    """
    job_id = str(uuid.uuid4())
    logging.info(f"Procesando documento {file_name} con Mistral OCR (ID: {job_id})")
    
    # Mostrar estado
    with st.status(f"Procesando documento {file_name}...", expanded=True) as status:
        try:
            status.update(label="Preparando documento para OCR...", state="running")
            
            # Guardar una copia del archivo para depuración
            debug_dir = os.path.join(tempfile.gettempdir(), "consentlex_debug")
            os.makedirs(debug_dir, exist_ok=True)
            debug_file_path = os.path.join(debug_dir, f"debug_{job_id}_{file_name}")
            
            with open(debug_file_path, "wb") as f:
                f.write(file_bytes)
            
            logging.info(f"Archivo de depuración guardado en: {debug_file_path}")
            
            # Sistema de procesamiento con verificación según tipo
            if file_type == "PDF":
                # Verificar que el PDF sea válido
                try:
                    import PyPDF2
                    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                    page_count = len(reader.pages)
                    sample_text = ""
                    if page_count > 0:
                        sample_text = reader.pages[0].extract_text()[:100]
                    logging.info(f"PDF válido con {page_count} páginas. Muestra: {sample_text}")
                    
                    # Codificar PDF en base64
                    encoded_file = base64.b64encode(file_bytes).decode("utf-8")
                    document = {
                        "type": "document_url",
                        "document_url": f"data:application/pdf;base64,{encoded_file}"
                    }
                except Exception as e:
                    logging.error(f"Error al validar PDF: {str(e)}")
                    status.update(label=f"Error al validar PDF: {str(e)}", state="error")
                    
                    # Intentar procesar como imagen si el PDF falló
                    logging.info("Intentando procesar como imagen alternativa...")
                    try:
                        optimized_bytes, mime_type = prepare_image_for_ocr(file_bytes)
                        encoded_file = base64.b64encode(optimized_bytes).decode("utf-8")
                        document = {
                            "type": "image_url",
                            "image_url": f"data:{mime_type};base64,{encoded_file}"
                        }
                    except Exception as e2:
                        return {"error": f"El archivo no es un PDF válido ni una imagen: {str(e2)}"}
            else:  # Imagen
                # Optimizar imagen para mejores resultados
                optimized_bytes, mime_type = prepare_image_for_ocr(file_bytes)
                
                # Codificar en base64
                encoded_file = base64.b64encode(optimized_bytes).decode("utf-8")
                document = {
                    "type": "image_url",
                    "image_url": f"data:{mime_type};base64,{encoded_file}"
                }
            
            status.update(label="Enviando documento a la API de Mistral...", state="running")
            
            # Configurar los headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            
            # Preparar payload
            payload = {
                "model": "mistral-ocr-latest",
                "document": document
            }
            
            # Guardar payload para depuración (excluyendo contenido base64 por tamaño)
            debug_payload = {
                "model": payload["model"],
                "document": {
                    "type": payload["document"]["type"],
                    "content_size": len(encoded_file),
                    "content_format": "base64"
                }
            }
            logging.info(f"Payload para OCR: {json.dumps(debug_payload)}")
            
            # Sistema de retry interno para la API de Mistral
            max_retries = 2
            retry_delay = 2
            last_error = None
            
            for retry in range(max_retries + 1):
                try:
                    # Hacer la solicitud a Mistral OCR API
                    response = requests.post(
                        "https://api.mistral.ai/v1/ocr",
                        json=payload,
                        headers=headers,
                        timeout=90  # Timeout ampliado para documentos grandes
                    )
                    
                    logging.info(f"Respuesta de OCR API - Estado: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            # Guardar respuesta para depuración
                            with open(os.path.join(debug_dir, f"response_{job_id}_{file_name}.json"), "w") as f:
                                json.dump(result, f, indent=2)
                                
                            status.update(label=f"Documento {file_name} procesado exitosamente", state="complete")
                            
                            # Verificar existencia de contenido
                            if not result or (isinstance(result, dict) and not result):
                                return {"error": "La API no devolvió contenido", "raw_response": str(result)}
                            
                            # Extraer texto de la respuesta
                            extracted_content = extract_text_from_ocr_response(result)
                            
                            if "error" in extracted_content:
                                status.update(label=f"Error al extraer texto: {extracted_content['error']}", state="error")
                                return {"error": extracted_content['error'], "raw_response": result}
                            
                            return extracted_content
                        except Exception as e:
                            error_message = f"Error al procesar respuesta JSON: {str(e)}"
                            logging.error(error_message)
                            # Guardar respuesta cruda para depuración
                            with open(os.path.join(debug_dir, f"raw_response_{job_id}_{file_name}.txt"), "w") as f:
                                f.write(response.text[:10000])  # Limitar tamaño
                            status.update(label=error_message, state="error")
                            last_error = e
                    elif response.status_code == 429:  # Rate limit
                        if retry < max_retries:
                            wait_time = retry_delay * (retry + 1)
                            logging.warning(f"Rate limit alcanzado. Esperando {wait_time}s antes de reintentar...")
                            status.update(label=f"Límite de tasa alcanzado. Reintentando en {wait_time}s...", state="running")
                            time.sleep(wait_time)
                            continue
                        else:
                            error_message = "Límite de tasa alcanzado. No se pudo procesar después de reintentos."
                            logging.error(error_message)
                            status.update(label=error_message, state="error")
                            return {"error": error_message, "raw_response": response.text}
                    else:
                        error_message = f"Error en API OCR ({response.status_code}): {response.text[:500]}"
                        logging.error(error_message)
                        status.update(label=f"Error: {error_message}", state="error")
                        last_error = Exception(error_message)
                        break
                except requests.exceptions.Timeout:
                    if retry < max_retries:
                        wait_time = retry_delay * (retry + 1)
                        logging.warning(f"Timeout al contactar API. Esperando {wait_time}s antes de reintentar...")
                        status.update(label=f"Timeout. Reintentando en {wait_time}s...", state="running")
                        time.sleep(wait_time)
                    else:
                        error_message = "Timeout al contactar API después de múltiples intentos."
                        logging.error(error_message)
                        status.update(label=error_message, state="error")
                        return {"error": error_message}
                except Exception as e:
                    if retry < max_retries:
                        wait_time = retry_delay * (retry + 1)
                        logging.warning(f"Error: {str(e)}. Esperando {wait_time}s antes de reintentar...")
                        status.update(label=f"Error. Reintentando en {wait_time}s...", state="running")
                        time.sleep(wait_time)
                    else:
                        error_message = f"Error al procesar documento: {str(e)}"
                        logging.error(error_message)
                        status.update(label=f"Error: {error_message}", state="error")
                        last_error = e
                        break
            
            # Si llegamos aquí después de reintentos, devolver último error
            return {"error": f"Error después de reintentos: {str(last_error)}", "details": traceback.format_exc()}
                
        except Exception as e:
            error_message = f"Error general al procesar documento: {str(e)}"
            logging.error(error_message)
            logging.error(traceback.format_exc())
            status.update(label=f"Error: {error_message}", state="error")
            return {"error": error_message}

# Función segura para gestionar el contexto de documentos
@handle_error(max_retries=0)
def manage_document_context():
    """
    Permite al usuario gestionar qué documentos mantener en el contexto actual
    con manejo seguro de actualización de estado
    """
    if "document_contents" in st.session_state and st.session_state.document_contents:
        st.write("Documentos en contexto actual:")
        
        # Crear checkboxes para cada documento
        docs_to_keep = {}
        for doc_name in st.session_state.document_contents:
            docs_to_keep[doc_name] = st.checkbox(f"{doc_name}", value=True, key=f"keep_{doc_name}")
        
        # Botón para aplicar cambios
        if st.button("Actualizar contexto", key="update_context"):
            # Eliminar documentos no seleccionados
            docs_to_remove = [doc for doc, keep in docs_to_keep.items() if not keep]
            if docs_to_remove:
                for doc in docs_to_remove:
                    if doc in st.session_state.document_contents:
                        del st.session_state.document_contents[doc]
                    if doc in st.session_state.uploaded_files:
                        st.session_state.uploaded_files.remove(doc)
                
                st.success(f"Se eliminaron {len(docs_to_remove)} documentos del contexto.")
                # Usar sistema seguro de reinicio
                rerun_app()
            else:
                st.info("No se seleccionaron documentos para eliminar.")
    else:
        st.info("No hay documentos cargados en el contexto actual.")

# Función para inicializar un thread con OpenAI Assistants
@handle_error(max_retries=1)
def initialize_thread(client):
    """
    Inicializa un nuevo thread de conversación
    con verificación de éxito
    """
    try:
        thread = client.beta.threads.create()
        thread_id = thread.id
        logging.info(f"Thread creado: {thread_id}")
        
        # Verificar que el thread se creó correctamente
        test_thread = client.beta.threads.retrieve(thread_id=thread_id)
        if not test_thread or not hasattr(test_thread, "id"):
            raise Exception("El thread se creó pero no se puede recuperar")
            
        return thread_id
    except Exception as e:
        logging.error(f"Error creando thread: {str(e)}")
        st.error("No se pudo inicializar la conversación con el asistente")
        return None

# Función para procesar mensajes del asistente
@handle_error(max_retries=1)
def process_message_with_citations(message):
    """
    Extrae y formatea el texto del mensaje del asistente con citas adecuadas,
    manejando diferentes formatos de respuesta
    """
    try:
        # Verificar que el mensaje tenga contenido
        if not hasattr(message, "content") or not message.content:
            return "No se pudo procesar el mensaje"
        
        # Procesar cada parte del contenido
        processed_content = ""
        for content_item in message.content:
            # Verificar tipo de contenido
            if hasattr(content_item, "text") and content_item.text:
                # Procesar texto con anotaciones si existen
                text_value = content_item.text.value
                annotations = []
                
                # Extraer anotaciones si existen
                if hasattr(content_item.text, "annotations") and content_item.text.annotations:
                    annotations = content_item.text.annotations
                    
                    # Procesar cada anotación para formatear citas de archivos
                    if annotations:
                        # Recolectar información de citas
                        citations = []
                        for idx, annotation in enumerate(annotations):
                            # Reemplazar el texto de la anotación con un marcador de referencia
                            text_value = text_value.replace(
                                annotation.text, 
                                f"[{idx+1}]"
                            )
                            
                            # Extraer detalles de la cita si es una cita de archivo
                            if file_citation := getattr(annotation, "file_citation", None):
                                file_id = file_citation.file_id
                                # Buscar el nombre del archivo en los metadatos
                                file_name = "Documento de referencia"
                                if "file_metadata" in st.session_state and file_id in st.session_state.file_metadata:
                                    file_name = st.session_state.file_metadata[file_id]["name"]
                                
                                citations.append(f"[{idx+1}] Fuente: {file_name}")
                        
                        # Añadir las citas al final del texto procesado si existen
                        if citations:
                            text_value += "\n\n--- Referencias: ---\n" + "\n".join(citations)
                
                processed_content += text_value
            else:
                # Si no es texto, añadimos una representación genérica
                processed_content += str(content_item)
                
        return processed_content
    except Exception as e:
        logging.error(f"Error procesando mensaje: {str(e)}")
        logging.error(traceback.format_exc())
        return "Error al procesar la respuesta del asistente"

# Función para enviar mensaje a OpenAI con contexto de documentos
@handle_error(max_retries=1)
def send_message_with_document_context(client, thread_id, assistant_id, prompt, current_doc_contents=None):
    """
    Envía un mensaje al asistente incluyendo el contexto de todos los documentos disponibles
    con manejo mejorado de errores y reintentos
    """
    try:
        # Construir el mensaje que incluirá el contexto del documento si existe
        full_prompt = prompt
        
        # Combinar documentos actuales con documentos previamente procesados
        all_doc_contents = {}
        
        # Añadir documentos existentes en la sesión
        if "document_contents" in st.session_state:
            all_doc_contents.update(st.session_state.document_contents)
        
        # Añadir documentos recién procesados, que pueden sobrescribir los anteriores
        if current_doc_contents and isinstance(current_doc_contents, dict):
            all_doc_contents.update(current_doc_contents)
            # Actualizar la sesión con los nuevos documentos
            if "document_contents" not in st.session_state:
                st.session_state.document_contents = {}
            st.session_state.document_contents.update(current_doc_contents)
        
        # Si hay contenido de documentos, añadirlo al prompt
        if all_doc_contents and len(all_doc_contents) > 0:
            document_context = "\n\n### Contexto de documentos procesados:\n\n"
            
            for doc_name, doc_content in all_doc_contents.items():
                # Extraer el texto del documento procesado por OCR
                if isinstance(doc_content, dict):
                    if "text" in doc_content:
                        # Limitamos el contenido para no exceder el contexto de OpenAI
                        doc_text = doc_content["text"][:5000] + "..." if len(doc_content["text"]) > 5000 else doc_content["text"]
                        document_context += f"-- Documento: {doc_name} --\n{doc_text}\n\n"
                    elif "error" in doc_content and "raw_response" in doc_content:
                        # Intentar extraer texto de la respuesta cruda si está disponible
                        raw_response = doc_content["raw_response"]
                        if isinstance(raw_response, dict) and "text" in raw_response:
                            doc_text = raw_response["text"][:5000] + "..." if len(raw_response["text"]) > 5000 else raw_response["text"]
                            document_context += f"-- Documento: {doc_name} --\n{doc_text}\n\n"
                        else:
                            document_context += f"-- Documento: {doc_name} -- (Error al extraer texto: {doc_content['error']})\n\n"
                    else:
                        document_context += f"-- Documento: {doc_name} -- (No se pudo extraer texto)\n\n"
                else:
                    document_context += f"-- Documento: {doc_name} -- (Formato no reconocido)\n\n"
            
            # Verificar si hay contenido real antes de añadirlo al prompt
            if len(document_context) > 60:  # Más que solo el encabezado
                full_prompt = f"{prompt}\n\n{document_context}"
                logging.info(f"Prompt enriquecido con contexto de {len(all_doc_contents)} documentos. Tamaño total: {len(full_prompt)} caracteres")
            else:
                logging.warning("No se pudo extraer texto útil de los documentos")
        
        # Crear mensaje con el prompt completo (con sistema de retry)
        message = None
        for attempt in range(2):
            try:
                message = client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=full_prompt
                )
                break
            except Exception as e:
                if attempt == 0:
                    logging.warning(f"Error al crear mensaje (intento 1): {str(e)}. Reintentando...")
                    time.sleep(2)
                else:
                    raise Exception(f"Error al crear mensaje: {str(e)}")
        
        if not message:
            raise Exception("No se pudo crear el mensaje después de reintentos")
        
        # Crear la ejecución
        run = None
        for attempt in range(2):
            try:
                run = client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=assistant_id
                )
                break
            except Exception as e:
                if attempt == 0:
                    logging.warning(f"Error al crear ejecución (intento 1): {str(e)}. Reintentando...")
                    time.sleep(2)
                else:
                    raise Exception(f"Error al crear ejecución: {str(e)}")
        
        if not run:
            raise Exception("No se pudo iniciar la ejecución después de reintentos")
        
        # Esperar a que se complete la ejecución
        with st.status("Analizando consulta y procesando información...", expanded=True) as status:
            run_counter = 0
            max_run_time = 120  # Tiempo máximo de espera (2 minutos)
            start_time = time.time()
            
            while run.status not in ["completed", "failed", "cancelled", "expired"]:
                run_counter += 1
                time.sleep(1)
                
                # Verificar timeout
                elapsed_time = time.time() - start_time
                if elapsed_time > max_run_time:
                    status.update(label="La operación está tomando demasiado tiempo. Intente nuevamente.", state="error")
                    logging.error(f"Timeout después de {max_run_time}s esperando completar ejecución.")
                    return None
                
                # Actualizar el estado cada 2 segundos para no sobrecargar la API
                if run_counter % 2 == 0:
                    try:
                        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
                    except Exception as e:
                        logging.warning(f"Error al recuperar estado de ejecución: {str(e)}")
                        # Continuar intentando, podría ser un error temporal
                
                # Mostrar mensajes según el estado
                if run.status == "in_progress":
                    status.update(label="Procesando consulta y analizando documentos...", state="running")
                elif run.status == "requires_action":
                    status.update(label="Realizando acciones requeridas...", state="running")
                
                # Manejar errores
                if run.status == "failed":
                    error_msg = f"Error en la ejecución: {getattr(run, 'last_error', 'Desconocido')}"
                    logging.error(error_msg)
                    status.update(label="Error en el procesamiento", state="error")
                    return None
            
            # Actualizar estado final
            if run.status == "completed":
                status.update(label="Análisis completado", state="complete")
            else:
                status.update(label=f"Estado final: {run.status}", state="error")
        
        # Recuperar mensajes agregados por el asistente
        if run.status == "completed":
            try:
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                
                # Buscar el mensaje más reciente del asistente
                for message in messages.data:
                    if message.role == "assistant" and not any(
                        msg["role"] == "assistant" and msg.get("id") == message.id
                        for msg in st.session_state.messages
                    ):
                        full_response = process_message_with_citations(message)
                        return {
                            "role": "assistant",
                            "content": full_response,
                            "id": message.id,
                        }
                
                # Si no se encontró un mensaje nuevo
                logging.warning("No se encontraron nuevos mensajes del asistente")
                return None
            except Exception as e:
                logging.error(f"Error al recuperar mensajes: {str(e)}")
                return None
        
        return None
    except Exception as e:
        logging.error(f"Error en comunicación con OpenAI: {str(e)}")
        logging.error(traceback.format_exc())
        st.error("Ocurrió un error al comunicarse con el asistente. Por favor, intente nuevamente.")
        return None

# Función para limpiar la sesión actual
@handle_error(max_retries=0)
def clean_current_session():
    """
    Limpia todos los recursos de la sesión actual
    con verificación de resultados
    """
    try:
        resources_cleaned = {
            "documents": 0,
            "messages": len(st.session_state.messages) if "messages" in st.session_state else 0
        }
        
        # Limpiar documentos procesados
        if "document_contents" in st.session_state:
            resources_cleaned["documents"] = len(st.session_state.document_contents)
            st.session_state.document_contents = {}
        
        # Limpiar lista de archivos
        if "uploaded_files" in st.session_state:
            st.session_state.uploaded_files = []
        
        # Limpiar historial de mensajes
        if "messages" in st.session_state:
            st.session_state.messages = []
        
        # Limpiar otros estados relacionados con documentos
        for key in ["file_metadata"]:
            if key in st.session_state:
                st.session_state[key] = {}
        
        # Verificar limpieza exitosa
        clean_success = True
        if "document_contents" in st.session_state and st.session_state.document_contents:
            clean_success = False
        if "messages" in st.session_state and st.session_state.messages:
            clean_success = False
            
        if clean_success:
            logging.info(f"Sesión limpiada exitosamente: {resources_cleaned['documents']} documentos, {resources_cleaned['messages']} mensajes")
        else:
            logging.warning("Limpieza de sesión incompleta - algunos elementos persistieron")
            
        return resources_cleaned
    except Exception as e:
        logging.error(f"Error limpiando sesión: {str(e)}")
        return {
            "documents": 0,
            "messages": 0,
            "error": str(e)
        }

# ----- INICIALIZACIÓN DE INTERFAZ -----

# Título principal
st.title("ConsentLex ⚖️ Experto en Consentimiento Informado")

# Barra lateral con toda la información e instrucciones
with st.sidebar:
    st.title("⚖️ Configuración y Recursos")

    # Obtener API Key de OpenAI
    openai_api_key = None
    # 1. Intentar obtener de variables de entorno
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    # 2. Intentar obtener de secrets.toml
    if not openai_api_key and hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
        openai_api_key = st.secrets["OPENAI_API_KEY"]

    # 3. Solicitar al usuario
    if not openai_api_key:
        openai_api_key = st.text_input("API Key de OpenAI", type="password", help="Ingrese su API Key de OpenAI")

    # Obtener API Key de Mistral 
    mistral_api_key = None
    # 1. Intentar obtener de variables de entorno
    mistral_api_key = os.environ.get("MISTRAL_API_KEY")

    # 2. Intentar obtener de secrets.toml
    if not mistral_api_key and hasattr(st, "secrets") and "MISTRAL_API_KEY" in st.secrets:
        mistral_api_key = st.secrets["MISTRAL_API_KEY"]

    # 3. Solicitar al usuario
    if not mistral_api_key:
        mistral_api_key = st.text_input("API Key de Mistral", type="password", help="Ingrese su API Key de Mistral para OCR")

    # Obtener Assistant ID
    assistant_id = None
    # 1. Intentar obtener de variables de entorno
    assistant_id = os.environ.get("ASSISTANT_ID")

    # 2. Intentar obtener de secrets.toml
    if not assistant_id and hasattr(st, "secrets") and "ASSISTANT_ID" in st.secrets:
        assistant_id = st.secrets["ASSISTANT_ID"]

    # 3. Solicitar al usuario
    if not assistant_id:
        assistant_id = st.text_input("ID del Asistente", type="password", help="Ingrese el ID del asistente de OpenAI")

    # Verificar configuración
    if openai_api_key and mistral_api_key and assistant_id:
        st.success("✅ Configuración completa")
    else:
        missing = []
        if not openai_api_key:
            missing.append("API Key de OpenAI")
        if not mistral_api_key:
            missing.append("API Key de Mistral")
        if not assistant_id:
            missing.append("ID del Asistente")
        st.warning(f"⚠️ Falta configurar: {', '.join(missing)}")

    # Mostrar entorno
    env_type = "Streamlit Cloud" if is_streamlit_cloud() else "Local"
    st.info(f"Entorno detectado: {env_type}")
    
    # Opciones de exportación de chat
    st.subheader("💾 Exportar Conversación")
    # export_format = st.radio("Formato de exportación:", ("Markdown", "PDF"))
    export_format = st.radio("Formato de exportación:", ("Markdown"))

    if st.button("Descargar conversación"):
        if "messages" in st.session_state and st.session_state.messages:
            if export_format == "Markdown":
                md_content = export_chat_to_markdown(st.session_state.messages)
                b64 = base64.b64encode(md_content.encode()).decode()
                href = f'<a href="data:text/markdown;base64,{b64}" download="consentlex_conversation.md">Descargar archivo Markdown</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:  # PDF
                try:
                    with st.spinner("Generando PDF..."):
                        try:
                            # Sistema de generación multicapa
                            content, content_type = export_chat_to_pdf(st.session_state.messages)
                            if content_type == "pdf":
                                b64 = base64.b64encode(content).decode()
                                href = f'<a href="data:application/pdf;base64,{b64}" download="consentlex_conversation.pdf">Descargar archivo PDF</a>'
                                st.markdown(href, unsafe_allow_html=True)
                            else:
                                # Si devuelve markdown, mostrar alternativa
                                b64 = content  # Ya viene en base64
                                href = f'<a href="data:text/markdown;base64,{b64}" download="consentlex_conversation.md">Descargar archivo Markdown</a>'
                                st.markdown(href, unsafe_allow_html=True)
                                st.warning("No se pudo generar el PDF. Se ha creado un archivo markdown en su lugar.")
                        except Exception as e:
                            st.error(f"Error durante la exportación: {str(e)}")
                            logging.error(f"Error detallado: {traceback.format_exc()}")
                except Exception as e:
                    st.error(f"Error al generar PDF: {str(e)}")
        else:
            st.warning("No hay conversación para exportar.")

    # Administrador de contexto de documentos
    st.subheader("📄 Gestión de Documentos")
    manage_document_context()

    # Botón para limpiar la sesión actual
    if st.button("🧹 Limpiar sesión actual", type="secondary", help="Elimina todos los archivos y datos de la sesión actual"):
        with st.spinner("Limpiando recursos de la sesión..."):
            result = clean_current_session()
            if isinstance(result, dict) and "error" not in result:
                st.success(f"Sesión limpiada: {result['documents']} documentos, {result['messages']} mensajes")
            else:
                st.error("No se pudo limpiar la sesión completamente")
            rerun_app()

    # Documentos cargados
    if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
        st.subheader("📚 Documentos disponibles")
        for idx, filename in enumerate(st.session_state.uploaded_files):
            st.markdown(f"📄 **{filename}**")
        
        st.info("Estos documentos están disponibles para consulta en la conversación.")
    
    # Área informativa - Trasladada desde el cuerpo principal
    st.markdown("---")
    st.subheader("⚖️ Sobre ConsentLex")
    st.markdown("""
    **ConsentLex** es un sistema experto para el análisis y creación de consentimientos informados médico-legales.
    
    Puede ayudarle con:
    
    * 📋 **Evaluación de consentimientos existentes**: Análisis de legalidad y conformidad normativa
    * 📝 **Creación de nuevos consentimientos**: Desarrollo de documentos personalizados según procedimiento
    * ⚕️ **Asesoría en casos específicos**: Consultas sobre situaciones médico-legales complejas
    * 📚 **Interpretación normativa**: Aclaración de requisitos legales vigentes
    * 🔍 **Identificación de riesgos**: Detección de posibles vulnerabilidades en documentos
    """)

    # Añadir información de uso
    st.markdown("---")
    st.subheader("💡 Cómo usar ConsentLex")
    st.markdown("""
    1. **Consultas generales**: Escriba su pregunta en el chat para recibir información sobre normativa y mejores prácticas.
    
    2. **Análisis de documentos**: Adjunte un documento de consentimiento informado (.pdf, .docx, .txt, imágenes) en el chat para que sea analizado.
    
    3. **Creación de documentos**: Solicite la creación de un nuevo consentimiento informado especificando el procedimiento médico, perfil de pacientes y contexto institucional.
    """)
    
    # Instrucciones para documentos
    st.markdown("---")
    st.subheader("📄 Procesamiento de documentos")
    st.info("""
    Esta aplicación utiliza la tecnología OCR de Mistral para:
    
    - Extraer texto y contenido estructurado de documentos PDF
    - Analizar automáticamente el contenido de documentos
    - Recuperar información relevante para responder consultas
    
    **Nota sobre privacidad**: Los documentos se procesan localmente y no se almacenan permanentemente.
    """)

    # Añadir créditos
    st.markdown("---")
    st.subheader("Desarrollado por:")
    st.markdown("Equipo Jurídico-Médico González Páez Abogados")
    st.markdown(
        "[Sitio web](https://gonzalezpaezabogados.co/) | [Documentación](#)"
    )
    
    # Footer en la barra lateral
    st.markdown("---")
    st.markdown(
        f"""
        <div style="color: #666666; font-size: 0.8rem;">
            <p>ConsentLex v{APP_VERSION} | {datetime.now().strftime('%Y-%m-%d')}</p>
            <p>Basado en la 'Guía Completa para el Control de Legalidad y Elaboración de Consentimientos Informados'.</p>
            <p>Las interacciones cumplen con las normas de confidencialidad médica.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Detener si no tenemos la configuración completa
if not openai_api_key or not mistral_api_key or not assistant_id:
    st.markdown(
        """
        ## ⚙️ Configuración necesaria
        
        Por favor, completa la configuración en la barra lateral para usar ConsentLex:
        
        1. **API Key de OpenAI**: Necesaria para conectar con el servicio
        2. **API Key de Mistral**: Necesaria para el procesamiento OCR de documentos
        3. **ID del Asistente**: Identifica el asistente de OpenAI a utilizar
        
        Una vez configurado, podrás interactuar con el sistema experto.
        """
    )
    st.stop()

# ----- INICIALIZACIÓN DE ESTADO -----

# Inicializar variables de estado
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "document_contents" not in st.session_state:
    st.session_state.document_contents = {}

if "file_metadata" not in st.session_state:
    st.session_state.file_metadata = {}

# Crear clientes
openai_client = create_openai_client(openai_api_key)

# Inicializar thread si no existe
if not st.session_state.thread_id and openai_client:
    with st.spinner("Inicializando sistema experto..."):
        thread_id = initialize_thread(openai_client)
        if thread_id:
            st.session_state.thread_id = thread_id
            st.success("⚖️ Sistema experto inicializado correctamente ⚖️")

# ----- INTERFAZ DE CHAT -----

# Contenedor de historial de chat - mostrar mensajes previos
chat_history_container = st.container()

with chat_history_container:
    # Mostrar mensajes previos
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Mostrar mensaje de bienvenida si no hay mensajes
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown("""
            ### ⚖️ Bienvenido a ConsentLex

            Soy su experto en consentimiento informado médico-legal. ¿En qué puedo ayudarle hoy?
            
            * Puede consultarme sobre normativa y requisitos legales
            * Enviarme un documento para análisis (PDF, DOCX, TXT, imágenes)
            * Solicitar ayuda para crear un nuevo consentimiento informado
            """)

# Chat input con soporte nativo para adjuntar archivos
prompt = st.chat_input(
    "Escriba su consulta sobre consentimientos informados...",
    accept_file=True,
    file_type=["pdf", "docx", "txt", "jpg", "jpeg", "png"]
)

# Procesar la entrada del usuario
if prompt:
    # Verificar si hay texto o archivos
    user_text = ""
    user_files = []
    
    if hasattr(prompt, "text"):
        user_text = prompt.text
    
    if hasattr(prompt, "files") and prompt.files:
        user_files = prompt.files
    elif isinstance(prompt, dict) and "files" in prompt and prompt["files"]:
        user_files = prompt["files"]
    
    # Documentos para compartir en el contexto
    current_doc_contents = {}
    
    # Si hay archivos adjuntos, procesarlos con OCR
    if user_files:
        with st.spinner("Procesando documentos con OCR..."):
            for file in user_files:
                if file.name not in st.session_state.uploaded_files:
                    st.session_state.uploaded_files.append(file.name)
                
                # Leer el contenido del archivo
                file_bytes = file.read()
                file.seek(0)  # Restaurar el puntero del archivo
                
                # Detectar tipo de documento
                file_type = detect_document_type(file)
                
                # Procesar con OCR de Mistral
                try:
                    ocr_results = process_document_with_mistral_ocr(
                        mistral_api_key, 
                        file_bytes, 
                        file_type, 
                        file.name
                    )
                    
                    if ocr_results and "error" not in ocr_results:
                        current_doc_contents[file.name] = ocr_results
                        # Guardar en la sesión para referencia futura
                        st.session_state.document_contents[file.name] = ocr_results
                        st.success(f"Documento {file.name} procesado correctamente")
                    else:
                        error_msg = ocr_results.get("error", "Error desconocido durante el procesamiento")
                        st.warning(f"No se pudo extraer texto completo de {file.name}: {error_msg}")
                        # Aún así, guardamos el resultado para potencial depuración y recuperación parcial
                        st.session_state.document_contents[file.name] = ocr_results
                except Exception as e:
                    st.error(f"Error procesando {file.name}: {str(e)}")
    
    # Generar un mensaje automático si solo hay archivos sin texto
    if not user_text and user_files:
        file_names = [f.name for f in user_files]
        user_text = f"He cargado el documento '{', '.join(file_names)}' para análisis. Por favor, analiza su contenido y estructura como consentimiento informado."
    
    # Si no hay ni texto ni archivos, no hacemos nada
    if not user_text and not user_files:
        st.warning("Por favor, ingrese un mensaje o adjunte un archivo para continuar.")
    else:
        # Construir el mensaje para mostrar
        display_message = user_text
        if user_files:
            file_names = [f.name for f in user_files]
            if user_text:
                display_message = f"{user_text}\n\n*Archivo adjunto: {', '.join(file_names)}*"
            else:
                display_message = f"*Archivo adjunto para análisis: {', '.join(file_names)}*"
        
        # Mostrar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": display_message})
        with st.chat_message("user"):
            st.markdown(display_message)
        
        # Procesar la respuesta usando el contenido de los documentos
        if st.session_state.thread_id and openai_client and assistant_id:
            try:
                # Determinar los documentos a incluir en el contexto 
                response = send_message_with_document_context(
                    openai_client, 
                    st.session_state.thread_id, 
                    assistant_id, 
                    user_text,
                    current_doc_contents=current_doc_contents
                )

                if response:
                    # Añadir respuesta al historial
                    st.session_state.messages.append(response)
                    with st.chat_message("assistant"):
                        st.markdown(response["content"])
                else:
                    st.error("No se pudo obtener respuesta. Por favor, intente de nuevo.")
            except Exception as e:
                st.error(f"Error al procesar la respuesta: {str(e)}")
                logging.error(f"Error procesando respuesta: {traceback.format_exc()}")
        else:
            st.error("Error: Sistema no inicializado correctamente.")
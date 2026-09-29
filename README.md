# WebGest 🌐📁

**WebGest** es un administrador y gestor de archivos ligero basado en la web, construido completamente en **Python** utilizando el framework **Flask**. Su propósito es ofrecer una interfaz rápida y sencilla para navegar, subir y gestionar archivos a través de un navegador web, almacenándolos localmente de forma estructurada.

## ✨ Características

*   **Subida de Archivos:** Sube múltiples archivos directamente desde la interfaz web al servidor de forma segura (utilizando `secure_filename` de Werkzeug).
*   **Exploración de Archivos:** Navega por los directorios almacenados en la carpeta `storage`.
*   **Gestión Simple:** Descarga y administración básica desde cualquier dispositivo en red que pueda acceder a la instancia Flask.
*   **Plantillas Web:** Interfaz basada en HTML, CSS y plantillas integradas de Flask (`render_template`).

## 🛠️ Tecnologías Usadas

*   **Backend:** Python 3, [Flask](https://flask.palletsprojects.com/)
*   **Seguridad y Utilidades:** Werkzeug
*   **Frontend:** HTML5, CSS (Archivos estáticos y plantillas)

## 🚀 Instalación y Despliegue

Sigue estos pasos para desplegar el gestor de archivos en tu máquina local:

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/elyxdev/webgest.git
    cd webgest
    ```

2.  **Crea un entorno virtual (Recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Linux/macOS
    venv\Scripts\activate     # En Windows
    ```

3.  **Instala las dependencias:**
    Todas las dependencias están listadas en el archivo `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecuta la aplicación:**
    ```bash
    python app.py
    ```
    La aplicación se levantará y podrás acceder desde tu navegador en la dirección por defecto de Flask (usualmente `http://127.0.0.1:5000/`).

## 📁 Estructura del Proyecto

*   `app.py`: Archivo principal que contiene las rutas de Flask y la lógica del backend.
*   `requirements.txt`: Lista de dependencias de Python (Flask, Werkzeug).
*   `storage/`: Directorio donde se guardarán todos los archivos subidos (no se rastrean en Git por seguridad).
*   `templates/`: Plantillas HTML utilizadas para renderizar la interfaz.
*   `static/`: Archivos estáticos como hojas de estilo (CSS) o scripts (JS).

## 👨‍💻 Autor

Creado y desarrollado por **Elyx** ([@elyxdev](https://github.com/elyxdev)).

¡Si encuentras útil este gestor o quieres proponer nuevas funciones, eres bienvenido a enviar un *Pull Request* o abrir un *Issue*!

# Zapotal Enterprise

Sistema de gestión comunal para la Comunidad Campesina Zapotal — plataforma integral con backend y frontend.

## Versión actual: 1.1.2

## Estructura

- **comunidad_zapotal_backend/** — API REST con Django + Django REST Framework + MySQL
- **comunidad_zapotal_frontend/** — Frontend con Vite + React 19 + axios
- **setup.bat** — Script de configuración y ejecución automática

## Requisitos previos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

- **Python 3.11+**
- **Node.js 18+**
- **MySQL** corriendo en local con la base de datos `comunidad_zapotal_db` creada

> ⚠️ La base de datos debe llamarse **`comunidad_zapotal_db`** y estar accesible en `localhost:3306`.  
> Configura tus credenciales en `comunidad_zapotal_backend/.env` (usa `.env.example` como referencia).

## Inicio rápido

Una vez clonado el repositorio y cumplidos los requisitos, ejecuta:

```batch
setup.bat
```

Este script hará automáticamente:

1. Crea el entorno virtual `zapotal_venv` en `comunidad_zapotal_backend/`
2. Instala las dependencias del backend (`pip install -r requirements.txt`)
3. Ejecuta las migraciones de Django (`python manage.py migrate`)
4. Instala las dependencias del frontend (`npm install`)
5. Abre dos ventanas:
   - **Backend** → `http://127.0.0.1:8000`
   - **Frontend** → `http://localhost:5173`

## Manual paso a paso

Si prefieres hacerlo manualmente:

### Backend

```batch
cd comunidad_zapotal_backend
python -m venv zapotal_venv
zapotal_venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```batch
cd comunidad_zapotal_frontend
npm install
npm run dev
```

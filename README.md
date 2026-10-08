# Gestión de solicitudes

Aplicación local para registrar solicitudes, consultar el listado y actualizar su estado. El backend está hecho con Flask y SQLite; la interfaz usa React y Vite.

## Requisitos

- Python 3.10 o posterior
- Node.js 18 o posterior y npm

## Ejecutar en local

Abre dos terminales desde la carpeta del proyecto.

**1. Backend (terminal 1)**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

La API queda disponible en `http://localhost:5000`. SQLite crea `backend/requests.db` automáticamente al iniciar.

**2. Frontend (terminal 2)**

```powershell
cd frontend
npm install
npm run dev
```

Abre la URL que muestre Vite, normalmente `http://localhost:5173`.

## API

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/api/requests` | Crea una solicitud; requiere `applicant_name`, `document_type`, `document_number` y `request_date` (`AAAA-MM-DD`). |
| `GET` | `/api/requests` | Devuelve todas las solicitudes, de la más reciente a la más antigua. |
| `PATCH` | `/api/requests/<id>/status` | Actualiza el estado usando `{"status":"aprobada"}`. Estados válidos: `pendiente`, `aprobada`, `rechazada`. |

El nombre solo acepta letras, espacios, apóstrofos y guiones; el número de documento solo acepta dígitos ASCII. Todos los campos son obligatorios y el tipo debe ser una de las opciones del formulario. Los errores de validación responden con HTTP `400`; una solicitud inexistente responde `404`. Cada capa tiene una responsabilidad: `routes.py` define HTTP, `services.py` valida las reglas y `repository.py` ejecuta consultas SQLite.

## Pruebas

Desde la carpeta `backend`, con el entorno virtual activado:

```powershell
python -m unittest discover -s tests -v
```

## Publicar en GitHub

Para entregar la prueba, crea un repositorio público en GitHub y publica el historial desde la carpeta del proyecto:

```powershell
git init
git add .
git commit -m "Construye aplicación de gestión de solicitudes"
git branch -M main
git remote add origin https://github.com/USUARIO/REPOSITORIO.git
git push -u origin main
```
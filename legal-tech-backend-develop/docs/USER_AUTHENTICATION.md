# Sistema de Autenticación de Usuarios

Este documento describe el sistema de autenticación de usuarios implementado en el backend de LegalTech.

## Características

- **Autenticación JWT**: Tokens seguros con expiración automática
- **Múltiples roles**: Admin, Developer, Tester, Client, Bot, Guest
- **Gestión de usuarios**: Registro, login, cambio de contraseña
- **Control de acceso**: Middleware para proteger endpoints
- **Encriptación de contraseñas**: Usando bcrypt

## Roles de Usuario

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| `admin` | Administrador del sistema | Acceso completo, gestión de usuarios |
| `developer` | Desarrollador | Acceso a funcionalidades de desarrollo |
| `tester` | Tester | Acceso a funcionalidades de testing |
| `client` | Cliente | Acceso a funcionalidades básicas |
| `bot` | Bot/Automatización | Acceso limitado para automatizaciones |
| `guest` | Invitado | Acceso muy limitado (por defecto) |

## Instalación y Configuración

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Agregar a tu archivo `.env`:

```env
# JWT Secret Key (cambiar en producción)
JWT_SECRET_KEY="your-super-secret-key-change-in-production"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Crear Usuario Administrador

```bash
python scripts/create_admin_user.py admin admin123
```

## Endpoints de Autenticación

### Registro de Usuario
```http
POST /v1/auth/register/
Content-Type: application/json

{
  "name": "usuario",
  "password": "contraseña123",
  "role": "client"
}
```

### Login
```http
POST /v1/auth/login/
Content-Type: application/json

{
  "username": "usuario",
  "password": "contraseña123"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "usuario",
  "role": "client",
  "expires_at": "2024-01-01T12:00:00"
}
```

### Obtener Información del Usuario Actual
```http
GET /v1/auth/me/
Authorization: Bearer <access_token>
```

### Cambiar Contraseña
```http
POST /v1/auth/change-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "contraseña123",
  "new_password": "nueva_contraseña456"
}
```

## Protección de Endpoints

### Usar Middleware de Autenticación

```python
from routers.auth.middleware import get_current_active_user, require_admin

@router.get("/protected-endpoint/")
async def protected_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    return {"message": f"Hello {current_user.name}!"}

@router.get("/admin-only/")
async def admin_endpoint(
    current_user: User = Depends(require_admin)
):
    return {"message": "Admin access granted"}
```

### Requerir Rol Específico

```python
from routers.auth.middleware import require_role

@router.get("/developer-only/")
async def developer_endpoint(
    current_user: User = Depends(require_role("developer"))
):
    return {"message": "Developer access granted"}
```

## Endpoints de Administración

### Listar Todos los Usuarios
```http
GET /v1/auth/users/
Authorization: Bearer <admin_token>
```

### Obtener Usuario por ID
```http
GET /v1/auth/users/{user_id}/
Authorization: Bearer <admin_token>
```

### Actualizar Rol de Usuario
```http
PUT /v1/auth/users/{user_id}/role/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "role": "developer"
}
```

### Desactivar Usuario
```http
DELETE /v1/auth/users/{user_id}/
Authorization: Bearer <admin_token>
```

## Migración desde el Sistema Anterior

El nuevo sistema de autenticación coexiste con el sistema anterior basado en tokens estáticos. Para migrar gradualmente:

1. **Mantener compatibilidad**: Los endpoints existentes siguen funcionando
2. **Nuevos endpoints**: Usar el nuevo sistema para nuevas funcionalidades
3. **Migración gradual**: Actualizar endpoints uno por uno

### Ejemplo de Migración

**Antes (token estático):**
```python
@router.post("/endpoint/")
async def old_endpoint(
    api_key: str = Depends(get_api_key)
):
    return {"message": "Protected endpoint"}
```

**Después (autenticación de usuario):**
```python
@router.post("/endpoint/")
async def new_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    return {"message": f"Hello {current_user.name}!"}
```

## Testing

### Ejecutar el Ejemplo

```bash
python examples/user_auth_example.py
```

### Crear Usuarios de Prueba

```python
from services.auth import UserAuthService
from models.api.user import UserCreate
from models.sql import UserRole

# Crear usuario de prueba
user_data = UserCreate(
    name="testuser",
    password="testpass123",
    role=UserRole.CLIENT
)

user = UserAuthService.create_user(session, user_data)
```

## Seguridad

### Mejores Prácticas

1. **Cambiar la clave secreta**: Usar una clave fuerte en producción
2. **Configurar expiración**: Ajustar `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
3. **Validar contraseñas**: Las contraseñas deben tener al menos 8 caracteres
4. **Usar HTTPS**: Siempre en producción
5. **Logs de seguridad**: Monitorear intentos de login fallidos

### Configuración de Producción

```env
JWT_SECRET_KEY="your-super-secure-random-key-here"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
DEBUG_MODE=false
```

## Referencias

- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [bcrypt Documentation](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html) 
# Video Local Storage - Módulo Odoo 18

Este módulo permite el almacenamiento local y reproducción de archivos de video MP4 en Odoo 18, manteniendo la compatibilidad con enlaces externos de YouTube, Vimeo y Google Drive.

## Características

### 🎥 Funcionalidades Principales
- **Almacenamiento Local**: Subida y almacenamiento de archivos de video MP4 en el servidor
- **Reproductor Integrado**: Reproductor HTML5 con controles personalizados
- **Compatibilidad Externa**: Soporte para YouTube, Vimeo, Google Drive y URLs directas
- **Gestión de Categorías**: Organización de videos por categorías personalizables
- **Sistema de Etiquetas**: Clasificación con etiquetas de colores
- **Miniaturas**: Soporte para miniaturas personalizadas
- **Controles de Acceso**: Sistema de permisos y videos públicos/privados

### 🔧 Características Técnicas
- **Formatos Soportados**: MP4, AVI, MOV, WMV, WebM
- **Límite de Tamaño**: 500MB por archivo
- **Validación de Archivos**: Verificación automática de formato y tamaño
- **Metadatos**: Extracción automática de información técnica
- **Responsive Design**: Interfaz adaptable a dispositivos móviles

## Instalación

### Requisitos Previos
- Odoo 18.0+
- Python 3.8+
- Espacio suficiente en disco para almacenamiento de videos

### Pasos de Instalación

1. **Copiar el módulo**:
   ```bash
   cp -r video_local_storage /path/to/odoo/addons/
   ```

2. **Actualizar lista de módulos**:
   ```bash
   # En Odoo shell o interfaz web
   # Ir a Aplicaciones > Actualizar lista de aplicaciones
   ```

3. **Instalar el módulo**:
   ```bash
   # Buscar "Video Local Storage" en Aplicaciones e instalar
   ```

### Configuración Inicial

1. **Permisos de Directorio**:
   ```bash
   # Asegurar permisos de escritura en el directorio de attachments
   chmod 755 /path/to/odoo/filestore/
   ```

2. **Configuración del Servidor**:
   ```ini
   # En odoo.conf
   [options]
   max_cron_threads = 2
   limit_memory_hard = 2684354560
   limit_memory_soft = 2147483648
   ```

## Uso

### Subir Videos Locales

1. **Acceder al Módulo**:
   - Ir a **Videos** en el menú principal
   - Hacer clic en **Crear**

2. **Configurar Video**:
   - **Nombre**: Título del video
   - **Tipo de Video**: Seleccionar "Archivo Local"
   - **Archivo de Video**: Subir archivo MP4
   - **Categoría**: Asignar categoría (opcional)
   - **Etiquetas**: Añadir etiquetas (opcional)

3. **Reproducir Video**:
   - Hacer clic en **Reproducir Video**
   - Usar controles HTML5 integrados

### Agregar Videos Externos

1. **YouTube**:
   - Tipo: "YouTube"
   - URL: `https://www.youtube.com/watch?v=VIDEO_ID`

2. **Vimeo**:
   - Tipo: "Vimeo"
   - URL: `https://vimeo.com/VIDEO_ID`

3. **Google Drive**:
   - Tipo: "Google Drive"
   - URL: `https://drive.google.com/file/d/FILE_ID/view`

### Gestión de Categorías

1. **Crear Categorías**:
   - Ir a **Videos > Categorías**
   - Crear nueva categoría con nombre y color

2. **Asignar Categorías**:
   - En el formulario de video, seleccionar categoría
   - Filtrar por categoría en la vista de lista

### Sistema de Etiquetas

1. **Crear Etiquetas**:
   - Ir a **Videos > Etiquetas**
   - Crear etiqueta con nombre y color

2. **Usar Etiquetas**:
   - Seleccionar múltiples etiquetas por video
   - Filtrar y buscar por etiquetas

## API y Desarrollo

### Modelos Principales

```python
# Modelo principal de videos
class VideoLocal(models.Model):
    _name = 'video.local'
    
    # Campos principales
    name = fields.Char('Nombre')
    video_file = fields.Binary('Archivo de Video')
    video_type = fields.Selection([...])
    video_url = fields.Char('URL del Video')
    
    # Métodos principales
    def action_play_video(self):
        # Reproducir video
        pass
    
    def action_download_video(self):
        # Descargar video local
        pass
```

### Widgets JavaScript

```javascript
// Widget personalizado para reproductor
import { VideoPlayerWidget } from './video_player';

// Utilidades para manejo de video
import { VideoPlayerUtils } from './video_player';

// Extraer miniatura
const thumbnail = await VideoPlayerUtils.extractThumbnail(videoFile);

// Validar formato
const isValid = VideoPlayerUtils.isValidVideoFormat(filename);
```

### Vistas Personalizadas

```xml
<!-- Vista Kanban con reproductor -->
<kanban>
    <field name="thumbnail"/>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_card">
                <img t-att-src="kanban_image('video.local', 'thumbnail', record.id.raw_value)"/>
                <button name="action_play_video" type="object">
                    <i class="fa fa-play"/> Reproducir
                </button>
            </div>
        </t>
    </templates>
</kanban>
```

## Personalización

### Agregar Nuevos Formatos

```python
# En models/video_local.py
@api.constrains('video_file')
def _check_video_file_format(self):
    for record in self:
        if record.video_file and record.video_filename:
            # Agregar nuevos formatos aquí
            allowed_formats = ('.mp4', '.avi', '.mov', '.wmv', '.webm', '.mkv')
            if not record.video_filename.lower().endswith(allowed_formats):
                raise ValidationError(_('Formato no soportado'))
```

### Personalizar Reproductor

```css
/* En static/src/css/video_player.css */
.o_video_player video {
    border-radius: 15px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.o_video_control_btn {
    background: linear-gradient(45deg, #007bff, #0056b3);
    color: white;
    border: none;
}
```

### Agregar Validaciones

```python
# Validación de duración máxima
@api.constrains('duration')
def _check_video_duration(self):
    for record in self:
        if record.duration and record.duration > 3600:  # 1 hora
            raise ValidationError(_('La duración del video no puede exceder 1 hora'))
```

## Seguridad

### Permisos por Defecto

```csv
# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_video_local_user,video.local.user,model_video_local,base.group_user,1,1,1,1
access_video_local_public,video.local.public,model_video_local,base.group_public,1,0,0,0
```

### Reglas de Seguridad

```xml
<!-- Regla para videos privados -->
<record id="video_local_rule" model="ir.rule">
    <field name="name">Video Local Rule</field>
    <field name="model_id" ref="model_video_local"/>
    <field name="domain_force">[('is_public', '=', True)]</field>
    <field name="groups" eval="[(4, ref('base.group_public'))]"/>
</record>
```

## Solución de Problemas

### Error: "Archivo demasiado grande"
```python
# Aumentar límite en odoo.conf
[options]
limit_memory_hard = 4294967296  # 4GB
limit_memory_soft = 3221225472  # 3GB
```

### Error: "Formato no soportado"
```python
# Verificar extensiones permitidas
def _check_video_file_format(self):
    # Añadir más formatos si es necesario
    allowed_formats = ('.mp4', '.avi', '.mov', '.wmv', '.webm')
```

### Error: "No se puede reproducir"
```javascript
// Verificar soporte del navegador
if (video.canPlayType('video/mp4')) {
    // Navegador soporta MP4
} else {
    // Mostrar mensaje de error
}
```

## Mantenimiento

### Limpieza de Archivos
```python
# Limpiar archivos huérfanos
def clean_orphaned_files(self):
    # Implementar lógica de limpieza
    pass
```

### Optimización de Base de Datos
```sql
-- Índices recomendados
CREATE INDEX idx_video_local_type ON video_local(video_type);
CREATE INDEX idx_video_local_public ON video_local(is_public);
CREATE INDEX idx_video_local_category ON video_local(category_id);
```

## Contribución

### Estructura del Proyecto
```
video_local_storage/
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── video_local.py
├── views/
│   ├── video_local_views.xml
│   └── video_local_menu.xml
├── security/
│   └── ir.model.access.csv
├── static/
│   ├── src/
│   │   ├── js/
│   │   │   └── video_player.js
│   │   ├── css/
│   │   │   └── video_player.css
│   │   └── xml/
│   │       └── video_player_templates.xml
│   └── description/
│       └── icon.png
└── README.md
```

### Normas de Código
- Seguir PEP 8 para Python
- Usar ESLint para JavaScript
- Validar XML con xmllint
- Documentar todas las funciones

## Licencia

Este módulo está licenciado bajo LGPL-3.0.

## Soporte

Para soporte técnico:
- Email: soporte@tucompania.com
- Documentación: https://docs.tucompania.com/video-local-storage
- Issues: https://github.com/tucompania/video-local-storage/issues

---

**Versión**: 18.0.1.0.0  
**Autor**: Tu Nombre  
**Fecha**: 2025
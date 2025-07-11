import os
import base64
import logging
from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

class VideoLocal(models.Model):
    _name = 'video.local'
    _description = 'Video Local Storage'
    _order = 'create_date desc'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')
    
    # Campos para archivo local
    video_file = fields.Binary(string='Archivo de Video', attachment=True)
    video_filename = fields.Char(string='Nombre del Archivo')
    video_mimetype = fields.Char(string='Tipo MIME')
    video_filesize = fields.Integer(string='Tamaño del Archivo')
    
    # Campos para enlaces externos (compatibilidad)
    video_url = fields.Char(string='URL del Video')
    video_type = fields.Selection([
        ('local', 'Archivo Local'),
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
        ('google_drive', 'Google Drive'),
        ('url', 'URL Directa')
    ], string='Tipo de Video', default='local')
    
    # Campos adicionales
    duration = fields.Float(string='Duración (segundos)')
    thumbnail = fields.Binary(string='Miniatura', attachment=True)
    is_public = fields.Boolean(string='Público', default=True)
    category_id = fields.Many2one('video.category', string='Categoría')
    tag_ids = fields.Many2many('video.tag', string='Etiquetas')
    
    # Campos computados
    video_embed_code = fields.Text(string='Código de Inserción', compute='_compute_video_embed_code')
    file_url = fields.Char(string='URL del Archivo', compute='_compute_file_url')

    @api.depends('video_file', 'video_url', 'video_type')
    def _compute_video_embed_code(self):
        for record in self:
            if record.video_type == 'local' and record.video_file:
                record.video_embed_code = f'''
                    <video controls style="width: 100%; max-width: 800px;">
                        <source src="/web/content/video.local/{record.id}/video_file/{record.video_filename}" type="{record.video_mimetype}">
                        Tu navegador no soporta la reproducción de video HTML5.
                    </video>
                '''
            elif record.video_type == 'youtube' and record.video_url:
                video_id = self._extract_youtube_id(record.video_url)
                if video_id:
                    record.video_embed_code = f'''
                        <iframe width="100%" height="315" src="https://www.youtube.com/embed/{video_id}" 
                                frameborder="0" allowfullscreen></iframe>
                    '''
                else:
                    record.video_embed_code = ''
            elif record.video_type == 'vimeo' and record.video_url:
                video_id = self._extract_vimeo_id(record.video_url)
                if video_id:
                    record.video_embed_code = f'''
                        <iframe src="https://player.vimeo.com/video/{video_id}" width="100%" height="315" 
                                frameborder="0" allowfullscreen></iframe>
                    '''
                else:
                    record.video_embed_code = ''
            elif record.video_type == 'google_drive' and record.video_url:
                file_id = self._extract_google_drive_id(record.video_url)
                if file_id:
                    record.video_embed_code = f'''
                        <iframe src="https://drive.google.com/file/d/{file_id}/preview" 
                                width="100%" height="315" allowfullscreen></iframe>
                    '''
                else:
                    record.video_embed_code = ''
            elif record.video_type == 'url' and record.video_url:
                record.video_embed_code = f'''
                    <video controls style="width: 100%; max-width: 800px;">
                        <source src="{record.video_url}" type="video/mp4">
                        Tu navegador no soporta la reproducción de video HTML5.
                    </video>
                '''
            else:
                record.video_embed_code = ''

    @api.depends('video_file', 'video_filename')
    def _compute_file_url(self):
        for record in self:
            if record.video_file and record.video_filename:
                record.file_url = f'/web/content/video.local/{record.id}/video_file/{record.video_filename}'
            else:
                record.file_url = ''

    @api.constrains('video_file', 'video_url', 'video_type')
    def _check_video_content(self):
        for record in self:
            if record.video_type == 'local' and not record.video_file:
                raise ValidationError(_('Debe seleccionar un archivo de video para el tipo "Archivo Local".'))
            elif record.video_type in ['youtube', 'vimeo', 'google_drive', 'url'] and not record.video_url:
                raise ValidationError(_('Debe proporcionar una URL para el tipo de video seleccionado.'))

    @api.constrains('video_file')
    def _check_video_file_format(self):
        for record in self:
            if record.video_file and record.video_filename:
                if not record.video_filename.lower().endswith(('.mp4', '.avi', '.mov', '.wmv', '.webm')):
                    raise ValidationError(_('Solo se permiten archivos de video en formatos: MP4, AVI, MOV, WMV, WebM.'))
                
                # Verificar tamaño del archivo (máximo 500MB)
                if record.video_filesize and record.video_filesize > 500 * 1024 * 1024:
                    raise ValidationError(_('El archivo de video no puede exceder 500MB.'))

    @api.model
    def create(self, vals):
        if vals.get('video_file') and vals.get('video_filename'):
            # Obtener información del archivo
            file_data = base64.b64decode(vals['video_file'])
            vals['video_filesize'] = len(file_data)
            
            # Determinar tipo MIME
            filename = vals['video_filename'].lower()
            if filename.endswith('.mp4'):
                vals['video_mimetype'] = 'video/mp4'
            elif filename.endswith('.avi'):
                vals['video_mimetype'] = 'video/x-msvideo'
            elif filename.endswith('.mov'):
                vals['video_mimetype'] = 'video/quicktime'
            elif filename.endswith('.wmv'):
                vals['video_mimetype'] = 'video/x-ms-wmv'
            elif filename.endswith('.webm'):
                vals['video_mimetype'] = 'video/webm'
            else:
                vals['video_mimetype'] = 'video/mp4'
        
        return super().create(vals)

    def write(self, vals):
        if vals.get('video_file') and vals.get('video_filename'):
            # Obtener información del archivo
            file_data = base64.b64decode(vals['video_file'])
            vals['video_filesize'] = len(file_data)
            
            # Determinar tipo MIME
            filename = vals['video_filename'].lower()
            if filename.endswith('.mp4'):
                vals['video_mimetype'] = 'video/mp4'
            elif filename.endswith('.avi'):
                vals['video_mimetype'] = 'video/x-msvideo'
            elif filename.endswith('.mov'):
                vals['video_mimetype'] = 'video/quicktime'
            elif filename.endswith('.wmv'):
                vals['video_mimetype'] = 'video/x-ms-wmv'
            elif filename.endswith('.webm'):
                vals['video_mimetype'] = 'video/webm'
            else:
                vals['video_mimetype'] = 'video/mp4'
        
        return super().write(vals)

    def _extract_youtube_id(self, url):
        """Extraer ID de video de YouTube desde URL"""
        import re
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _extract_vimeo_id(self, url):
        """Extraer ID de video de Vimeo desde URL"""
        import re
        pattern = r'(?:vimeo\.com\/)(?:.*\/)([0-9]+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def _extract_google_drive_id(self, url):
        """Extraer ID de archivo de Google Drive desde URL"""
        import re
        pattern = r'(?:drive\.google\.com\/file\/d\/)([a-zA-Z0-9_-]+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def action_play_video(self):
        """Acción para reproducir video"""
        self.ensure_one()
        return {
            'name': f'Reproducir: {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'video.local',
            'res_id': self.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'dialog_size': 'medium', 'play_video': True}
        }

    def action_download_video(self):
        """Acción para descargar video local"""
        self.ensure_one()
        if self.video_type == 'local' and self.video_file:
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/video.local/{self.id}/video_file/{self.video_filename}?download=true',
                'target': 'self',
            }
        else:
            raise UserError(_('Solo se pueden descargar archivos de video locales.'))


class VideoCategory(models.Model):
    _name = 'video.category'
    _description = 'Categoría de Video'
    
    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')
    color = fields.Integer(string='Color')
    video_ids = fields.One2many('video.local', 'category_id', string='Videos')
    video_count = fields.Integer(string='Cantidad de Videos', compute='_compute_video_count')
    
    @api.depends('video_ids')
    def _compute_video_count(self):
        for record in self:
            record.video_count = len(record.video_ids)


class VideoTag(models.Model):
    _name = 'video.tag'
    _description = 'Etiqueta de Video'
    
    name = fields.Char(string='Nombre', required=True)
    color = fields.Integer(string='Color')
    video_ids = fields.Many2many('video.local', string='Videos')
{
    'name': 'Video Local Storage',
    'version': '18.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Almacenamiento y reproducción de videos MP4 locales',
    'description': '''
        Módulo para permitir el almacenamiento local y reproducción de archivos de video MP4,
        manteniendo compatibilidad con YouTube, Vimeo y Google Drive.
        
        Características:
        - Subida de archivos MP4 al servidor
        - Reproductor de video integrado
        - Gestión de archivos de video
        - Compatibilidad con enlaces externos existentes
    ''',
    'author': 'Tu Nombre',
    'website': 'https://www.tucompania.com',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/video_local_views.xml',
        'views/video_local_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'video_local_storage/static/src/js/video_player.js',
            'video_local_storage/static/src/css/video_player.css',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
/** @odoo-module **/

import { Component, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Widget personalizado para reproducir videos
 */
export class VideoPlayerWidget extends Component {
    setup() {
        this.videoRef = useRef("video");
        this.notification = useService("notification");
        
        onMounted(() => {
            this.setupVideoPlayer();
        });
    }

    setupVideoPlayer() {
        const video = this.videoRef.el;
        if (!video) return;

        // Configurar eventos del reproductor
        video.addEventListener('loadstart', () => {
            console.log('Cargando video...');
        });

        video.addEventListener('loadedmetadata', () => {
            console.log('Metadatos cargados');
            this.updateDuration();
        });

        video.addEventListener('error', (e) => {
            console.error('Error al cargar el video:', e);
            this.notification.add(
                'Error al cargar el video. Verifique el formato y la conexión.',
                { type: 'danger' }
            );
        });

        video.addEventListener('ended', () => {
            console.log('Video terminado');
        });

        // Configurar controles personalizados si es necesario
        this.setupCustomControls();
    }

    setupCustomControls() {
        const video = this.videoRef.el;
        if (!video) return;

        // Agregar controles de velocidad de reproducción
        const speedControls = document.createElement('div');
        speedControls.className = 'video-speed-controls';
        speedControls.innerHTML = `
            <label>Velocidad:</label>
            <select class="video-speed-select">
                <option value="0.5">0.5x</option>
                <option value="1" selected>1x</option>
                <option value="1.25">1.25x</option>
                <option value="1.5">1.5x</option>
                <option value="2">2x</option>
            </select>
        `;

        // Insertar controles después del video
        video.parentNode.insertBefore(speedControls, video.nextSibling);

        // Manejar cambios de velocidad
        const speedSelect = speedControls.querySelector('.video-speed-select');
        speedSelect.addEventListener('change', (e) => {
            video.playbackRate = parseFloat(e.target.value);
        });
    }

    updateDuration() {
        const video = this.videoRef.el;
        if (!video || !video.duration) return;

        // Actualizar duración en el registro si es necesario
        if (this.props.record && this.props.record.data.duration !== video.duration) {
            this.props.record.update({
                duration: video.duration
            });
        }
    }

    onPlayPause() {
        const video = this.videoRef.el;
        if (!video) return;

        if (video.paused) {
            video.play();
        } else {
            video.pause();
        }
    }

    onFullscreen() {
        const video = this.videoRef.el;
        if (!video) return;

        if (video.requestFullscreen) {
            video.requestFullscreen();
        } else if (video.webkitRequestFullscreen) {
            video.webkitRequestFullscreen();
        } else if (video.msRequestFullscreen) {
            video.msRequestFullscreen();
        }
    }

    get videoSrc() {
        const record = this.props.record;
        if (!record) return '';

        const videoType = record.data.video_type;
        
        if (videoType === 'local' && record.data.video_file) {
            return `/web/content/video.local/${record.data.id}/video_file/${record.data.video_filename}`;
        } else if (videoType === 'url' && record.data.video_url) {
            return record.data.video_url;
        }
        
        return '';
    }

    get videoMimetype() {
        const record = this.props.record;
        return record?.data.video_mimetype || 'video/mp4';
    }

    get showVideoPlayer() {
        const record = this.props.record;
        return record?.data.video_type === 'local' || record?.data.video_type === 'url';
    }
}

VideoPlayerWidget.template = "video_local_storage.VideoPlayerWidget";
VideoPlayerWidget.props = {
    record: { type: Object, optional: true },
    readonly: { type: Boolean, optional: true },
};

// Registrar el widget
registry.category("fields").add("video_player", VideoPlayerWidget);

// Funciones de utilidad para el reproductor
export const VideoPlayerUtils = {
    /**
     * Formatear tiempo en formato mm:ss
     */
    formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return '00:00';
        
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        
        return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    },

    /**
     * Extraer miniatura de video (si es posible)
     */
    async extractThumbnail(videoFile) {
        return new Promise((resolve) => {
            const video = document.createElement('video');
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            video.addEventListener('loadedmetadata', () => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                
                video.currentTime = Math.min(1, video.duration / 2); // Buscar un frame del medio
            });

            video.addEventListener('seeked', () => {
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                canvas.toBlob((blob) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result);
                    reader.readAsDataURL(blob);
                }, 'image/jpeg', 0.8);
            });

            video.src = URL.createObjectURL(videoFile);
        });
    },

    /**
     * Validar formato de video
     */
    isValidVideoFormat(filename) {
        const validFormats = ['.mp4', '.avi', '.mov', '.wmv', '.webm'];
        return validFormats.some(format => filename.toLowerCase().endsWith(format));
    },

    /**
     * Obtener información básica del archivo de video
     */
    getVideoInfo(file) {
        return new Promise((resolve) => {
            const video = document.createElement('video');
            
            video.addEventListener('loadedmetadata', () => {
                resolve({
                    duration: video.duration,
                    width: video.videoWidth,
                    height: video.videoHeight,
                    size: file.size,
                    type: file.type
                });
            });

            video.src = URL.createObjectURL(file);
        });
    }
};
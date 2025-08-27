/**
 * JavaScript para manejo de modales de usuarios
 * Funcionalidades: Crear, Editar, Eliminar usuarios
 */

class UsuarioModalManager {
    constructor() {
        this.currentUsuarioId = null;
        this.isEditMode = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.cargarGrupos();
    }

    /**
     * Vincular eventos a los elementos del DOM
     */
    bindEvents() {
        // Botón para crear nuevo usuario
        document.getElementById('btnCrearUsuario')?.addEventListener('click', () => {
            this.abrirModalCrear();
        });

        // Botón para guardar usuario
        document.getElementById('btnGuardarUsuario')?.addEventListener('click', () => {
            this.guardarUsuario();
        });

        // Botón para confirmar cambio de estado
        document.getElementById('btnConfirmarCambioEstado')?.addEventListener('click', () => {
            this.confirmarCambioEstadoUsuario();
        });

        // Eventos del modal principal
        const modalUsuario = document.getElementById('modalUsuario');
        if (modalUsuario) {
            modalUsuario.addEventListener('hidden.bs.modal', () => {
                this.limpiarFormulario();
            });
        }

        // Eventos de teclado
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.cerrarModal();
            }
        });
    }

    /**
     * Cargar grupos activos desde la API
     */
    async cargarGrupos() {
        try {
            const response = await fetch('/cliente/ajax/obtener_grupos/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.popularSelectGrupos(data.grupos);
                }
            }
        } catch (error) {
            console.error('Error al cargar grupos:', error);
            this.mostrarMensaje('Error al cargar grupos', 'danger');
        }
    }

    /**
     * Popular el select de grupos
     */
    popularSelectGrupos(grupos) {
        const select = document.getElementById('id_group');
        if (!select) return;

        // Limpiar opciones existentes
        select.innerHTML = '<option value="">Seleccione un grupo</option>';

        // Agregar opciones
        grupos.forEach(grupo => {
            const option = document.createElement('option');
            option.value = grupo.id;
            option.textContent = grupo.name;
            if (grupo.description) {
                option.title = grupo.description;
            }
            select.appendChild(option);
        });
    }

    /**
     * Abrir modal para crear nuevo usuario
     */
    abrirModalCrear() {
        this.isEditMode = false;
        this.currentUsuarioId = null;
        
        // Actualizar título y botón
        document.getElementById('modalTitle').textContent = 'Crear Nuevo Usuario';
        document.getElementById('btnGuardarText').textContent = 'Guardar Usuario';
        
        // Limpiar formulario
        this.limpiarFormulario();
        
        // Ocultar imagen actual
        document.getElementById('imagen_actual_container').style.display = 'none';
        
        // Abrir modal
        const modal = new bootstrap.Modal(document.getElementById('modalUsuario'));
        modal.show();
    }

    /**
     * Abrir modal para editar usuario existente
     */
    async abrirModalEditar(usuarioId) {
        try {
            this.isEditMode = true;
            this.currentUsuarioId = usuarioId;
            
            // Actualizar título y botón
            document.getElementById('modalTitle').textContent = 'Editar Usuario';
            document.getElementById('btnGuardarText').textContent = 'Actualizar Usuario';
            
            // Obtener datos del usuario
            const response = await fetch(`/cliente/ajax/obtener_usuario/${usuarioId}/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.popularFormulario(data.usuario);
                    
                    // Mostrar imagen actual si existe
                    if (data.usuario.imagen_perfil_url) {
                        document.getElementById('imagen_actual').src = data.usuario.imagen_perfil_url;
                        document.getElementById('imagen_actual_container').style.display = 'block';
                    } else {
                        document.getElementById('imagen_actual_container').style.display = 'none';
                    }
                    
                    // Abrir modal
                    const modal = new bootstrap.Modal(document.getElementById('modalUsuario'));
                    modal.show();
                } else {
                    this.mostrarMensaje(data.message || 'Error al obtener usuario', 'danger');
                }
            } else {
                this.mostrarMensaje('Error al obtener usuario', 'danger');
            }
        } catch (error) {
            console.error('Error al abrir modal de edición:', error);
            this.mostrarMensaje('Error al obtener datos del usuario', 'danger');
        }
    }

    /**
     * Popular formulario con datos del usuario
     */
    popularFormulario(usuario) {
        document.getElementById('usuario_id').value = usuario.id;
        document.getElementById('id_primer_nombre').value = usuario.primer_nombre;
        document.getElementById('id_segundo_nombre').value = usuario.segundo_nombre || '';
        document.getElementById('id_primer_apellido').value = usuario.primer_apellido;
        document.getElementById('id_segundo_apellido').value = usuario.segundo_apellido || '';
        document.getElementById('id_email').value = usuario.email;
        document.getElementById('id_telefono').value = usuario.telefono || '';
        document.getElementById('id_group').value = usuario.group_id || '';
    }

    /**
     * Guardar usuario (crear o actualizar)
     */
    async guardarUsuario() {
        try {
            // Validar formulario
            if (!this.validarFormulario()) {
                return;
            }

            // Deshabilitar botón durante el envío
            const btnGuardar = document.getElementById('btnGuardarUsuario');
            btnGuardar.disabled = true;
            btnGuardar.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';

            // Preparar datos del formulario
            const formData = new FormData(document.getElementById('formUsuarioModal'));
            
            // Determinar URL según el modo
            const url = this.isEditMode 
                ? `/cliente/ajax/actualizar_usuario/${this.currentUsuarioId}/`
                : '/cliente/ajax/crear_usuario/';

            // Enviar datos
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });

            const data = await response.json();

            if (data.success) {
                this.mostrarMensaje(data.message, 'success');
                
                if (this.isEditMode) {
                    // Cerrar modal y recargar página para mostrar cambios
                    this.cerrarModal();
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    // Mostrar modal de usuario creado
                    this.mostrarModalUsuarioCreado(data.usuario);
                    // Después de mostrar el modal, recargar la página
                    setTimeout(() => {
                        window.location.reload();
                    }, 3000);
                }
            } else {
                // Mostrar errores de validación
                this.mostrarErroresValidacion(data.errors);
            }
        } catch (error) {
            console.error('Error al guardar usuario:', error);
            this.mostrarMensaje('Error interno del servidor', 'danger');
        } finally {
            // Restaurar botón
            const btnGuardar = document.getElementById('btnGuardarUsuario');
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = '<i class="material-symbols-outlined me-1">save</i><span id="btnGuardarText">' + 
                (this.isEditMode ? 'Actualizar Usuario' : 'Guardar Usuario') + '</span>';
        }
    }

    /**
     * Validar formulario del lado cliente
     */
    validarFormulario() {
        let isValid = true;
        
        // Limpiar errores previos
        this.limpiarErrores();
        
        // Validar campos obligatorios
        const camposObligatorios = ['primer_nombre', 'primer_apellido', 'email', 'group'];
        
        camposObligatorios.forEach(campo => {
            const elemento = document.getElementById(`id_${campo}`);
            if (!elemento.value.trim()) {
                this.mostrarErrorCampo(campo, 'Este campo es obligatorio');
                isValid = false;
            }
        });
        
        // Validar formato de email
        const email = document.getElementById('id_email').value;
        if (email && !this.validarEmail(email)) {
            this.mostrarErrorCampo('email', 'Formato de email inválido');
            isValid = false;
        }
        
        return isValid;
    }

    /**
     * Validar formato de email
     */
    validarEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    /**
     * Mostrar error en un campo específico
     */
    mostrarErrorCampo(campo, mensaje) {
        const elemento = document.getElementById(`id_${campo}`);
        const errorDiv = document.getElementById(`${campo}_error`);
        
        if (elemento && errorDiv) {
            elemento.classList.add('is-invalid');
            errorDiv.textContent = mensaje;
        }
    }

    /**
     * Limpiar todos los errores
     */
    limpiarErrores() {
        const campos = ['primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'email', 'telefono', 'group', 'imagen_perfil'];
        
        campos.forEach(campo => {
            const elemento = document.getElementById(`id_${campo}`);
            const errorDiv = document.getElementById(`${campo}_error`);
            
            if (elemento) {
                elemento.classList.remove('is-invalid');
            }
            if (errorDiv) {
                errorDiv.textContent = '';
            }
        });
    }

    /**
     * Mostrar errores de validación del servidor
     */
    mostrarErroresValidacion(errors) {
        if (errors) {
            Object.keys(errors).forEach(campo => {
                const mensaje = Array.isArray(errors[campo]) ? errors[campo][0] : errors[campo];
                this.mostrarErrorCampo(campo, mensaje);
            });
        }
    }

    /**
     * Mostrar mensaje en el modal
     */
    mostrarMensaje(mensaje, tipo) {
        const mensajeDiv = document.getElementById('mensajeModal');
        if (mensajeDiv) {
            mensajeDiv.className = `alert alert-${tipo}`;
            mensajeDiv.textContent = mensaje;
            mensajeDiv.style.display = 'block';
            
            // Ocultar mensaje después de 5 segundos
            setTimeout(() => {
                mensajeDiv.style.display = 'none';
            }, 5000);
        }
    }

    /**
     * Mostrar modal de usuario creado exitosamente
     */
    mostrarModalUsuarioCreado(usuario) {
        // Popular información del usuario
        document.getElementById('infoUsuarioCreado').innerHTML = `
            <p><strong>Nombre:</strong> ${usuario.primer_nombre} ${usuario.segundo_nombre} ${usuario.primer_apellido} ${usuario.segundo_apellido}</p>
            <p><strong>Email:</strong> ${usuario.email}</p>
            <p><strong>Teléfono:</strong> ${usuario.telefono || 'No especificado'}</p>
            <p><strong>Grupo:</strong> ${usuario.group_name}</p>
        `;
        
        // Mostrar contraseña generada
        document.getElementById('passwordGenerada').textContent = usuario.password;
        
        // Cerrar modal principal
        this.cerrarModal();
        
        // Abrir modal de usuario creado
        const modal = new bootstrap.Modal(document.getElementById('modalUsuarioCreado'));
        modal.show();
        
        // Agregar evento para recargar página cuando se cierre el modal
        const modalUsuarioCreado = document.getElementById('modalUsuarioCreado');
        modalUsuarioCreado.addEventListener('hidden.bs.modal', () => {
            window.location.reload();
        });
    }

    /**
     * Abrir modal de confirmación para cambiar estado
     */
    abrirModalConfirmarCambioEstado(usuarioId, nombreUsuario, estadoActual) {
        this.currentUsuarioId = usuarioId;
        this.currentEstado = estadoActual;
        
        const accion = estadoActual ? 'desactivar' : 'activar';
        const icono = estadoActual ? 'block' : 'check_circle';
        const color = estadoActual ? 'warning' : 'success';
        
        document.getElementById('nombreUsuarioCambioEstado').textContent = nombreUsuario;
        document.getElementById('accionCambioEstado').textContent = accion;
        document.getElementById('modalConfirmarCambioEstadoLabel').innerHTML = `
            <i class="material-symbols-outlined me-2">${icono}</i>
            Confirmar ${accion.charAt(0).toUpperCase() + accion.slice(1)} Usuario
        `;
        
        // Cambiar colores del modal según la acción
        const modalHeader = document.querySelector('#modalConfirmarCambioEstado .modal-header');
        modalHeader.className = `modal-header bg-${color} text-white`;
        
        const btnConfirmar = document.getElementById('btnConfirmarCambioEstado');
        btnConfirmar.className = `btn btn-${color}`;
        btnConfirmar.innerHTML = `<i class="material-symbols-outlined me-1">${icono}</i>Sí, ${accion.charAt(0).toUpperCase() + accion.slice(1)}`;
        
        const modal = new bootstrap.Modal(document.getElementById('modalConfirmarCambioEstado'));
        modal.show();
    }

    /**
     * Confirmar cambio de estado del usuario
     */
    async confirmarCambioEstadoUsuario() {
        try {
            const btnCambiar = document.getElementById('btnConfirmarCambioEstado');
            btnCambiar.disabled = true;
            btnCambiar.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Cambiando...';

            const response = await fetch(`/cliente/ajax/cambiar_estado_usuario/${this.currentUsuarioId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            const data = await response.json();

            if (data.success) {
                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalConfirmarCambioEstado'));
                modal.hide();
                
                // Mostrar mensaje de éxito
                this.mostrarMensajeGlobal(data.message, 'success');
                
                // Recargar página para mostrar cambios
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                this.mostrarMensajeGlobal(data.message, 'danger');
            }
        } catch (error) {
            console.error('Error al cambiar estado del usuario:', error);
            this.mostrarMensajeGlobal('Error interno del servidor', 'danger');
        } finally {
            const btnCambiar = document.getElementById('btnConfirmarCambioEstado');
            btnCambiar.disabled = false;
            btnCambiar.innerHTML = `<i class="material-symbols-outlined me-1">${this.currentEstado ? 'block' : 'check_circle'}</i>Sí, ${this.currentEstado ? 'Desactivar' : 'Activar'}`;
        }
    }

    /**
     * Agregar nueva fila a la tabla
     */
    agregarFilaTabla(usuario) {
        const tbody = document.querySelector('#myTable tbody');
        if (!tbody) return;

        const nuevaFila = document.createElement('tr');
        nuevaFila.id = `fila_usuario_${usuario.id}`;
        
        const nombreCompleto = `${usuario.primer_nombre} ${usuario.segundo_nombre} ${usuario.primer_apellido} ${usuario.segundo_apellido}`.trim();
        
        nuevaFila.innerHTML = `
            <td class="text-body text-center">${tbody.children.length + 1}</td>
            <td class="text-secondary text-center">${nombreCompleto}</td>
            <td class="text-secondary text-center">${usuario.email}</td>
            <td class="text-secondary text-center">${usuario.telefono || '-'}</td>
            <td class="text-secondary text-center">${usuario.group_name}</td>
            <td class="text-center">
                <span class="badge bg-success bg-opacity-10 text-success p-2 fs-12 fw-normal">Activo</span>
            </td>
            <td class="text-center">
                <div class="d-flex justify-content-center align-items-center gap-1">
                    <button class="btn bg-primary bg-opacity-10 fw-medium text-primary py-2 px-4" 
                            onclick="usuarioModalManager.abrirModalEditar(${usuario.id})">
                        <i class="material-symbols-outlined fs-16">edit</i>
                    </button>
                    <button class="btn bg-info bg-opacity-10 fw-medium text-info py-2 px-4" 
                            onclick="usuarioModalManager.verUsuario(${usuario.id})">
                        <i class="material-symbols-outlined fs-16">visibility</i>
                    </button>
                    <button class="btn bg-danger bg-opacity-10 fw-medium text-danger py-2 px-4" 
                            onclick="usuarioModalManager.abrirModalConfirmarCambioEstado(${usuario.id}, '${nombreCompleto}', ${usuario.is_active})">
                        <i class="material-symbols-outlined fs-16">block</i>
                    </button>
                </div>
            </td>
        `;
        
        tbody.appendChild(nuevaFila);
        
        // Actualizar numeración de filas
        this.actualizarNumeracionFilas();
    }

    /**
     * Actualizar fila existente en la tabla
     */
    actualizarFilaTabla(usuario) {
        const fila = document.getElementById(`fila_usuario_${usuario.id}`);
        if (!fila) return;

        const nombreCompleto = `${usuario.primer_nombre} ${usuario.segundo_nombre} ${usuario.primer_apellido} ${usuario.segundo_apellido}`.trim();
        
        // Actualizar celdas
        fila.children[1].textContent = nombreCompleto;
        fila.children[2].textContent = usuario.email;
        fila.children[3].textContent = usuario.telefono || '-';
        fila.children[4].textContent = usuario.group_name;
    }

    /**
     * Eliminar fila de la tabla
     */
    eliminarFilaTabla(usuarioId) {
        const fila = document.getElementById(`fila_usuario_${usuarioId}`);
        if (fila) {
            fila.remove();
            this.actualizarNumeracionFilas();
        }
    }

    /**
     * Actualizar numeración de filas
     */
    actualizarNumeracionFilas() {
        const filas = document.querySelectorAll('#myTable tbody tr');
        filas.forEach((fila, index) => {
            fila.children[0].textContent = index + 1;
        });
    }

    /**
     * Ver usuario (placeholder para futura implementación)
     */
    verUsuario(usuarioId) {
        // TODO: Implementar vista detallada del usuario
        console.log('Ver usuario:', usuarioId);
    }

    /**
     * Limpiar formulario
     */
    limpiarFormulario() {
        document.getElementById('formUsuarioModal').reset();
        this.limpiarErrores();
        document.getElementById('mensajeModal').style.display = 'none';
        document.getElementById('imagen_actual_container').style.display = 'none';
    }

    /**
     * Cerrar modal principal
     */
    cerrarModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalUsuario'));
        if (modal) {
            modal.hide();
        }
    }

    /**
     * Mostrar mensaje global (fuera del modal)
     */
    mostrarMensajeGlobal(mensaje, tipo) {
        // Crear toast o notificación
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${tipo} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${mensaje}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Agregar al contenedor de toasts
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toast);
        
        // Mostrar toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remover toast después de que se oculte
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.usuarioModalManager = new UsuarioModalManager();
});

// Exportar para uso global
window.UsuarioModalManager = UsuarioModalManager;

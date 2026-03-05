// tagify custom 
function limpiarTagify(campoId) {
    let cleanId = campoId.replace('#', '');
    let input = document.getElementById(cleanId);
    
    if (input && input.classList.contains("tagify-applied")) {
        // Remover Tagify existente
        let tagifyInstance = input.tagify;
        if (tagifyInstance) {
            tagifyInstance.destroy();
        }
        input.classList.remove("tagify-applied");
    }
}

function TagifyList(campoId, apiUrl) {
    let input = document.getElementById(campoId);

    if (!input) {
        console.warn(`El campo con ID "${campoId}" no existe.`);
        return;
    }

    let opciones = {
        whitelist: [],
        maxTags: 10,
        dropdown: {
            maxItems: 10,
            classname: "tags-look",
            enabled: 1,
            closeOnSelect: false
        }
    };

    if (!input.classList.contains("tagify-applied")) {
        let tagify = new Tagify(input, opciones);
        input.classList.add("tagify-applied");

        if (apiUrl) {
            $.ajax({
                url: apiUrl,
                method: 'GET',
                success: function(data) {
                    tagify.whitelist = data;
                },
                error: function(xhr, status, error) {
                    console.error('Error cargando profesiones:', error);
                }
            });
        }
    }
}

/**
 * Inicializa Tagify para listado de profesiones cargando whitelist desde API primero.
 * Similar a incializarTagifyLista pero con datos desde API (más confiable que TagifyList).
 * @param {string} campoId - ID del input
 * @param {string} apiUrl - URL de la API de profesiones
 * @param {function} onReady - Callback opcional cuando Tagify está listo (recibe instancia tagify)
 */
function TagifyProfesionesFromAPI(campoId, apiUrl, onReady) {
    let input = document.getElementById(campoId);
    if (!input) {
        console.warn(`TagifyProfesiones: campo "${campoId}" no existe.`);
        return;
    }

    limpiarTagify(campoId);

    if (!apiUrl) {
        console.warn('TagifyProfesiones: apiUrl no proporcionada.');
        return;
    }

    $.ajax({
        url: apiUrl,
        method: 'GET',
        dataType: 'json',
        success: function(whitelist) {
            if (!Array.isArray(whitelist)) whitelist = [];
            if (!input.classList.contains("tagify-applied")) {
                let tagify = new Tagify(input, {
                    whitelist: whitelist,
                    enforceWhitelist: false,
                    maxTags: 15,
                    dropdown: {
                        maxItems: 15,
                        classname: "tags-look",
                        enabled: 1,
                        closeOnSelect: false
                    }
                });
                input.classList.add("tagify-applied");
                if (typeof onReady === 'function') onReady(tagify);
            }
        },
        error: function(xhr, status, error) {
            console.error('TagifyProfesiones: Error cargando profesiones:', error);
            if (!input.classList.contains("tagify-applied")) {
                let tagify = new Tagify(input, { maxTags: 15 });
                input.classList.add("tagify-applied");
                if (typeof onReady === 'function') onReady(tagify);
            }
        }
    });
}

// Funcionalidad por Tagify
function inicializarTagify(campoId) {
    let input = document.getElementById(campoId);

    if (!input) {
        console.warn(`El campo con ID "${campoId}" no existe.`);
        return;
    }

    let tagify = new Tagify(input);

    // Forzar actualización del tamaño cuando se agregan tags
    tagify.on('add', function () {
        document.querySelectorAll(".tagify").forEach(function (element) {
            element.style.height = "auto";
        });
    });

    tagify.on('remove', function () {
        document.querySelectorAll(".tagify").forEach(function (element) {
            element.style.height = "auto";
        });
    });
}


function incializarTagifyLista(fieldId, whitelist) {
    var input = document.getElementById(fieldId);
    if (input) {
        var tagify = new Tagify(input, {
            whitelist: whitelist,
            enforceWhitelist: true, // Solo permitir valores de la lista
            maxTags: 10,
            dropdown: {
                maxItems: 20,
                classname: 'tags-look',
                enabled: 0,
                closeOnSelect: false
            }
        });

        // 👉 Ordenar automáticamente las etiquetas al añadirlas
        tagify.on('add', function(e) {
            // 🛑 Desactivar el evento para evitar el bucle
            tagify.off('add');

            let sortedTags = tagify.value
                .map(tag => tag.value)
                .sort(); // Ordena alfabéticamente

            // Reemplazar las etiquetas ordenadas
            tagify.removeAllTags(); // ✅ Elimina las etiquetas actuales
            tagify.addTags(sortedTags); // ✅ Añade las etiquetas ordenadas

            // ✅ Reactivar el evento después de actualizar
            tagify.on('add', this);
        });
    }
}

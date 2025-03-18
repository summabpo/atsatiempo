// tagify custom 
function TagifyList(campoId, listaSugerencias = []) {
    let input = document.getElementById(campoId);

    if (!input) {
        console.warn(`El campo con ID "${campoId}" no existe.`);
        return;
    }

    let opciones = {
        whitelist: listaSugerencias,
        maxTags: 10, // Número máximo de tags permitidos
        dropdown: {
            maxItems: 10,
            classname: "tags-look",
            enabled: 0, // Mostrar sugerencias siempre
            closeOnSelect: false
        }
    };

    // Inicializar Tagify solo si no se ha aplicado antes
    if (!input.classList.contains("tagify-applied")) {
        new Tagify(input, opciones);
        input.classList.add("tagify-applied"); // Evita inicialización duplicada
    }
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

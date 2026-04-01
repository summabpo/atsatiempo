function initializeSelect2(selector) {
    var $el = $(selector);
    if ($el.length && !$el.hasClass('select2-hidden-accessible')) {
        $el.select2({
            width: '100%',
            placeholder: "Seleccione una opción",
            allowClear: true,
            dropdownParent: $('body'),
            language: {
                noResults: function() { return 'No se encontraron resultados'; },
                searching: function() { return 'Buscando...'; }
            }
        }).on('select2:open', function() {
            setTimeout(function() {
                var $search = $('.select2-container--open .select2-search__field');
                if ($search.length) {
                    $search[0].focus();
                }
            }, 100);
        });
    }
}

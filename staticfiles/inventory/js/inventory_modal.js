$(document).ready(function() {
    const url = $('#addStockForm').data('add-stock-url');

    $('#addStockForm').on('submit', function(e) {
        e.preventDefault();

        $.ajax({
            type: 'POST',
            url: url,
            data: $(this).serialize(),
            // --- BLOCO SUCCESS CORRIGIDO ---
            success: function(response) {
                if (response.status === 'success') {
                    alert(response.message);
                    $('#addStockModal').modal('hide');
                    location.reload();
                }
            },

            error: function(response) {
                if (response.responseJSON && response.responseJSON.error) {
                    alert('Ocorreu um erro: ' + response.responseJSON.error);
                } else {
                    alert('Ocorreu um erro desconhecido. Tente novamente.');
                }
            }
        });
    });
    $('#addStockModal').on('hidden.bs.modal', function () {
        $('#addStockForm')[0].reset();
    });
});
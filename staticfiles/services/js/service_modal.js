document.addEventListener('DOMContentLoaded', function () {
    const serviceModal = document.getElementById('serviceModal');
    if (!serviceModal) return;

    const form = serviceModal.querySelector('#serviceForm');
    const modalTitle = serviceModal.querySelector('.modal-title');
    const submitButton = serviceModal.querySelector('#modalSubmitButton');
    const isBilledCheckbox = form.querySelector('#modalIsBilled');
    const billedDateContainer = form.querySelector('#billedDateContainer');

    function toggleBilledDateVisibility() {
        if (isBilledCheckbox.checked) {
            billedDateContainer.style.display = 'block';
        } else {
            billedDateContainer.style.display = 'none';
        }
    }

    isBilledCheckbox.addEventListener('change', toggleBilledDateVisibility);

    serviceModal.addEventListener('show.bs.modal', async function (event) {
        const button = event.relatedTarget;
        const mode = button.dataset.mode;
        
        form.reset();
        form.querySelectorAll('input, select, textarea').forEach(el => {
            el.readOnly = false;
            el.disabled = false;
        });
        submitButton.style.display = 'block';
        billedDateContainer.style.display = 'none';

        if (mode === 'create') {
            modalTitle.textContent = 'Adicionar Nova Marcação';
            submitButton.textContent = 'Adicionar';
            form.action = button.dataset.formUrl;
        } else {
            const dataUrl = button.dataset.url;
            
            try {
                const response = await fetch(dataUrl);
                if (!response.ok) throw new Error('Falha ao buscar dados.');
                const data = await response.json();

                form.company.value = data.company_id;
                form.weight.value = data.weight_id;
                form.bag_type.value = data.bag_type_id;
                form.quantity.value = data.quantity;
                form.oic.value = data.oic || '';
                form.notes.value = data.notes || '';
                form.is_billed.checked = data.is_billed;
                
                form.email.value = data.email || '';
                form.request_date.value = data.request_date ? data.request_date.split('T')[0] : '';
                form.billed_date.value = data.billed_date ? data.billed_date.split('T')[0] : '';
                
                toggleBilledDateVisibility();

            } catch (error) {
                console.error('Erro:', error);
            }

            if (mode === 'edit') {
                modalTitle.textContent = 'Editar Marcação';
                submitButton.textContent = 'Salvar Alterações';
                form.action = button.dataset.formUrl;
            } else if (mode === 'view') {
                modalTitle.textContent = 'Visualizar Marcação';
                submitButton.style.display = 'none';
                
                form.querySelectorAll('input, select, textarea').forEach(el => {
                    el.readOnly = true;
                    if (el.tagName === 'SELECT' || el.type === 'checkbox' || el.type === 'radio') {
                        el.disabled = true;
                    }
                });
            }
        }
    });
});
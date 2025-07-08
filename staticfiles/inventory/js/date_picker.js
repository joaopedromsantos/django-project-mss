$(function() {
  var drp = $('input[name="daterange"]').daterangepicker({
    opens: 'left',
    autoUpdateInput: false,
    locale: {
      format: "DD/MM/YYYY",
      applyLabel: "Aplicar",
      cancelLabel: "Limpar",
      fromLabel: "De",
      toLabel: "Até",
      customRangeLabel: "Personalizado",
      weekLabel: "S",
      daysOfWeek: ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"],
      monthNames: ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
      firstDay: 1
    }
  }, function(start, end, label) {
  });

  drp.on('apply.daterangepicker', function(ev, picker) {
      $(this).val(picker.startDate.format('DD/MM/YYYY') + ' - ' + picker.endDate.format('DD/MM/YYYY'));
  });

  drp.on('cancel.daterangepicker', function(ev, picker) {
      $(this).val('');
  });
});
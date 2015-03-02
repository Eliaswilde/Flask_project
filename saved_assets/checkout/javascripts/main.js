$(document).ready(function(){
	$('#checkout-wizard').bootstrapWizard({
		onTabClick: function(tab, navigation, index) {
			return false;
		},
		tabClass: '',
		nextSelector: '.btn-next'
	});
	
	$('.btn-next-2').click(function () {
		$('#checkout-wizard').bootstrapWizard('show', 2);
		return false;
	});
});
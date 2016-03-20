$.rsUrl = "/web_decode";
var convertText = function(){
	var textVar = $.trim($('#textArea1').val());
	$('#convert').attr('disabled', true); 		
	$('#example1').attr('disabled', true); 
	$('#example2').attr('disabled', true); 	
	$.ajax({
		url: $.rsUrl,
		type: 'POST',
		data: JSON.stringify({"query":textVar}),
		contentType: "application/json; charset=utf-8",
		success: function (data, json, textStatus) {
			$( "#textArea2" ).val( data.answer);										
		},
		error: function () {},
		complete: function (data, json, XMLHttpRequest, textStatus) {
			$('#convert').attr('disabled', false); 
			$('#example1').attr('disabled', false); 
			$('#example2').attr('disabled', false); 
		}
	});								
};
$( "#textArea1" ).keypress(function(e) {
	if(e.which == 13) {
		convertText();
	}
});
$( "#convert" ).click(function() {
	convertText();
});
$( "#example1" ).click(function() {
	$('#textArea1').val("Содержание зерен крупностью свыше десяти миллиметров не должно превышать пять процентов по массе.");
	convertText();
});
$( "#example2" ).click(function() {
	$('#textArea1').val("Листы гипсокартонные или эквивалент. Отклонение от прямоугольности не должно быть более 6 мм.");
	convertText();
});
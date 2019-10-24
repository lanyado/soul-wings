$(".dropdown-menu").on('click', '.dropdown-item', function(){
	$("#dropdownMenuButton").text($(this).text());
});

/*================ sendSearchString====================*/
function sendSearchString(){
	var type = $.trim($($('.option:checked')[0]).val())
	if (type=='או')
		op = "or";
	else
		op = "and";
	$('.cs-loader').css('display','block');

	$.get('/results',{
		search_string: $('#searchBar').val(),
    	operator: op
   }, function(data) {
   		$('.cs-loader').css('display','none');
		console.log(data)
        document.open('text/html');
        document.write(data);
        document.close();
    })
}

$('#searchBar').keyup(function(e){
    if(e.keyCode == 13)
        sendSearchString();
});

$(".fa-search").on('click', function(){
	sendSearchString();
});

$(".search-icons").on('click', function(){
	$('#searchBar').val('');
});

$(".fa-question-circle").on('click', function(){
	Swal.fire({
		type: 'question',
		title: 'חיפוש קבצים מהמאגר',
		html: '<span class="highlight">וגם</span> יחפש קבצים המכילים את כל הביטויים שתכניס.<br><span class="highlight">או</span> יחפש קבצים המכילים לפחות אחד מהביטויים שתכניס.<br>הפרדה בין ביטויים תעשה באמצעות מקש הרווח. <br>יש להכניס לגרשיים ביטויים המכילים יותר ממילה אחת, (לדוגמא: "הצלב האדום").',
		confirmButtonText: 'הבנתי',
	})
});

$('.btn.btn-secondary').removeClass('waves-effect waves-light')


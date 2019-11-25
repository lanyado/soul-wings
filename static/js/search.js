/*var user_token = $.cookie("user_token");
if (!(user_token)){
	window.location = 'landing_page';
}*/

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
	var st = $.trim($('#searchBar').val());
	st = st.replace(/\s\s+/g, ' ');
	if (st.length>0){
		$('.cs-loader').css('display','block');

		$.get('/results',{
			//user_token: user_token,
			search_string: st,
	    	operator: op
	   }, function(data) {
	   		//$('.cs-loader').css('display','none');
	        document.open('text/html');
	        document.write(data);
	        document.close();
	    })
	}
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
		html: '● &nbsp;הפרדה  בין ביטויים תעשה באמצעות מקש הרווח. <br>● &nbsp;יש להכניס לגרשיים ביטויים המכילים יותר ממילה אחת, (לדוגמא: "הצלב האדום").<br><span class="highlight">או</span> - חיפוש קבצים המכילים <b>לפחות אחד </b>מהביטויים.<br><span class="highlight">וגם</span> - חיפוש קבצים המכילים את <b>כל </b>הביטויים.',
		confirmButtonText: 'הבנתי',
	})
});

$('.btn.btn-secondary').removeClass('waves-effect waves-light')
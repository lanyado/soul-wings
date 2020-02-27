/*================ send search string ====================*/
function sendSearchString(){
	var type = $.trim($($('.option:checked')[0]).val())
	if (type=='או')
		operator = "or";
	else
		operator = "and";
	var searchString = $.trim($('#searchBar').val());
	searchString = searchString.replace(/\s\s+/g, ' ');
	if (searchString.length>0){
		runLoadingAnimation();
		$.get('/results',{
			search_string: searchString,
	    	operator: operator
	   }, function(data) {
	        document.open('text/html');
	        document.write(data);
	        document.close();
	    })
	}
}

$(".dropdown-menu").on('click', '.dropdown-item', function(){
	$("#dropdownMenuButton").text($(this).text());
});

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

$('.btn.btn-secondary').removeClass('waves-effect waves-light')
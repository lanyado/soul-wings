function sendSearchString (searchString, operator) {
	const queryUrl = `${window.location}search?q=${searchString}&o=${operator}`;
	window.location = queryUrl;
}

function getSearchVariables () {
	const type = $.trim($($('.option:checked')[0]).val());
	const operator = (type === 'או') ? 'or' : 'and';
	let searchString = $.trim($('#searchBar').val());
	searchString = searchString.replace(/\s\s+/g, ' ');

	return { searchString, operator };
}

function search() {
	const { searchString, operator } = getSearchVariables();

	if (searchString.length > 0) {
		runLoadingAnimation();
		sendSearchString(searchString, operator);
	}
}

$('.dropdown-menu').on('click', '.dropdown-item', () => {
	$('#dropdownMenuButton').text($(this).text());
});

$('#searchBar').keyup((e) => {
	if (e.keyCode === 13) search(); // ENTER key code
});

$('.fa-search').on('click', () => { // search icon
	search();
});

$('.fa-times').on('click', () => { // X icon
	$('#searchBar').val('');
});

$('.btn.btn-secondary').removeClass('waves-effect waves-light');

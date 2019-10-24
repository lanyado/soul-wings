$('#dtBasicExample, #dtBasicExample-1, #dt-more-columns, #dt-less-columns').mdbEditor();
$('.dataTables_length').addClass('bs-select');

$('.unsortable').removeClass('sorting sorting_asc sorting_desc');
	$('.unsortable').removeAttr("aria-sort")

$(".th-sm").click(function() {
	$('.unsortable').removeClass('sorting sorting_asc sorting_desc');
	$('.unsortable').removeAttr("aria-sort")
});

$('#dtBasicExample_info').css("display","none");

// Add the number of results on the top of the results table
var str = $('#dtBasicExample_info').html();
var res = str.split(" ");
var num = res[res.length-2];
$('#numOfResults').html(num+" תוצאות");

// Mark the words in yellow
var words = $.trim($('#searchBar').val()).split(" ");
$.each(words, function (index, value) {
    $(".text:contains(" + value + ")").html(function (_, html) {
        var regex = new RegExp(value, 'g');
        return html.replace(regex, '<mark>' + value + '</mark>');
    });
});

// Take care of multi sentences in one document
$('.contentSection').each(function(){
    if($(this).next().attr('class')=='contentSection')
        $('<hr>').insertAfter( $(this) );
})

$('.popup').on('toggle', function() {
   if ($(this).attr("open") == "open")
        $($(this).find("video")).get(0).play();
	else
		$($(this).find("video")).get(0).pause();
})
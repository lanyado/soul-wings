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

// no results alert when there are not results
if($('tbody:contains("No data available in table")').length>0){
    $('#results').html("<i class=׳far fa-frown׳></i><h2>מצטערים, לא נמצאו תוצאות עבור שאילתת החיפוש שלך :(</h2>")
}

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

// auto play when open the video and auto pause when close the video
$('.popup').on('toggle', function() {
   if ($(this).attr("open") == "open")
        $($(this).find("video")).get(0).play();
	else
		$($(this).find("video")).get(0).pause();
})

// open the information about the search popup when click on the question mark icon
$(".fa.fa-question-circle.search-area").on('click', function(){
    Swal.fire({
        type: 'question',
        title: 'חיפוש קבצים מהמאגר',
        html: '● &nbsp;הפרדה  בין ביטויים תעשה באמצעות מקש הרווח. <br>● &nbsp;יש להכניס לגרשיים ביטויים המכילים יותר ממילה אחת, (לדוגמא: "הצלב האדום").<br><span class="highlight">או</span> - חיפוש קבצים המכילים <b>לפחות אחד </b>מהביטויים.<br><span class="highlight">וגם</span> - חיפוש קבצים המכילים את <b>כל </b>הביטויים.',
        confirmButtonText: 'הבנתי',
        showCloseButton: true
    })
});
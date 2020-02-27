// animation until the page is loaded
runLoadingAnimation();

$(window).on('load', function() {
    setTimeout(function(){ 
        stopLoadingAnimation();
    }, 3000);
});

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

var words = $.trim($('#searchBar').val()).split(" ");

function addFunctionsToTr(){
    $("tr").not(".withFunctions").each(function(){
        $tr = $(this);
        $tr.addClass('withFunctions');

        //$tr.find('.contentSection').each(function(){
        // Mark the words in yellow
        $.each(words, function (index, value) {
            $tr.find(".text:contains(" + value + ")").html(function (_, html) {
                var regex = new RegExp(value, 'g');
                return html.replace(regex, '<mark>' + value + '</mark>');
            });
        });

        // separate multi sentences in one document with <hr>
        $tr.find('.contentSection').each(function(){
            if($(this).next().attr('class')=='contentSection')
                $('<hr>').insertAfter( $(this) );
        })
        //})

        // auto play when open the video and auto pause when close the video
        $tr.find('.video-popup').on('toggle', function() {
           if ($(this).attr("open") == "open")
                $($(this).find("video")).get(0).play();
            else
                $($(this).find("video")).get(0).pause();
        })

        $tr.find('.video-close-icon').click(function() {
            // trigger ESC key press
            var e = jQuery.Event("keydown");
            e.which = 27; // # Some key code value
            $("body").trigger(e);
            
            //$tr.find('.video-popup').removeAttr("open");
        })

        $tr.find('.video-close-icon').click(function() {
            // trigger ESC key press
            var e = jQuery.Event("keydown");
            e.which = 27; // # Some key code value
            $("body").trigger(e);
            
            //$tr.find('.video-popup').removeAttr("open");
        })
        $tr.find('.timing').each(function(){
            time = $(this).text();
            formatedTime = getFormatedTime(time);
            
            $(this).text(formatedTime); 
        })
    })
}

addFunctionsToTr();

// if runs too many times can write instead -> $('tbody').one(
$('tbody').bind("DOMSubtreeModified",function(){
    addFunctionsToTr();
});
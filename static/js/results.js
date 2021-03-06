documentStatistics = {};

function makeMdbAdjustments () {
	const table = $('#dtBasicExample').DataTable({
		"columnDefs": [{ targets: 'unsortable', orderable: false }]});
	table.order( [0,'asc'] ).draw();
}

function getWatchingData () {
	const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('session_id', sessionId);
	formData.append('search_string', searchString);
	formData.append('search_operator', searchOperator);
    formData.append('document_url', documentStatistics['url'].split('#t=')[0]);
    formData.append('document_timing', documentStatistics['url'].split('#t=')[1]);
    formData.append('start_time', documentStatistics['startTime']);
    formData.append('stop_time', documentStatistics['stopTime']);

	return formData;
}

function sendWatchingData () {
	const formData = getWatchingData();

	$.ajax({
		url: '/watching_data',
		type: 'POST',
		dataType: 'json',
		data: formData,
		processData: false,
		cache: false,
		contentType: false,
	})
		.done(() => {
		})
		.fail((jqXhr) => {
			console.log(jqXhr.responseJSON);
			console.log('failed to send watching data');
		});
}

// open the information about the search popup when click on the question mark icon
$('.fa.fa-question-circle.search-area').on('click', () => {
	const text = `● &nbsp;הפרדה  בין ביטויים תעשה באמצעות מקש הרווח. <br>
				  ● &nbsp;יש להכניס לגרשיים ביטויים המכילים יותר ממילה אחת, (לדוגמא: "הצלב האדום").<br>
				  <span class="highlight">או</span> - חיפוש קבצים המכילים <b>לפחות אחד </b>מהביטויים.<br>
				  <span class="highlight">וגם</span> - חיפוש קבצים המכילים את <b>כל </b>הביטויים.`;
	Swal.fire({
		icon: 'question',
		title: 'חיפוש קבצים מהמאגר',
		html: text,
		confirmButtonText: 'הבנתי',
		showCloseButton: true,
	});
});

function addFunctionsToTr () {	
	$('tr').not('.withFunctions').each(function() {
		const $tr = $(this);

		// Mark the words in yellow
		const words = $.trim($('#searchBar').val()).split(' ');
		if (!words) words = searchString;
		$.each(words, (index, value) => {
			$tr.find(`.text:contains(${value})`).html((_, html) => {
				const regex = new RegExp(value, 'g');
				return html.replace(regex, `<mark> ${value} </mark>`);
			});
		});
		// separate multi sentences in one document with <hr>
		$tr.find('.contentSection').each(function() {
			if ($(this).next().attr('class') === 'contentSection') $('<hr>').insertAfter($(this));
		});

		// auto play when open the video and auto pause when close the video
		$tr.find('.video-popup').on('toggle', function() {
            documentStatistics["url"] = $(this).find('source')[0].src;			

			let nowTime = new Date();
				nowTime = nowTime.toISOString();
				//toLocaleString 

			if ($(this).attr('open') === 'open') {
                documentStatistics['startTime'] = nowTime;

				$($(this).find('video')).get(0).play();	
			} else {
                documentStatistics['stopTime'] = nowTime;
                sendWatchingData();

				$($(this).find('video')).get(0).pause();
			}
		});

		// close the file on close icon
		$tr.find('.video-close-icon').click(function() {
			const e = jQuery.Event('keydown');
			e.which = 27; // # ESC key code
			$('body').trigger(e);
		});

		// format the time
		$tr.find('.timing').each(function() {
			const time = $($(this)[0]).text();
			const formatedTime = getFormatedTime(time);

			$($(this)[0]).text(formatedTime);
		});
		
		$tr.addClass('withFunctions');
	});
}

// if runs too many times can write instead -> $('tbody').one(
$('tbody').bind('DOMSubtreeModified', () => {
	//();
});

runLoadingAnimation(); // animation until the page is loaded

$( document ).ready(function() {
	makeMdbAdjustments();
	addFunctionsToTr();

	stopLoadingAnimation();
});




/*
	setTimeout(function(){
	}, 3000);

function preparePage () {
	let myPromise = new Promise(
		(resolve, reject) => { 		
			makeMdbAdjustments();
			addFunctionsToTr();
			setSaortableColumns();
			resolve('prepared the page');
	});
	return myPromise;
}
preparePage()
.then((result) => { stopLoadingAnimation(); });
*/

//$('#dtBasicExample_info').css('display', 'none'); // a part of mdb tables that we dont need

	//$('.unsortable').removeClass('sorting sorting_asc sorting_desc');
	//$('.unsortable').removeAttr('aria-sort');


		//$('#dtBasicExample, #dtBasicExample-1, #dt-more-columns, #dt-less-columns').mdbEditor();
	//$('.dataTables_length').addClass('bs-select');

	/*$('#dtBasicExample, #dtBasicExample-1, #dt-more-columns, #dt-less-columns').mdbEditor({
		"ordering": false
	});*/

	//const data_table = $('#dtBasicExample').DataTable();
	//data_table.order( [0,'desc'] ).draw();
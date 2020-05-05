window.documentTruckList = {};

function makeMdbAdjustments () {
	$('#dtBasicExample_info').css('display', 'none'); // a part of mdb tables that we dont need
	$('#dtBasicExample, #dtBasicExample-1, #dt-more-columns, #dt-less-columns').mdbEditor();
	$('.dataTables_length').addClass('bs-select');
}
function setSaortableColumns () {
	$('.unsortable').removeClass('sorting sorting_asc sorting_desc');
	$('.unsortable').removeAttr('aria-sort');
}

function getWatchingDataFormFata () {
	const formData = new FormData();

	formData.append('search_string', searchString);
	formData.append('document_truck_list', JSON.stringify(window.documentTruckList));

	return formData;
}

function sendWatchingData () {
	const formData = getWatchingDataFormFata();

	$.ajax({
		url: '/watchingData',
		type: 'POST',
		dataType: 'json',
		data: formData,
		processData: false,
		cache: false,
		contentType: false,
	})
		.done(() => {
			console.log('sent watching data');
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

$('.th-sm').click(() => {
	$('.unsortable').removeClass('sorting sorting_asc sorting_desc');
	$('.unsortable').removeAttr('aria-sort');
});

function addFunctionsToTr () {
	$('tr').not('.withFunctions').each(() => {
		const $tr = $(this);
		$tr.addClass('withFunctions');

		// Mark the words in yellow
		const words = $.trim($('#searchBar').val()).split(' ');
		$.each(words, (index, value) => {
			$tr.find(`.text:contains(${value})`).html((_, html) => {
				const regex = new RegExp(value, 'g');
				return html.replace(regex, `<mark> ${value} </mark>`);
			});
		});

		// separate multi sentences in one document with <hr>
		$tr.find('.contentSection').each(() => {
			if ($(this).next().attr('class') === 'contentSection') $('<hr>').insertAfter($(this));
		});

		// auto play when open the video and auto pause when close the video
		$tr.find('.video-popup').on('toggle', () => {
			var attr;
			if ($(this).attr('open') === 'open') {
				attr = 'startTime';
				$($(this).find('video')).get(0).play();
			} else {
				attr = 'stopTime';
				$($(this).find('video')).get(0).pause();
			}

			const documentId = $(this).find('source')[0].src;
			const nowTime = new Date();
			window.documentTruckList[documentId][attr] = nowTime;
			sendWatchingData();
		});

		// close the file on close icon
		$tr.find('.video-close-icon').click(() => {
			const e = jQuery.Event('keydown');
			e.which = 27; // # ESC key code
			$('body').trigger(e);
		});

		// format the time
		$tr.find('.timing').each(() => {
			const time = $(this).text();
			const formatedTime = getFormatedTime(time);

			$(this).text(formatedTime);
		});
	});
}

// if runs too many times can write instead -> $('tbody').one(
$('tbody').bind('DOMSubtreeModified', () => {
	addFunctionsToTr();
});

$(window).on('load', () => {
	setTimeout(() => {
		stopLoadingAnimation();
	}, 3000);
});

runLoadingAnimation(); // animation until the page is loaded
addFunctionsToTr();
setSaortableColumns();
makeMdbAdjustments();

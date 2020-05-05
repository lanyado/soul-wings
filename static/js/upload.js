// ================== file input and drop area ======================
const $fileInput = $('.file-input');
const $droparea = $('.file-drop-area');

// highlight drag area
$fileInput.on('dragenter focus click', () => {
	$droparea.addClass('is-active');
});

// back to normal state
$fileInput.on('dragleave blur drop', () => {
	$droparea.removeClass('is-active');
});

// change inner text
$fileInput.on('change', () => {
	const $textContainer = $(this).prev();
	const fileName = $(this).val().split('\\').pop();
	$textContainer.text(fileName);
});

// ================== Text area ======================
function updateTextAreaCounter (charactersRemaining = window.MAX_CHARACTERS_LENGTH) {
	$('#characters-remaining').text(charactersRemaining);
	$('#maximum-characters').text(window.MAX_CHARACTERS_LENGTH); // the maximum character count SPAN
}

// respond to each keydown by incrementing or decrementing the current character count
$('textarea').keydown(() => {
	const characterCount = $(this).val().length;
	const charactersRemaining = window.MAX_CHARACTERS_LENGTH - characterCount;

	$('#characters-remaining').text(charactersRemaining); // the current character count
});

// text area characters count
function analizeTextArea () {
	// textarea maxlength
	window.MAX_CHARACTERS_LENGTH = 200;
	// using the default values
	updateTextAreaCounter();
	// make it not be possible to enter more characters then maxlength
	$('#the-textarea').attr('maxlength', window.MAX_CHARACTERS_LENGTH);
}

// ================== Tags ======================
$('#addTagBtn').click(() => {
	$('#tags option:selected').each(() => {
		$(this).appendTo($('#selectedTags'));
	});
});

$('#removeTagBtn').click(() => {
	$('#selectedTags option:selected').each((element) => {
		$(element).appendTo($('#tags'));
	});
});

$('.tagRemove').click((event) => {
	event.preventDefault();
	$(this).parent().remove();
});

$('ul.tags').click(() => {
	$('#search-field').focus();
});

$('#search-field').keyup((e) => {
	if (e.keyCode === 13) {
		if ($('.addedTag').length < 10) {
			if (($(this).val() !== '') && ($(`.tags .addedTag:contains('${$(this).val()}')`).length === 0)) {
				const element = `<li class="addedTag"> ${$(this).val()} <span class="tagRemove" onclick="$(this).parent().remove();">x</span><input type="hidden" value=" ${$(this).val()} " name="tags[]"></li>`;
				$(element).insertBefore('.tags .tagAdd');
				$(this).val('');
			} else $(this).val('');
		} else errorAlert(true, 'ישנה הגבלה של 10 תגיות לקובץ');
	}
});

// ================== Upload the file ======================
function runProgressBar () {
	Swal.fire({
		title: 'מעלה את הקובץ למערכת',
		html: 'עד כה הועלה <b></b> מהקובץ',
		allowOutsideClick: false,
		onBeforeOpen: () => {
			Swal.showLoading();
			setInterval(() => {
				const content = Swal.getContent();
				if (content) {
					const b = content.querySelector('b');
					if (b) {
						if (window.precents < 100) b.textContent = `${window.precents.toString()}%`;
					}
				}
			}, 100);
		},
	});
}

function getUploadDict () {
	const theFile = $('#theFile').prop('files')[0];
	const fileName = $('#file_name').val();
	const fileDescription = $('#file_description').val();

	let language;
	const languages = ['hebrew', 'english'];
	for (const lang of languages) {
		if ($(`#${lang}`).hasClass('active')) language = lang;
	}

	const tags = [];
	$('.addedTag').each(() => {
		tags.push($(this).text().slice(0, -1));
	});

	const uploadDict = {
		theFile,
		fileName,
		fileDescription,
		language,
		tags,
	};

	return uploadDict;
}

function isUploadDictValid (uploadDict) {
	const MAX_FILE_SIZE = 2000000000; // 1 Giga
	const ALLOWED_FILE_EXTENSIONS = ['mp4', 'mp3'];

	var fileSize;
	var fileExtension;

	try {
		fileSize = uploadDict.theFile.size;
		fileExtension = $('#theFile').val().split('.').pop()
			.toLowerCase();
	} catch (err) {
		errorAlert(true, 'יש לצרף קובץ');
		return false;
	}

	if (fileSize > MAX_FILE_SIZE) {
		errorAlert(false, 'גודל הקובץ המקסימלי הוא 1 גיגה');
		return false;
	}

	if ($.inArray(fileExtension, ALLOWED_FILE_EXTENSIONS) === -1) {
		errorAlert(false, `סוגי הקבצים האפשריים להעלאה הם: ${ALLOWED_FILE_EXTENSIONS.join(', ')}`);
		return false;
	}

	return true;
}

function uploadDictToFormData () {
	const formData = new FormData();

	formData.append('file', uploadDict.theFile);
	formData.append('file_name', uploadDict.fileName);
	formData.append('file_description', uploadDict.fileDescription);
	formData.append('language', uploadDict.language);

	for (const tag of uploadDict.tags) {
		formData.append('tags', tag);
	}

	return formData;
}

function uploadFileRequest (formData) {
	$.ajax({
		url: '/uploader',
		type: 'POST',
		dataType: 'json',
		data: formData,
		processData: false,
		cache: false,
		contentType: false,

		xhr: () => {
			const xhr = $.ajaxSettings.xhr();
			xhr.upload.onprogress = (e) => {
				if (e.lengthComputable) {
					const precents = parseInt(((e.loaded / e.total) * 100), 10);
					if (precents < 1) {
						runProgressBar();
					}
				}
			};
			return xhr;
		},
	})
		.done((response) => {
			Swal.close(); // close the progress bar
			if (response.upload_successful) {
				sendSecsuss('הקובץ הועלה בהצלחה, אנחנו עכשיו מתחילים לנתח אותו, בעוד מספר דקות הוא יהיה זמין לחיפוש');
				$('.upload-details').removeAttr('open');
				$('#uploadForm').trigger('reset');
				$('#done').attr('disabled', 'disabled');
				$('#uploadPopup').scrollTop(0);
			}
		})
		.fail((jqXhr) => {
			Swal.close(); // close the progress bar
			console.log(jqXhr.responseJSON);
			errorAlert(false, 'נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר');
		});
}
// ================== general things ======================
//  make the submit button not disable when the user fill all the required fields
$('input').on('change keydown', () => {
	const theFile = $('#theFile').prop('files')[0];
	const fileName = $('#file_name').val();

	if (theFile && fileName) $('#done').removeAttr('disabled');
});

// the submit function that uploads the file
$('#done').click(() => {
	const uploadDict = getUploadDict();

	if (isUploadDictValid(uploadDict)) {
		console.log(uploadDict);
		const formData = uploadDictToFormData(uploadDict);
		uploadFileRequest(formData);
	}
});

// the colse icon
$('#upload-close-icon').click(() => {
	Swal.fire({
		title: 'התחרטת?',
		text: 'אם נפסיק את תהליך העלאת הקובץ, הנתונים לא יישמרו ונצטרך להתחיל מחדש את ההעלאה.',
		icon: 'warning',
		showCancelButton: true,
		confirmButtonColor: '#3085d6',
		cancelButtonColor: '#d33',
		confirmButtonText: 'רוצה להמשיך',
		cancelButtonText: 'רוצה לסגור',
		allowOutsideClick: false,
	}).then((result) => {
		if (!result.value) {
			$('.upload-details').removeAttr('open');
			$('#uploadForm').trigger('reset');
		}
	});
});

// start to tooltips when hover on the question marks
$('[data-toggle="tooltip"]').tooltip();

analizeTextArea();

// choose the hebrew language as default
$($('.btn.btn-outline-primary')[0]).click();

$.expr[':'].contains = $.expr.createPseudo((arg) => (elem) => $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0);

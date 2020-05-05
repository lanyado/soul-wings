/* eslint-disable no-unused-vars */
(() => {
	$('.cs-loader').css('display', 'none');
})();

// close all the popups exept the upload popup, when click on esc keyboard button
$(document).keyup((e) => {
	if (e.keyCode === 27) {
		$('details').not($('.upload-details')).removeAttr('open');
	}
});

function errorAlert (isUserFault = false, text) {
	let title;
	if (isUserFault) title = 'סליחה';
	else title = 'מצטערים';

	Swal.fire({
		icon: 'error',
		title,
		text,
		confirmButtonText: 'הבנתי',
		showCloseButton: true,
	});
}

function secsussAlert (text) {
	const titles = ['מעולה!', 'מצויין!'];
	const title = titles[Math.floor(Math.random() * titles.length)];

	Swal.fire({
		icon: 'success',
		title,
		text,
		confirmButtonText: 'הבנתי',
		showCloseButton: true,
	});
}

function runLoadingAnimation () {
	$('.cs-loader').css('display', 'block');
	$('body').css('overflow-y', 'hidden');
}

function stopLoadingAnimation () {
	$('.cs-loader').css('display', 'none');
	$('body').css('overflow-y', 'auto');
}

function getFormatedTime (time) {
	let minutes = String(parseInt(time / 60, 10));
	let seconds = String(parseInt(time % 60, 10));
	if (minutes < 10) minutes = `0${minutes}`;
	if (seconds < 10) seconds = `0${seconds}`;

	return `${minutes}:${seconds}`;
}

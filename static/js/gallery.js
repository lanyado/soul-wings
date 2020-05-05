// add the duration ton each video
$('video').one('loadedmetadata', () => {
	const { duration } = this;
	const formatedDuration = getFormatedTime(duration);
	const durationTag = $(this).closest('.popup').find('.duration')[0];
	$(durationTag).text(formatedDuration);
});

/* when the user clicks on the closing button it triggers ESC key press,
in order to close the video box */
$('.video-close-icon').on('click', () => {
	const e = jQuery.Event('keydown');
	e.which = 27; // # Some key code value
	$('body').trigger(e);
});

$('.popup').on('toggle', () => {
	if ($(this).attr('open') === 'open') {
		$($(this).find('video')).get(0).play();
	} else {
		$($(this).find('video')).get(0).pause();
	}
});

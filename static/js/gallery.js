// add the duration ton each video
$('video').one('loadedmetadata',function() {
	duration = this.duration;
	formatedDuration = getFormatedTime(duration);
	
	durationTag = $(this).closest('.popup').find('.duration')[0];
	$(durationTag).text(formatedDuration); 
})

$('.video-close-icon').on('click', function(){
    // trigger ESC key press, in order to close the video box	
    var e = jQuery.Event("keydown");
    e.which = 27; // # Some key code value
    $("body").trigger(e);
})
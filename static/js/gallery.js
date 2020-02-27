// add the duration ton each video
$('video').one('loadedmetadata',function() {
	var duration = this.duration;
	var formatedDuration = getFormatedTime(duration);
	
	var durationTag = $(this).closest('.popup').find('.duration')[0];
	$(durationTag).text(formatedDuration); 
})

// when the user clicks on the closing button it triggers ESC key press,
// in order to close the video box	
$('.video-close-icon').on('click', function(){
    var e = jQuery.Event("keydown");
    e.which = 27; // # Some key code value
    $("body").trigger(e);
})
// add the duration ton each video
$('video').one('loadedmetadata',function() {
	duration = this.duration;
	var minutes = String(parseInt(duration / 60, 10));
	var seconds = String(parseInt(duration % 60, 10));
	
	if (minutes<10)
		minutes = '0'+minutes;
	if (seconds<10)
		seconds = '0'+seconds;

	durationTag = $(this).closest('.popup').find('.duration')[0];
	$(durationTag).text(minutes+":"+seconds); 
})
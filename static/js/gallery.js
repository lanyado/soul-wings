$('video').one('loadedmetadata',function() {
	duration = this.duration;
	var minutes = String(parseInt(duration / 60, 10));
	var seconds = String(parseInt(duration % 60, 10));

	durationTag = $(this).closest('.popup').find('.duration')[0];
	$(durationTag).text(minutes+":"+seconds); 
})
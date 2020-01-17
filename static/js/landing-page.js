function login(){
	userName = $('#login-username').val();
	pass = $('#login-password').val();
	if (userName && pass){
		runLoadingAnimation();
		$.post('/login',{
			user_name: userName,
	    	password: pass
			},function(response){
				stopLoadingAnimation();
		        if (response.auth==false)
		        	sendError(false,'פרטי ההתחברות שגויים, נסו שוב')
				else{
					document.cookie = "soulwings" + "=" + (response.user_token || "") + "; path=/";
					window.location.href = response.redirect_url
				}
    		})
	}
	else
		sendError(true,'יש למלא שם משתמש וסיסמא')
}

$('input').keyup(function(e){
    if(e.keyCode == 13)
        $("#login").click();
});

$("#login").on('click', function(){
    login();
});

$(window).scroll(function() {
   if($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
	setTimeout(function(){ 
		$('details').prop('open', true);
	 }, 5000);
	}
});


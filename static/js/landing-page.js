function login(){
	var userName = $('#login-username').val();
	var pass = $('#login-password').val();
	if (userName && pass){
		runLoadingAnimation();
		$.post('/login',{
			user_name: userName,
	    	password: pass
			},function(response){
				stopLoadingAnimation();
		        if (response.auth){
		        	document.cookie = "soulwings" + "=" + (response.user_token || "") + "; path=/";
					window.location.href = response.redirect_url
		        }
				else
					sendError(false,'פרטי ההתחברות שגויים, נסו שוב')
    		})
	}
	else
		sendError(true,'יש למלא שם משתמש וסיסמא')
}

$("#login").on('click', function(){
    login();
});

// let the user to login on enter key press
$('input').keyup(function(e){
    if(e.keyCode == 13)
       login();
});

// 5 seconds after the user reaches the bottom of the page, he gets a login popup
$(window).scroll(function() {
   if($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
	setTimeout(function(){ 
		$('details').prop('open', true);
	 }, 5000);
	}
});
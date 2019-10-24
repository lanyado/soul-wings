/*================ login ====================*/
function login(){
	userName = $('#login-username').val();
	pass = $('#login-password').val();
	if (userName && pass){
		$('.cs-loader').css('display','block');
		$.post('/login',{
			user_name: userName,
	    	password: pass
	    	},function(response){
	    		$('.cs-loader').css('display','none');
		        if (!(response.auth)){
					Swal.fire({
						type: 'error',
						title: 'שגיאה',
						text: 'פרטי ההתחברות שגויים',
						confirmButtonText: 'המשך',
					})
		        }
    		})
	}
	else{
		Swal.fire({
			type: 'error',
			title: 'שגיאה',
			text: 'יש למלא שם משתמש וסיסמא',
			confirmButtonText: 'המשך',
		})
	}
}

$('input').keyup(function(e){
    if(e.keyCode == 13)
        $("#login").click();
});
$("#login").on('click', function(){
    login();
});
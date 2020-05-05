function sendLoginRequest (loginDict) {
	$.post('/login', loginDict, (response) => {
		if (response.auth) {
			// add the token we got from the server into a cookie
			document.cookie = `soulwings=${response.user_token || ''}; path=/`;
			// open the result page
			window.location.href = response.redirect_url;
		} else {
			stopLoadingAnimation();
			errorAlert(false, 'פרטי ההתחברות שגויים, נסו שוב');
		}
	});
}

function getLloginAttributes () {
	const userName = $('#login-username').val();
	const password = $('#login-password').val();

	return { userName, password };
}

function login () {
	const { userName, password } = getLloginAttributes();
	const loginDict = {
		user_name: userName,
		password,
	};

	if (userName && password) {
		runLoadingAnimation();
		sendLoginRequest(loginDict);
	} else {
		errorAlert(true, 'יש למלא שם משתמש וסיסמא');
	}
}

$('#login').on('click', () => { // login button
	login();
});

// let the user to login on enter key press
$('input').keyup((e) => {
	if (e.keyCode === 13) login();
});

// 5 seconds after the user reaches the bottom of the page, he gets a login popup
$(window).scroll(() => {
	if ($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
		setTimeout(() => {
			$('details').prop('open', true);
		}, 5000);
	}
});

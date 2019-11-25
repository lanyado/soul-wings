$(document).ready(function(){
    $(document).bind('keydown', function(e) { 
        if (e.which == 27) {
            $('details').removeAttr("open"); 
        }
    }); 
});

function sendError(isUserFault, text){
    var title;
    if (isUserFault)
        title = 'אופס';
    else
        title = 'מצטערים';

    Swal.fire({
        type: 'error',
        title: title,
        text: text,
        confirmButtonText: 'הבנתי',
    })
}

function sendSecsuss(text){
    var titles = ['מעולה!', 'מצויין!']
    var title = titles[Math.floor(Math.random()*titles.length)];

    Swal.fire({
        type: 'success',
        title: title,
        text: text,
        confirmButtonText: 'הבנתי',
    })
}
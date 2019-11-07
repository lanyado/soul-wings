$($('.btn.btn-outline-primary')[0]).click()


$.expr[":"].contains = $.expr.createPseudo(function(arg) {
    return function( elem ) {
        return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
});

$(document).ready(function() {
    $('#addTagBtn').click(function() {
        $('#tags option:selected').each(function() {
            $(this).appendTo($('#selectedTags'));
        });
    });
    $('#removeTagBtn').click(function() {
        $('#selectedTags option:selected').each(function(el) {
            $(this).appendTo($('#tags'));
        });
    });
    $('.tagRemove').click(function(event) {
        event.preventDefault();
        $(this).parent().remove();
    });
    $('ul.tags').click(function() {
        $('#search-field').focus();
    });
    $('#search-field').keypress(function(event) {
        if (event.which == '13') {
            if (($(this).val() != '') && ($(".tags .addedTag:contains('" + $(this).val() + "') ").length == 0 ))  {



                    $('<li class="addedTag">' + $(this).val() + '<span class="tagRemove" onclick="$(this).parent().remove();">x</span><input type="hidden" value="' + $(this).val() + '" name="tags[]"></li>').insertBefore('.tags .tagAdd');
                    $(this).val('');

            } else {
                $(this).val('');

            }
        }
    });
});


$('#done').click(function() {

    var theFile = $('#theFile').prop('files');
    var file_name = $('#file_name').val()
    var uploader_name = $('#uploader_name').val()
    
    var language;
    //langChoose
    if ($($('.btn.btn-outline-primary')[0]).is(':focus'))
        language = 'hebrew';
    else if ($($('.btn.btn-outline-warning')[0]).is(':focus'))
        language = 'english'

    var tags = []
    $('.addedTag').each(function(){
      tags.push($(this).text());
    })

    if (!theFile || !file_name || !uploader_name || !language){
        Swal.fire({
                    type: 'error',
                    title: 'שגיאה',
                    text: 'יש למלא את כל שדות החובה',
                    confirmButtonText: 'המשך',
                })
    }

    else{
        console.log(theFile, file_name, uploader_name,language,tags);

        $.post('/uploader',{
            file: theFile,
            file_name: file_name,
            uploader_name: uploader_name,
            language: language,
            tags: tags
        },function(response){
        })
    }


})
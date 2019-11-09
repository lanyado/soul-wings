function error(isUserFault, text){
    var title;
    if (isUserFault)
        title = 'אופס';
    else
        title = 'מצטערים';

    Swal.fire({
        type: 'error',
        title: title,
        text: text,
        confirmButtonText: 'המשך',
    })
}

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

    var maxFileSize = 1000000000; // 1 Giga
    var allowedFileExtension = ['mp4', 'mp3'];
   
    var theFile = $('#theFile').prop('files')[0];
    try {
        var fileSize = theFile.size;
        var fileExtension = $('#theFile').val().split('.').pop().toLowerCase();
    }
    catch(err) {
        console.log('error')
    }

    var file_name = $('#file_name').val()
    var uploader_name = $('#uploader_name').val()

    var language;
    //langChoose
    if ($('#hebrew').hasClass('active'))
        language = 'hebrew';
    else if ($('#english').hasClass('active'))
        language = 'english';

    var tags = []
    $('.addedTag').each(function(){
      tags.push($(this).text());
    })

    if (!theFile || !file_name || !uploader_name || !language)
        error(true, 'יש למלא את כל שדות החובה')
    
    else if (fileSize > maxFileSize)
        error(false, 'גודל הקובץ המקסימלי הוא 1 גיגה');

    else if ($.inArray(fileExtension, allowedFileExtension) == -1)
        error(false, 'סוגי הקבצים האפשריים להעלאה הם: '+allowedFileExtension.join(', '));
    
    else{
        console.log(theFile, file_name, uploader_name, language, tags);

        var newUpload = new Object();
        newUpload.file = theFile;
        newUpload.file_name = file_name;
        newUpload.uploader_name = uploader_name;
        newUpload.language = language;
        newUpload.tags = tags;
       
        $.ajax({
            url: '/uploader',
            type: 'POST',
            dataType: 'json',
            processData: false,
            data: newUpload
        },function(response){
        })
    }
})

/*=============*/
var $fileInput = $('.file-input');
var $droparea = $('.file-drop-area');

// highlight drag area
$fileInput.on('dragenter focus click', function() {
  $droparea.addClass('is-active');
});

// back to normal state
$fileInput.on('dragleave blur drop', function() {
  $droparea.removeClass('is-active');
});

// change inner text
$fileInput.on('change', function() {
    var filesCount = $(this)[0].files.length;
    var $textContainer = $(this).prev();
    var fileName = $(this).val().split('\\').pop();
    $textContainer.text(fileName);
 
});
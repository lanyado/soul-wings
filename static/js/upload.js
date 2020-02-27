$(document).ready(function() {
  // start to tooltips when hover on the question marks
  $('[data-toggle="tooltip"]').tooltip()

  // === file input
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

  // === choose the hebrew language as default
  $($('.btn.btn-outline-primary')[0]).click()

  $.expr[":"].contains = $.expr.createPseudo(function(arg) {
      return function( elem ) {
          return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
      };
  });

  // text area characters count
  var myMaxLength = 200, // textarea maxlength, set it to whatever you want
    myAlertTheshold = 95, // the threshold where the ARIA alert will start firing, don't set it too low
    maximum = $('#maximum'), // the maximum character count SPAN
    characterCounter = $('#characterCounter'); //the current character count

  /* initialise the character count area */
  $('#the-textarea').attr('maxlength', myMaxLength);
  $('#characterCounter').text(myMaxLength);
  $('#characterCounterDetails').text(myMaxLength);
  $('#maximum').text(myMaxLength);

   // respond to each keydown by incrementing or decrementing the current character count 
  $('textarea').keydown(function() {

    var characterCount = $(this).val().length,
      charactersRemaining = 0;

    charactersRemaining = myMaxLength - characterCount;
    characterCounter.text(charactersRemaining);
    /* once characters entered reaches the predefined threshold, create a new aria-alert 
        element so the screen reader receives the alert */

    /* creates the new element for each character up to the final one, so an alert happens for each keypress */

    if (characterCount > myAlertTheshold) {
      var newAlert = document.createElement("div"); /* using the native js because it's faster */
      newAlert.setAttribute("role", "alert");
      newAlert.setAttribute("id", "alert");
      newAlert.setAttribute("class", "sr-only");
      var msg = document.createTextNode('You have ' + charactersRemaining + ' characters of ' + myMaxLength + ' left');
      newAlert.appendChild(msg);
      document.body.appendChild(newAlert);
    }
  });

  //  === tags
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

          if ($('.addedTag').length < 10){
              if (($(this).val() != '') && ($(".tags .addedTag:contains('" + $(this).val() + "') ").length == 0 ))  {
                  $('<li class="addedTag">' + $(this).val() + '<span class="tagRemove" onclick="$(this).parent().remove();">x</span><input type="hidden" value="' + $(this).val() + '" name="tags[]"></li>').insertBefore('.tags .tagAdd');
                  $(this).val('');
              } else {
                  $(this).val('');
              }
          }
          else
              sendError(true, 'ישנה הגבלה של 10 תגיות לקובץ')
      }
  });
  
  //  === make the submit button not disable when the user fill all the required fields
  $('input').on('change keydown', function() {
      var theFile = $('#theFile').prop('files')[0];
      var file_name = $('#file_name').val()

      if (theFile && file_name)
          $('#done').removeAttr('disabled')
  })

  // === the submit function that uploads the file
  $('#done').click(function() {

      var maxFileSize = 2000000000; // 1 Giga
      var allowedFileExtension = ['mp4', 'mp3'];
     
      var theFile = $('#theFile').prop('files')[0];
      try {
          var fileSize = theFile.size;
          var fileExtension = $('#theFile').val().split('.').pop().toLowerCase();
      }
      catch(err) {
          sendError(true, 'יש לצרף קובץ');
      }

      var file_name = $('#file_name').val()
      var file_description = $('#file_description').val()

      var language;
      //set a language
      if ($('#hebrew').hasClass('active'))
          language = 'hebrew';
      else if ($('#english').hasClass('active'))
          language = 'english';

      var tags = []
      $('.addedTag').each(function(){
        tags.push($(this).text().slice(0,-1));
      })

      if (fileSize > maxFileSize)
          sendError(false, 'גודל הקובץ המקסימלי הוא 1 גיגה');

      else if ($.inArray(fileExtension, allowedFileExtension) == -1 && 1!=1)
          sendError(false, 'סוגי הקבצים האפשריים להעלאה הם: '+allowedFileExtension.join(', '));
      
      else{
          console.log(theFile, file_name, file_description, language, tags);
          
          var form_data = new FormData();
          
          form_data.append('file', theFile)
          form_data.append('file_name', file_name)
          form_data.append('file_description', file_description)
          form_data.append('language', language)

          for (var i = 0; i < tags.length; i++) {
              form_data.append('tags', tags[i]);
          }
          
          $.ajax({
              url: '/uploader',
              type: 'POST',
              dataType: 'json',
              data: form_data,
              processData: false,
              cache: false,
              contentType: false,
     
              xhr: function () {
                  var xhr = $.ajaxSettings.xhr();
                  xhr.upload.onprogress = function (e) {
                      // For uploads

                      if (e.lengthComputable) {

                       window.precents = (parseInt((e.loaded / e.total)*100));
                        if (precents < 1){
                            runProgressBar()
                        }
                      }
                  };
                  return xhr;          
              }
          })
          .done((response) => {
              Swal.close() // close the progress bar
              if (response.upload_successful){
                  sendSecsuss('הקובץ הועלה בהצלחה, אנחנו עכשיו מתחילים לנתח אותו, בעוד מספר דקות הוא יהיה זמין לחיפוש');
                  $('.upload-details').removeAttr("open");
                  $('#uploadForm').trigger("reset");
                  $('#done').attr('disabled', 'disabled');
                  $('#uploadPopup').scrollTop(0);  
              }
          })
          .fail((jqXhr) => {
              Swal.close() // close the progress bar
              console.log(jqXhr.responseJSON)
              sendError(false,'נראה שיש בעיית תקשורת, כדאי לנסות שוב בעוד זמן קצר');              //on success code here
        });
      }
  })

function runProgressBar(){
  let timerInterval

  Swal.fire({
    title: 'מעלה את הקובץ למערכת',
    html: 'עד כה הועלה <b></b> מהקובץ',
    allowOutsideClick: false,
    onBeforeOpen: () => {
      Swal.showLoading()
      setInterval(() => {
        const content = Swal.getContent()
        if (content) {
          const b = content.querySelector('b')
          if (b) {
            if (window.precents<100)
              b.textContent = window.precents.toString() + '%'
          }
        }
      }, 100)
    }
  })
}

// === the colse icon
$('#upload-close-icon').click(function() {
      Swal.fire({
        title: 'התחרטת?',
        text: "אם נפסיק את תהליך העלאת הקובץ, הנתונים לא יישמרו ונצטרך להתחיל מחדש את ההעלאה.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'רוצה להמשיך',
        cancelButtonText: 'רוצה לסגור',
        allowOutsideClick: false
      }).then((result) => {
        if (!result.value) {
          $('.upload-details').removeAttr("open");
          $('#uploadForm').trigger("reset");
        }
      })
  })
})

// https://jsfiddle.net/hgnyjdz6/ => Check the user's upload speed
// ===================================================================
/*
function checkUploadSpeed( iterations, update ) {
    var average = 0,
        index = 0,
        timer = window.setInterval( check, 5000 ); //check every 5 seconds
    check();
    
    function check() {
        var xhr = new XMLHttpRequest(),
            url = '?cache=' + Math.floor( Math.random() * 10000 ), //prevent url cache
            data = getRandomString( 1 ), //1 meg POST size handled by all servers
            startTime,
            speed = 0;
        xhr.onreadystatechange = function ( event ) {
            if( xhr.readyState == 4 ) {
                speed = Math.round( 1024 / ( ( new Date() - startTime ) / 1000 ) );
                average == 0 
                    ? average = speed 
                    : average = Math.round( ( average + speed ) / 2 );
                update( speed, average );
                index++;
                if( index == iterations ) {
                    window.clearInterval( timer );
                };
            };
        };
        xhr.open( 'POST', url, true );
        startTime = new Date();
        xhr.send( data );
    };
    
    function getRandomString( sizeInMb ) {
        var chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789~!@#$%^&*()_+`-=[]\{}|;':,./<>?", //random data prevents gzip effect
            iterations = sizeInMb * 1024 * 1024, //get byte count
            result = '';
        for( var index = 0; index < iterations; index++ ) {
            result += chars.charAt( Math.floor( Math.random() * chars.length ) );
        };     
        return result;
    };
};

checkUploadSpeed( 5, function ( speed, average ) {
    window.averageUploadSpeed = average
} );

var fileSizeMB = fileSize/1000000;
var uploadSpeedMBS = window.averageUploadSpeed/1000;
var secondsToUpload = (fileSizeMB/uploadSpeedMBS)/60;
var minutesToUpload = Math.ceil(secondsToUpload)+3;
console.log(minutesToUpload);
*/
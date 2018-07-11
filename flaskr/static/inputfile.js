$(document).ready(function(){
        $('#file').change(function(e){
            var fileName = e.target.files[0].name;
            var extension = fileName.substr((fileName.lastIndexOf('.') +1));
            $('#fileLabel').text(fileName);
            $('#fileLabel').width(fileName.length * 9.3);
            
            if (extension == 'xml') {
                $('#fileLabel').css("background", "#07e500");
            }
            else {
                alert('File must have XML extension');
                $('#fileLabel').css("background", "#c42300");
            }
        });
    });

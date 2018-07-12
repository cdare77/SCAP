$(document).ready(function(){
        $('#file').change(function(e) {
            
            var validFiles = e.target.files.length;
            var i = validFiles;
            while (i--) {
                // iterate over files
                console.log(e.target.files[i].name)
                var extension = e.target.files[i].name.substr(e.target.files[i].name.lastIndexOf('.') +1);
                    
                // All files must be XML -- if a non XML file
                // is found, alert the user
                if (extension != 'xml') {
                    alert(e.target.files[i].name + ' does not have an XML extension - it will not be processed');
                    validFiles--;
                }
            } // end for loop
            
            console.log(e.target.files.length);
            
            // Update label based on number of remaining files
            if (validFiles == 0) {
                // no valid files
                $('#fileLabel').text("No files");
                $('#fileLabel').css("background", "#c42300"); // Red
                $('#fileLabel').width(145);
            }
            else if (validFiles == 1) {
                // one valid file -- display its name
                var fileName = e.target.files[0].name;
                var extension = fileName.substr((fileName.lastIndexOf('.') +1));
                $('#fileLabel').text(fileName);
                $('#fileLabel').width(fileName.length * 9.3);
                $('#fileLabel').css("background", "#07e500");

            }
            else {
                // multiple valid files
                $('#fileLabel').width(145);
                $('#fileLabel').css("background", "#07e500");
                $('#fileLabel').text(e.target.files.length + " files selected");
            } // end else
        });
    });

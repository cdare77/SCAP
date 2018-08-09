$('#endnode').on('change',function() {
    var isSelected = $(this).val();

    if (isSelected == "ontap_9_3" || isSelected == "ontap_9_4") {
        $("#IPAddr").show();
        $("#IPAddrlabel").show();
        $("#IPAddr").attr("required", "");
        
        $("#user").show();
        $("#userlabel").show();
        $("#user").attr("required", "");

        $("#password").show();
        $("#passwordlabel").show();
        $("#password").attr("required", "");

        $("#submitbutton").val("Connect");
    }
    else {
        $("#IPAddr").hide();
        $("#IPAddrlabel").hide();
        $("#IPAddr").removeAttr("required");

        $("#user").hide();
        $("#userlabel").hide();
        $("#user").removeAttr("required");

        $("#password").hide();
        $("#passwordlabel").hide();
        $("#password").removeAttr("required");

        $("#submitbutton").val("Continue");
    }
});

$('#processType').on('change',function(){
    var selection = $(this).val();
   
    if( $(this).val()==="parallel"){
        $("#coreFactorInput").show();
        $("#coreFactorLabel").show();
        $("#coreFactorInput").attr('required', '');
    }
    else{
        $("#coreFactorInput").hide();
        $("#coreFactorLabel").hide();
        $("#coreFactorInput").removeAttr('required');
    }  

});

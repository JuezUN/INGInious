

function register_user(){
    
    jQuery.ajax({
        method: "POST",
        data: getUserDataLTI(),
        success: () => {

        },
        error: () => {

        }
    });

}
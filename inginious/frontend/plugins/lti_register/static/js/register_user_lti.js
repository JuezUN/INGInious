function display_alert(){
    let alert_id = "#registration_lti_alert";
    let alert = $(alert_id);
    alert.show();
}

function hide_alert(){
    let alert_id = "#registration_lti_alert";
    let alert = $(alert_id);
    alert.hide();
}

function set_alert_message(message){
    let alert_id = "#registration_lti_alert";
    let alert = $(alert_id);
    alert.text(message);
}

function register_user(){
    
    jQuery.ajax({
        method: "POST",
        data: {
            "new_user": getUserDataLTI(),
        },
        success: function(result){
            console.log(result);
        }
    });

}
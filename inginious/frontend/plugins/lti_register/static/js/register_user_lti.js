function display_alert(){

    let alert_id = "#registration_lti_alert";
    let alert = $(alert_id);

    alert.show();
}

function hide_alert(){

    let alert_id = "#registration_lti_alert";
    let alert = $(alert_id);

    alert.hide();
    clear_list_messages();
}

function set_all_messages(result_messages){
    let alert_id = "#registration_lti_alert";
    let alert = $(alert_id);
    let status;
    let message;
    clear_list_messages();
    result_messages.forEach((element) => {
        status = element.status;
        message = element.message; 
        add_new_alert_satus(alert, status, message);
    });
    display_alert(alert);

    setTimeout(function (){
        hide_alert(alert);
    },1000000)
}

function add_new_alert_satus(alert, status, message){

    let status_element_template;
    let messages_list;

    if (status == "success"){
        status_element_template="<li>"+message+"</li>";

        messages_list = $("#success_messages");

        messages_list.show();

    }else if(status == "error"){
        status_element_template="<li>"+message+"</li>";

        messages_list = $("#error_messages"); 
        
        messages_list.show();
    }

    if(!messages_list.find("ul").length){
        
        messages_list.append("<ul></ul>");

        if(status_element_template != null){
            messages_list.append(status_element_template);
        }
    }else{
        if(status_element_template != null){
            messages_list.append(status_element_template);
        }
    }

}

function clear_messages(list_id){
    let success_messages_list = $(list_id);

    success_messages_list.children().remove();
    success_messages_list.hide();
}

function clear_list_messages(){

    clear_messages("#success_messages");
    clear_messages("#error_messages");
}

function register_user(){


    hide_alert();
    
    jQuery.ajax({
        method: "POST",
        data: {
            "new_user": getUserDataLTI(),
        }
    }).done(function(result){
        let result_messages = JSON.parse(result.replaceAll('\'','"'));
        set_all_messages(result_messages.all_messages);
    });
}
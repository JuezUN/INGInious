jQuery(document).ready(function () {
    const form = new Formulary();
    form.addChangeListenerToSelect();
    form.addChangeListenerToCheckbox();
    form.changeSelection();
    form.addClickListenerToSendButton();
});
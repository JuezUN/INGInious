function get_service_name_by_key(key) {
    return all_services[key];
}

function get_services_names(services = []) {
    return services.map(value => {
        return get_service_name_by_key(value);
    });
}

function generate_get_url_plot(path) {
    const request = [path];
    const parameters = [];
    if (analytics_username || analytics_service || analytics_duration_time)
        request.push("?");
    if (analytics_username)
        parameters.push('username=' + analytics_username);
    if (analytics_service)
        parameters.push('service=' + analytics_service);
    if (analytics_duration_time)
        parameters.push('time=' + analytics_duration_time);
    request.push(parameters.join('&'));
    return request.join('');
}

function on_search() {
    location.replace(location.pathname + "?");
}

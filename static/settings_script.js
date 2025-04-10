// settings_script.js specifically for the settings page
//created because the main file was too long

document.addEventListener('DOMContentLoaded', function() {
    const settingsForm = document.getElementById('settings-form');
    const currentFirstName = document.getElementById('current-first-name');
    const currentLastName = document.getElementById('current-last-name');

    // fet the current first name and last name of the account
    function fetchCurrentSettings() {
        fetch('/get_settings')
            .then(response => response.json())
            .then(data => {
                currentFirstName.textContent = data.first_name || 'N/A';
                currentLastName.textContent = data.last_name || 'N/A';
            })
            .catch(error => console.error('Error fetching settings:', error));
    }

    fetchCurrentSettings();
    //updates the settings with a new password if they change password
    settingsForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(settingsForm);
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');

        if (password || confirmPassword) { 
            if (password !== confirmPassword) {
                alert("Passwords do not match.");
                return;
            }
        }

        fetch('/update_settings', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Settings updated successfully!");
                fetchCurrentSettings(); 
            } else {
                alert("Error updating settings.");
            }
        })
        .catch(error => console.error('Error updating settings:', error));
    });
});
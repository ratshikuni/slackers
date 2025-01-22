function checkPasswordStrength(password) {
    // At least one lower case letter, one upper case letter, one digit, one special character, and at least 8 characters long
    var re = /^(?=.*\d)(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z]).{8,}$/;
    return re.test(password);
}

function validateForm() {
    var password = document.getElementById('password').value;
    if (!checkPasswordStrength(password)) {
        alert('Password must be at least 8 characters long, contain a lowercase letter, uppercase letter, a digit and a special character.');
        return false;
    }
    return true;
}
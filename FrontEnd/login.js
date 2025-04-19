async function handleLogin() {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    if (!username || !password) {
        alert("Both username and password are required!");
        return;
    }

    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    try {
        const response = await fetch("/db/login", {
            method: "POST",
            body: formData,
        });

        // // Use this for DEV
        // const response = await fetch("https://capstone1.cs.kent.edu/db/login", {
        //     method: "POST",
        //     body: formData,
        // });

        const result = await response.json();

        if (response.ok) {
            alert(result);
            set_profile_tab(2);
        } else {
            alert(result);
        }
    } catch (error) {
        console.error("Login error:", error);
    }
}

async function handleCreateAccount() {
    event.preventDefault();

    const username = document.getElementById("c_username").value;
    const password = document.getElementById("new-pass").value;
    const matchPass = document.getElementById("new-pass-rep").value;
    const email = document.getElementById("c_email").value;
    
    // Check that all fields are filled
    if (!username || !password || !email || !matchPass) {
        alert("All fields are required!");
        return;
    }

    // Check that password and matchPass match
    if(password != matchPass){
        alert ("Passwords must match!");
        return;
    }

    // Check for valid password
    if(!(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$/
        .test(password))){
            alert("Invalid password!");
            return;
    }

    // Check for valid email
    if(!(/^([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-z]{2,})$/
        .test(email))){
            alert("Invalid email!");
            return;
    }

    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);
    formData.append("email", email);

    try {
        const response = await fetch("/db/create_account", {
            method: "POST",
            body: formData,
        });

        // // Use this for DEV
        // const response = await fetch("https://capstone1.cs.kent.edu/db/create_account", {
        //     method: "POST",
        //     body: formData,
        // });

        const result = await response.json();

        if (response.ok) {
            alert(result);
            set_profile_tab(0);
        } else {
            alert(result);
        }
    } catch (error) {
        console.error("Account Creation error:", error);
    }
}
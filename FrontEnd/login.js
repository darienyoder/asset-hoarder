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
    if (!username || !password || !email) {
        alert("Email, Password, and Username are all required!");
        return;
    }
    if(password != matchPass){
        alert ("Passwords must match!");
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
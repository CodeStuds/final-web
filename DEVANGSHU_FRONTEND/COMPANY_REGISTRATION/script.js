// ======== COMPANY REGISTRATION WITH SUPABASE AUTH ========
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("companyForm");
    const togglePassword = document.getElementById("togglePassword");
    const passwordInput = document.getElementById("password");

    // Check if user is already logged in
    checkAuth().then(session => {
        if (session) {
            // Redirect to company main page if already authenticated
            window.location.href = "../COMPANY_MAIN_PAGE/index.html";
        }
    });

    // Password toggle functionality
    togglePassword.addEventListener("click", () => {
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
        passwordInput.setAttribute("type", type);
        togglePassword.textContent = type === "password" ? "👁️" : "🙈";
    });

    // Handle registration form submission
    form.addEventListener("submit", async function(event) {
        event.preventDefault();

        // Collect input values
        const companyData = {
            companyName: document.getElementById("companyName").value.trim(),
            email: document.getElementById("email").value.trim(),
            password: document.getElementById("password").value.trim(),
            goal: document.getElementById("goal").value.trim(),
            description: document.getElementById("description").value.trim()
        };

        // Basic client-side validation
        if (!companyData.companyName || !companyData.email || !companyData.password) {
            alert("Please fill all required fields.");
            return;
        }

        if (companyData.password.length < 6) {
            alert("Password must be at least 6 characters long.");
            return;
        }

        // Show loading state
        const submitButton = form.querySelector("button[type='submit']");
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = "Registering...";

        try {
            // Sign up with Supabase Auth
            const { data, error } = await supabase.auth.signUp({
                email: companyData.email,
                password: companyData.password,
                options: {
                    data: {
                        company_name: companyData.companyName,
                        company_goal: companyData.goal,
                        company_description: companyData.description,
                        user_type: 'company'
                    }
                }
            });

            if (error) {
                throw error;
            }

            if (data.user) {
                alert("✅ Registration successful! Welcome, " + companyData.companyName + "!");

                // Check if email confirmation is required
                if (data.session) {
                    // User is automatically logged in, redirect to main page
                    window.location.href = "../COMPANY_MAIN_PAGE/index.html";
                } else {
                    // Email confirmation required
                    alert("Please check your email to confirm your account before logging in.");
                    window.location.href = "../COMPANY_LOGIN/index.html";
                }
            }
        } catch (error) {
            console.error("Registration error:", error);

            // Handle specific error messages
            if (error.message.includes("already registered") || error.message.includes("already been registered")) {
                alert("❌ This email is already registered. Please use a different email or login.");
            } else if (error.message.includes("password")) {
                alert("❌ Password error: " + error.message);
            } else {
                alert("❌ Registration failed: " + (error.message || "Unknown error"));
            }
        } finally {
            // Reset button state
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    });
});

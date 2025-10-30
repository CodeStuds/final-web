// ======== COMPANY LOGIN WITH SUPABASE AUTH ========
document.addEventListener("DOMContentLoaded", () => {
    const passwordInput = document.getElementById("password");
    const togglePassword = document.getElementById("togglePassword");
    const loginForm = document.getElementById("loginForm");

    // Check if user is already logged in
    checkAuth().then(session => {
        if (session) {
            // Redirect to company main page if already authenticated
            window.location.href = "/company/dashboard";
        }
    });

    // Password toggle functionality
    togglePassword.addEventListener("click", () => {
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
        passwordInput.setAttribute("type", type);
        togglePassword.textContent = type === "password" ? "👁️" : "🙈";
    });

    // Handle login form submission
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = passwordInput.value.trim();

        // Basic client-side validation
        if (!email || !password) {
            alert("Please fill in all fields!");
            return;
        }

        // Show loading state
        const submitButton = loginForm.querySelector("button[type='submit']");
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = "Logging in...";

        try {
            // Sign in with Supabase Auth
            const { data, error } = await supabase.auth.signInWithPassword({
                email: email,
                password: password
            });

            if (error) {
                throw error;
            }

            if (data.session) {
                alert("✅ Login successful! Welcome back!");
                // Redirect to company dashboard
                window.location.href = "/company/dashboard";
            }
        } catch (error) {
            console.error("Login error:", error);

            // Handle specific error messages
            if (error.message.includes("Invalid login credentials")) {
                alert("❌ Invalid email or password. Please try again.");
            } else if (error.message.includes("Email not confirmed")) {
                alert("❌ Please confirm your email before logging in. Check your inbox.");
            } else {
                alert("❌ Login failed: " + (error.message || "Unknown error"));
            }
        } finally {
            // Reset button state
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    });
});

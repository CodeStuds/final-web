// ======== COMPANY LOGIN WITH SUPABASE AUTH ========
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");

  // Check if user is already logged in
  checkAuth().then(session => {
    if (session) {
      // Redirect to company main page if already authenticated
      window.location.href = "../COMPANY_MAIN_PAGE/index.html";
    }
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
      alert("Please enter both email and password.");
      return;
    }

    const button = form.querySelector("button");
    button.disabled = true;
    button.textContent = "Logging in...";

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
        alert("✅ Login successful! Welcome back.");
        // Redirect to company main page
        window.location.href = "../COMPANY_MAIN_PAGE/index.html";
      }
    } catch (error) {
      console.error("Login error:", error);

      // Handle specific error messages
      if (error.message.includes("Invalid login credentials")) {
        alert("❌ Invalid email or password. Please try again.");
      } else if (error.message.includes("Email not confirmed")) {
        alert("❌ Please confirm your email address before logging in. Check your inbox for the confirmation email.");
      } else {
        alert("❌ Login failed: " + (error.message || "Unknown error"));
      }
    } finally {
      button.disabled = false;
      button.textContent = "Login";
    }
  });
});

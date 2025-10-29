// ======== SUPABASE CONFIGURATION ========
// Shared Supabase client configuration for authentication
// IMPORTANT: Set these values in your environment or build configuration
// DO NOT commit actual credentials to version control

const SUPABASE_URL = window.ENV?.SUPABASE_URL || "YOUR_SUPABASE_URL_HERE";
const SUPABASE_ANON_KEY = window.ENV?.SUPABASE_ANON_KEY || "YOUR_SUPABASE_ANON_KEY_HERE";

// Initialize Supabase client
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Helper function to check if user is authenticated
async function checkAuth() {
  const { data: { session }, error } = await supabase.auth.getSession();
  if (error) {
    console.error("Error checking auth:", error);
    return null;
  }
  return session;
}

// Helper function to get current user
async function getCurrentUser() {
  const { data: { user }, error } = await supabase.auth.getUser();
  if (error) {
    console.error("Error getting user:", error);
    return null;
  }
  return user;
}

// Helper function to sign out
async function signOut() {
  const { error } = await supabase.auth.signOut();
  if (error) {
    console.error("Error signing out:", error);
    return false;
  }
  return true;
}

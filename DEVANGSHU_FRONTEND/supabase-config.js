// ======== SUPABASE CONFIGURATION ========
// Shared Supabase client configuration for authentication
// IMPORTANT: Replace SUPABASE_ANON_KEY with your actual key from Supabase dashboard
// Get it from: Supabase Dashboard > Project Settings > API > anon public key

const SUPABASE_URL = "https://laqedbvdwsbhsckcbskw.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxhcWVkYnZkd3NiaHNja2Nic2t3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE3NDYxODgsImV4cCI6MjA3NzMyMjE4OH0.5tqQguiDtIHB23bZC6y9LE1qZXRL-vDAT8wXZrfpsps";

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

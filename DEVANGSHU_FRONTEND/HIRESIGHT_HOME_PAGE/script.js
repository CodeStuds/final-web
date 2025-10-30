// Simple JavaScript to log responsive mode for debugging
window.addEventListener("resize", () => {
  const width = window.innerWidth;
  let mode = "Desktop";

  if (width < 800) mode = "Mobile";
  else if (width < 1280) mode = "Tablet";

  console.log(`Current layout: ${mode} (${width}px)`);
});

// Example API key holder (if needed for future backend integration)
const API_KEYS = {
  HIRE_BACKEND: "YOUR_API_KEY_HERE",
};
// Smooth scroll to Services section
const servicesBtn = document.getElementById('servicesBtn');
if (servicesBtn) {
	servicesBtn.addEventListener('click', () => {
		const services = document.getElementById('services');
		if (services) services.scrollIntoView({ behavior: 'smooth' });
	});
}

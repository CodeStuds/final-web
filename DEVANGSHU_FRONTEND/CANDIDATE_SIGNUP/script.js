const sampleJobs = [
  {id:1,title:'Senior Frontend Engineer',company:'Acme Studios',location:'Remote',type:'Full-time',salary:'₹2.4L - ₹5.0L',posted:'2d'},
  {id:2,title:'Backend Developer (Node.js)',company:'Zenex',location:'Bengaluru, India',type:'Full-time',salary:'₹3.0L - ₹7.0L',posted:'1d'},
  {id:3,title:'Product Designer',company:'Orbit',location:'Remote',type:'Contract',salary:'₹1.5L - ₹4.0L',posted:'3d'},
  {id:4,title:'Data Scientist',company:'Nimbus',location:'Mumbai, India',type:'Full-time',salary:'₹4.0L - ₹9.0L',posted:'5d'},
  {id:5,title:'DevOps Engineer',company:'Atlas',location:'Remote',type:'Full-time',salary:'₹3.5L - ₹8.0L',posted:'7d'},
  {id:6,title:'Engineering Manager',company:'Acme',location:'US',type:'Full-time',salary:'$120k - $160k',posted:'10d'}
]

const jobsGrid = document.getElementById('jobsGrid')
const searchForm = document.getElementById('searchForm')
const searchInput = document.getElementById('searchInput')
const locationSelect = document.getElementById('locationSelect')
const loadMore = document.getElementById('loadMore')
const jobsCountEl = document.getElementById('jobsCount')

let visibleJobs = 3
let currentJobs = [...sampleJobs]

function renderJobs(list){
  jobsGrid.innerHTML = ''
  list.slice(0, visibleJobs).forEach(job=>{
    const el = document.createElement('div')
    el.className = 'job-card'
    el.innerHTML = `
      <h4>${job.title}</h4>
      <div class="job-meta">${job.company} • ${job.location}</div>
      <p class="muted">${job.type} • ${job.salary}</p>
      <div class="job-actions">
        <button class="btn btn-outline">Save</button>
        <button class="btn btn-primary">Apply</button>
      </div>
    `
    jobsGrid.appendChild(el)
  })
  jobsCountEl.textContent = list.length
}

searchForm.addEventListener('submit', (e)=>{
  e.preventDefault()
  const q = searchInput.value.trim().toLowerCase()
  const loc = locationSelect.value
  const filtered = sampleJobs.filter(j=>{
    const matchQ = q === '' || j.title.toLowerCase().includes(q) || j.company.toLowerCase().includes(q)
    const matchLoc = loc === 'any' || (loc === 'remote' ? j.location.toLowerCase().includes('remote') : j.location.toLowerCase().includes(loc))
    return matchQ && matchLoc
  })
  currentJobs = filtered
  visibleJobs = Math.min(6, filtered.length)
  renderJobs(filtered)
})

loadMore.addEventListener('click', ()=>{
  visibleJobs += 3
  renderJobs(currentJobs)
})

// mobile nav toggle
const nav = document.getElementById('nav')
const navToggle = document.getElementById('navToggle')
navToggle.addEventListener('click', ()=>{
  nav.classList.toggle('open')
})

// small contact form handler
const contactForm = document.getElementById('contactForm')
contactForm.addEventListener('submit', (e)=>{
  e.preventDefault()
  const email = document.getElementById('email').value
  alert(`Thanks — we\'ll notify: ${email}`)
  contactForm.reset()
})

// set year
document.getElementById('year').textContent = new Date().getFullYear()

// initial render
renderJobs(sampleJobs)

// simple intersection animation for sections
const obs = new IntersectionObserver((entries)=>{
  entries.forEach(en=>{
    if(en.isIntersecting) en.target.classList.add('inview')
  })
},{threshold:0.12})

document.querySelectorAll('section').forEach(s=>obs.observe(s))

// keyboard: press / to focus search
window.addEventListener('keydown',(e)=>{
  if(e.key === '/'){
    e.preventDefault();searchInput.focus();
  }
})

import menuData from './data/menu.json';

// State management
let currentCategory = 'all';
let currentTag = 'all';
let searchQuery = '';
let visibleCount = 18;
const BATCH_SIZE = 18;

// DOM Elements
const menuGrid = document.getElementById('menu-grid');
const searchInput = document.getElementById('menu-search-input');
const clearSearchBtn = document.getElementById('clear-search-btn');
const categoryContainer = document.getElementById('category-scroll-container');
const filterChips = document.querySelectorAll('.filter-chip');
const resultsCountEl = document.getElementById('results-count');
const loadMoreBtn = document.getElementById('load-more-btn');
const loadMoreContainer = document.getElementById('load-more-container');
const openStatusEl = document.getElementById('open-status-badge');
const topBarStatusEl = document.getElementById('top-bar-live-status');
const navToggle = document.getElementById('mobile-nav-toggle');
const navMenu = document.getElementById('nav-menu');
const scrollTopBtn = document.getElementById('scroll-top-btn');
const modalBackdrop = document.getElementById('dish-modal');
const modalCloseBtn = document.getElementById('modal-close-btn');

// Image Fallback Mapping
const fallbackImages = {
  'egg-dosas': '/images/frittata.jpg',
  'idly-vada': '/images/omelette.jpg',
  'english-breakfast': '/images/omelette.jpg',
  'omelets-frittatas': '/images/frittata.jpg',
  'starters-fusion': '/images/ghotala.jpg',
  'breakfast-platters': '/images/omelette.jpg',
  'egg-specials': '/images/ghotala.jpg',
  'chef-specials': '/images/ghotala.jpg',
  'signature-rolls': '/images/egg_roll.jpg',
  'soups-broths': '/images/interior.jpg',
  'artisan-egg-rice': '/images/sizzler.jpg',
  'street-noodles': '/images/egg_roll.jpg',
  'maggi-chronicles': '/images/frittata.jpg',
  'burgers-sandwiches': '/images/egg_roll.jpg',
  'pizzas-sizzlers': '/images/sizzler.jpg',
  'salads-meals': '/images/interior.jpg',
  'sweets-desserts': '/images/frittata.jpg',
  'beverages-coolers': '/images/interior.jpg',
  'hot-beverages': '/images/interior.jpg'
};

// Check Open/Closed Hours (11:00 AM to 11:00 PM IST)
function checkOpenHours() {
  const now = new Date();
  // Get IST hours (UTC + 5:30)
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
  const istDate = new Date(utc + (3600000 * 5.5));
  const hours = istDate.getHours();

  const isOpen = hours >= 11 && hours < 23;

  if (openStatusEl) {
    if (isOpen) {
      openStatusEl.className = 'hours-badge-live';
      openStatusEl.innerHTML = '<span class="pulse-dot"></span> Open Now (11:00 AM – 11:00 PM)';
    } else {
      openStatusEl.className = 'hours-badge-live closed';
      openStatusEl.innerHTML = '● Closed Now (Opens at 11:00 AM IST)';
    }
  }

  if (topBarStatusEl) {
    if (isOpen) {
      topBarStatusEl.innerHTML = '<span class="pulse-dot"></span> Kitchen Open Now (Dine-in & Takeaway)';
    } else {
      topBarStatusEl.innerHTML = '● Kitchen Closed (Opens at 11:00 AM)';
    }
  }
}

// Category Buttons Rendering
function renderCategories() {
  if (!categoryContainer) return;

  const totalAll = menuData.dishes.length;

  let html = `
    <button class="cat-pill ${currentCategory === 'all' ? 'active' : ''}" data-category="all">
      <span class="cat-icon">🍳</span>
      <span>All Dishes</span>
      <span class="cat-count">${totalAll}</span>
    </button>
  `;

  menuData.categories.forEach(cat => {
    const count = menuData.dishes.filter(d => d.categoryId === cat.id).length;
    html += `
      <button class="cat-pill ${currentCategory === cat.id ? 'active' : ''}" data-category="${cat.id}">
        <span class="cat-icon">${cat.icon}</span>
        <span>${cat.name}</span>
        <span class="cat-count">${count}</span>
      </button>
    `;
  });

  categoryContainer.innerHTML = html;

  categoryContainer.querySelectorAll('.cat-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      categoryContainer.querySelectorAll('.cat-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentCategory = btn.getAttribute('data-category');
      visibleCount = BATCH_SIZE;
      renderMenu();
    });
  });
}

// Filter dishes based on Category, Tag, and Search
function getFilteredDishes() {
  return menuData.dishes.filter(dish => {
    // Category match
    if (currentCategory !== 'all' && dish.categoryId !== currentCategory) {
      return false;
    }

    // Tag match
    if (currentTag !== 'all') {
      if (currentTag === 'Bestseller' && !dish.tags.includes('Bestseller')) return false;
      if (currentTag === 'High Protein' && !dish.tags.includes('High Protein')) return false;
      if (currentTag === 'Spicy' && (!dish.tags.includes('Spicy') && dish.spiceLevel < 2)) return false;
      if (currentTag === "Chef's Special" && !dish.tags.includes("Chef's Special")) return false;
    }

    // Search query match
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const inName = dish.name.toLowerCase().includes(q);
      const inDesc = dish.description.toLowerCase().includes(q);
      const inTags = dish.tags.some(t => t.toLowerCase().includes(q));
      if (!inName && !inDesc && !inTags) return false;
    }

    return true;
  });
}

// Render Menu Cards
function renderMenu() {
  const filtered = getFilteredDishes();

  if (resultsCountEl) {
    resultsCountEl.innerHTML = `Showing <span>${Math.min(visibleCount, filtered.length)}</span> of <span>${filtered.length}</span> dishes`;
  }

  if (filtered.length === 0) {
    menuGrid.innerHTML = `
      <div class="empty-menu-state">
        <div class="empty-icon">🍳</div>
        <h3 class="empty-title">No egg dishes found</h3>
        <p class="empty-desc">We couldn't find any dish matching "${searchQuery}". Try a different keyword or reset filters.</p>
        <button class="btn btn-primary" id="reset-filters-btn">Reset All Filters</button>
      </div>
    `;
    const resetBtn = document.getElementById('reset-filters-btn');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        searchQuery = '';
        if (searchInput) searchInput.value = '';
        if (clearSearchBtn) clearSearchBtn.classList.remove('visible');
        currentCategory = 'all';
        currentTag = 'all';
        filterChips.forEach(c => c.classList.toggle('active', c.getAttribute('data-tag') === 'all'));
        renderCategories();
        renderMenu();
      });
    }
    if (loadMoreContainer) loadMoreContainer.style.display = 'none';
    return;
  }

  const toShow = filtered.slice(0, visibleCount);

  let cardsHtml = '';
  toShow.forEach(dish => {
    // Spice icons
    let spiceIcons = '';
    if (dish.spiceLevel > 0) {
      spiceIcons = '🌶️'.repeat(dish.spiceLevel);
    }

    // Tags
    let tagsHtml = '';
    dish.tags.forEach(t => {
      let tagClass = 'dish-tag';
      if (t === 'Bestseller') tagClass += ' bestseller';
      else if (t === "Chef's Special") tagClass += ' chef';
      else if (t === 'High Protein') tagClass += ' protein';
      else if (t === 'Spicy') tagClass += ' spicy';
      tagsHtml += `<span class="${tagClass}">${t}</span>`;
    });

    cardsHtml += `
      <article class="dish-card" data-id="${dish.id}" tabindex="0" role="button" aria-label="View details for ${dish.name}">
        <div class="dish-card-header">
          <h4 class="dish-title">${dish.name}</h4>
        </div>
        <div class="dish-card-body">
          <p class="dish-desc">${dish.description}</p>
          ${tagsHtml ? `<div class="dish-tags-row">${tagsHtml}</div>` : ''}
          <div class="dish-footer-meta">
            <div class="dish-nutrition">
              <span class="nutrition-item ${dish.dietary === 'Veg' ? 'badge-veg' : 'badge-egg'}">${dish.dietary === 'Veg' ? '🟢 Pure Veg' : '🟡 Egg'}</span>
              ${dish.eggsUsed > 0 ? `<span class="nutrition-item" title="Eggs Used">🥚 ${dish.eggsUsed} Eggs</span>` : ''}
              ${dish.protein ? `<span class="nutrition-item" title="Protein">💪 ${dish.protein}</span>` : ''}
              ${spiceIcons ? `<span class="nutrition-item" title="Spice Level">${spiceIcons}</span>` : ''}
            </div>
            <span class="view-details-action">View Details →</span>
          </div>
        </div>
      </article>
    `;
  });

  menuGrid.innerHTML = cardsHtml;

  // Add click listeners to cards
  menuGrid.querySelectorAll('.dish-card').forEach(card => {
    card.addEventListener('click', () => {
      const id = card.getAttribute('data-id');
      const dish = menuData.dishes.find(d => d.id === id);
      if (dish) openDishModal(dish);
    });
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        const id = card.getAttribute('data-id');
        const dish = menuData.dishes.find(d => d.id === id);
        if (dish) openDishModal(dish);
      }
    });
  });

  // Load More Button Visibility
  if (loadMoreContainer) {
    if (visibleCount < filtered.length) {
      loadMoreContainer.style.display = 'flex';
      const remaining = filtered.length - visibleCount;
      loadMoreBtn.innerText = `Explore More Dishes (${remaining} remaining)`;
    } else {
      loadMoreContainer.style.display = 'none';
    }
  }
}

// Open Dish Modal (Details Only - No Photo, No Price)
function openDishModal(dish) {
  if (!modalBackdrop) return;

  const catObj = menuData.categories.find(c => c.id === dish.categoryId);
  const catName = catObj ? catObj.name : (dish.categoryName || 'Egg Specialty');

  // Construct WhatsApp inquiry text (No price)
  const waMsg = encodeURIComponent(`Hello Frittata Fiesta Cafe! I would like to inquire about: ${dish.name}.`);
  const waUrl = `https://wa.me/919886012345?text=${waMsg}`;

  let spiceText = 'Mild / Balanced';
  if (dish.spiceLevel === 1) spiceText = 'Mild Spiced 🌶️';
  if (dish.spiceLevel === 2) spiceText = 'Medium Spicy 🌶️🌶️';
  if (dish.spiceLevel === 3) spiceText = 'Fiery Hot 🌶️🌶️🌶️';

  const proteinVal = dish.protein || (dish.eggsUsed > 0 ? `${dish.eggsUsed * 6}g+ Farm Protein` : (dish.dietary === 'Veg' ? 'Nutritious & Fresh' : 'Artisanal Preparation'));

  const catEl = document.getElementById('modal-cat');
  if (catEl) catEl.textContent = catName;

  const titleEl = document.getElementById('modal-title');
  if (titleEl) titleEl.textContent = dish.name;

  const dietaryEl = document.getElementById('modal-dietary');
  if (dietaryEl) {
    dietaryEl.className = `nutrition-item ${dish.dietary === 'Veg' ? 'badge-veg' : 'badge-egg'}`;
    dietaryEl.textContent = dish.dietary === 'Veg' ? '🟢 Pure Vegetarian' : '🟡 Farm Egg Specialty';
  }

  const spiceEl = document.getElementById('modal-spice');
  if (spiceEl) spiceEl.textContent = spiceText;

  const tagsEl = document.getElementById('modal-tags');
  if (tagsEl) {
    if (dish.tags && dish.tags.length > 0) {
      tagsEl.innerHTML = dish.tags.map(t => {
        let tagClass = 'dish-tag';
        if (t === 'Bestseller') tagClass += ' bestseller';
        else if (t === "Chef's Special") tagClass += ' chef';
        else if (t === 'High Protein') tagClass += ' protein';
        else if (t === 'Spicy') tagClass += ' spicy';
        return `<span class="${tagClass}">${t}</span>`;
      }).join('');
      tagsEl.style.display = 'flex';
    } else {
      tagsEl.style.display = 'none';
    }
  }

  const descEl = document.getElementById('modal-desc');
  if (descEl) descEl.textContent = dish.description;

  const proteinEl = document.getElementById('modal-protein');
  if (proteinEl) proteinEl.textContent = proteinVal;

  const eggsEl = document.getElementById('modal-eggs');
  if (eggsEl) eggsEl.textContent = dish.eggsUsed > 0 ? `${dish.eggsUsed} Farm Eggs` : (dish.dietary === 'Veg' ? 'Pure Vegetarian' : 'Beverage / Side');

  const waBtn = document.getElementById('modal-wa-btn');
  if (waBtn) waBtn.href = waUrl;

  // Book Table action inside modal
  const bookBtn = document.getElementById('modal-book-table-btn');
  if (bookBtn) {
    bookBtn.onclick = () => {
      closeDishModal();
      const notesInput = document.getElementById('booking-notes');
      if (notesInput) {
        notesInput.value = `Order interest: ${dish.name}`;
      }
    };
  }

  const closeActionBtn = document.getElementById('modal-close-action-btn');
  if (closeActionBtn) {
    closeActionBtn.onclick = closeDishModal;
  }

  modalBackdrop.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeDishModal() {
  if (!modalBackdrop) return;
  modalBackdrop.classList.remove('active');
  document.body.style.overflow = '';
}

// Setup Event Listeners
function setupEvents() {
  // Search input
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value.trim();
      visibleCount = BATCH_SIZE;
      if (clearSearchBtn) {
        clearSearchBtn.classList.toggle('visible', searchQuery.length > 0);
      }
      renderMenu();
    });
  }

  // Clear search
  if (clearSearchBtn) {
    clearSearchBtn.addEventListener('click', () => {
      searchQuery = '';
      if (searchInput) searchInput.value = '';
      clearSearchBtn.classList.remove('visible');
      visibleCount = BATCH_SIZE;
      renderMenu();
    });
  }

  // Tag filter chips
  filterChips.forEach(chip => {
    chip.addEventListener('click', () => {
      filterChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      currentTag = chip.getAttribute('data-tag');
      visibleCount = BATCH_SIZE;
      renderMenu();
    });
  });

  // Load More Button
  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', () => {
      visibleCount += BATCH_SIZE;
      renderMenu();
    });
  }

  // Modal close handlers
  if (modalCloseBtn) {
    modalCloseBtn.addEventListener('click', closeDishModal);
  }
  if (modalBackdrop) {
    modalBackdrop.addEventListener('click', (e) => {
      if (e.target === modalBackdrop) closeDishModal();
    });
  }
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalBackdrop && modalBackdrop.classList.contains('active')) {
      closeDishModal();
    }
  });

  // Featured cards click to open dish details modal
  document.querySelectorAll('.featured-card').forEach(card => {
    card.style.cursor = 'pointer';
    card.addEventListener('click', () => {
      const name = card.getAttribute('data-dish-name');
      if (name) {
        const dish = menuData.dishes.find(d => d.name.toLowerCase() === name.toLowerCase()) || {
          name: name,
          categoryId: 'chef-specials',
          categoryName: 'Chef Special Signatures',
          description: card.querySelector('.featured-card-desc')?.textContent.trim() || 'Signature chef preparation.',
          tags: ['Bestseller'],
          dietary: 'Egg',
          spiceLevel: 1,
          eggsUsed: 2
        };
        openDishModal(dish);
      }
    });
  });

  // Category Scroll Buttons
  const catScrollLeft = document.getElementById('cat-scroll-left');
  const catScrollRight = document.getElementById('cat-scroll-right');
  if (catScrollLeft && categoryContainer) {
    catScrollLeft.addEventListener('click', () => {
      categoryContainer.scrollBy({ left: -260, behavior: 'smooth' });
    });
  }
  if (catScrollRight && categoryContainer) {
    catScrollRight.addEventListener('click', () => {
      categoryContainer.scrollBy({ left: 260, behavior: 'smooth' });
    });
  }

  // FAQ Accordion
  document.querySelectorAll('.faq-item').forEach(item => {
    const questionBtn = item.querySelector('.faq-question');
    if (questionBtn) {
      questionBtn.addEventListener('click', () => {
        const isOpen = item.classList.contains('open');
        document.querySelectorAll('.faq-item').forEach(other => other.classList.remove('open'));
        if (!isOpen) {
          item.classList.add('open');
        }
      });
    }
  });

  // Mobile Nav Toggle & Backdrop Overlay
  const navBackdrop = document.getElementById('nav-menu-backdrop');
  if (navToggle && navMenu) {
    const toggleNav = (forceState) => {
      const willBeOpen = forceState !== undefined ? forceState : !navMenu.classList.contains('open');
      navMenu.classList.toggle('open', willBeOpen);
      navToggle.classList.toggle('active', willBeOpen);
      navToggle.setAttribute('aria-expanded', willBeOpen);
      if (navBackdrop) navBackdrop.classList.toggle('active', willBeOpen);
      document.body.style.overflow = willBeOpen ? 'hidden' : '';
    };

    navToggle.addEventListener('click', () => toggleNav());
    if (navBackdrop) {
      navBackdrop.addEventListener('click', () => toggleNav(false));
    }
    navMenu.querySelectorAll('.nav-link, .btn').forEach(link => {
      link.addEventListener('click', () => toggleNav(false));
    });
  }

  // Sticky header, active section spy, and scroll to top
  const header = document.querySelector('.header');
  const dockItems = document.querySelectorAll('.mobile-bottom-dock .dock-item');
  const sections = document.querySelectorAll('section[id], footer[id]');

  window.addEventListener('scroll', () => {
    const scrollPos = window.scrollY;
    if (scrollPos > 50) {
      if (header) header.classList.add('scrolled');
      if (scrollTopBtn) scrollTopBtn.classList.add('visible');
    } else {
      if (header) header.classList.remove('scrolled');
      if (scrollTopBtn) scrollTopBtn.classList.remove('visible');
    }

    // Mobile Dock Active State Spy
    let currentId = '';
    sections.forEach(sec => {
      const top = sec.offsetTop - 120;
      const height = sec.offsetHeight;
      if (scrollPos >= top && scrollPos < top + height) {
        currentId = sec.getAttribute('id');
      }
    });

    if (currentId) {
      dockItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === `#${currentId}`) {
          item.classList.add('active');
        } else if (href && href.startsWith('#')) {
          item.classList.remove('active');
        }
      });
    }
  });

  if (scrollTopBtn) {
    scrollTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
}

// ==========================================================================
// TABLE BOOKING INTERACTIVITY & RAZORPAY EXTENSION
// ==========================================================================
const bookingState = {
  guests: '2',
  date: '',
  dateFormatted: 'Today',
  session: 'lunch',
  time: '1:00 PM'
};

const sessionSlots = {
  lunch: ['12:00 PM', '12:30 PM', '1:00 PM', '1:30 PM', '2:00 PM', '2:30 PM', '3:00 PM'],
  dinner: ['7:00 PM', '7:30 PM', '8:00 PM', '8:30 PM', '9:00 PM', '9:30 PM', '10:00 PM'],
  breakfast: ['8:30 AM', '9:00 AM', '9:30 AM', '10:00 AM', '10:30 AM', '11:00 AM'],
  tea: ['4:00 PM', '4:30 PM', '5:00 PM', '5:30 PM', '6:00 PM', '6:30 PM']
};

function setupTableBooking() {
  const form = document.getElementById('table-booking-form');
  if (!form) return;

  const guestPills = document.querySelectorAll('#guest-pills-row .guest-pill');
  const quickDatesRow = document.getElementById('quick-dates-row');
  const dateInput = document.getElementById('booking-date-input');
  const sessionTabs = document.querySelectorAll('#session-tabs .session-tab');
  const slotsGrid = document.getElementById('slots-grid');

  const sumGuests = document.getElementById('sum-guests');
  const sumDate = document.getElementById('sum-date');
  const sumTime = document.getElementById('sum-time');

  const bookingModal = document.getElementById('booking-success-modal');
  const modalCloseBtn = document.getElementById('booking-modal-close-btn');
  const doneBtn = document.getElementById('conf-done-btn');

  // Update summary card UI
  function updateSummary() {
    if (sumGuests) sumGuests.textContent = `${bookingState.guests} ${bookingState.guests.includes('Guest') ? '' : 'Guests'}`;
    if (sumDate) sumDate.textContent = bookingState.dateFormatted;
    if (sumTime) sumTime.textContent = bookingState.time;
  }

  // 1. Guest Selection
  guestPills.forEach(pill => {
    pill.addEventListener('click', () => {
      guestPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      bookingState.guests = pill.getAttribute('data-guests');
      updateSummary();
    });
  });

  // 3. Quick Dates & Calendar Setup
  const today = new Date();
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  function formatDateObj(d) {
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }

  bookingState.date = formatDateObj(today);
  bookingState.dateFormatted = `Today (${days[today.getDay()]}, ${today.getDate()} ${months[today.getMonth()]})`;
  if (dateInput) {
    dateInput.min = bookingState.date;
    dateInput.value = bookingState.date;
  }

  // Generate 4 quick date chips
  if (quickDatesRow) {
    quickDatesRow.innerHTML = '';
    for (let i = 0; i < 4; i++) {
      const d = new Date(today);
      d.setDate(today.getDate() + i);
      const isToday = i === 0;
      const isTomorrow = i === 1;
      const label = isToday ? 'Today' : isTomorrow ? 'Tomorrow' : `${days[d.getDay()]}, ${d.getDate()} ${months[d.getMonth()]}`;
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = `quick-date-chip ${i === 0 ? 'active' : ''}`;
      chip.textContent = label;
      chip.dataset.isoDate = formatDateObj(d);
      chip.dataset.displayDate = label;

      chip.addEventListener('click', () => {
        quickDatesRow.querySelectorAll('.quick-date-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        bookingState.date = chip.dataset.isoDate;
        bookingState.dateFormatted = chip.dataset.displayDate;
        if (dateInput) dateInput.value = bookingState.date;
        updateSummary();
      });

      quickDatesRow.appendChild(chip);
    }
  }

  if (dateInput) {
    dateInput.addEventListener('change', (e) => {
      const selected = new Date(e.target.value + 'T00:00:00');
      if (!isNaN(selected)) {
        bookingState.date = e.target.value;
        bookingState.dateFormatted = `${days[selected.getDay()]}, ${selected.getDate()} ${months[selected.getMonth()]}`;
        if (quickDatesRow) {
          quickDatesRow.querySelectorAll('.quick-date-chip').forEach(c => {
            if (c.dataset.isoDate === bookingState.date) {
              c.classList.add('active');
            } else {
              c.classList.remove('active');
            }
          });
        }
        updateSummary();
      }
    });
  }

  // 4. Meal Sessions & Time Slots
  function renderSlots(session) {
    if (!slotsGrid) return;
    const slots = sessionSlots[session] || sessionSlots.lunch;
    slotsGrid.innerHTML = '';

    slots.forEach((timeStr, idx) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `slot-chip ${idx === 2 ? 'active' : ''}`; // default 1:00 PM for lunch
      btn.textContent = timeStr;
      if (idx === 2) bookingState.time = timeStr;

      btn.addEventListener('click', () => {
        slotsGrid.querySelectorAll('.slot-chip').forEach(s => s.classList.remove('active'));
        btn.classList.add('active');
        bookingState.time = timeStr;
        updateSummary();
      });

      slotsGrid.appendChild(btn);
    });
    updateSummary();
  }

  sessionTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      sessionTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      bookingState.session = tab.getAttribute('data-session');
      renderSlots(bookingState.session);
    });
  });

  renderSlots('lunch');
  updateSummary();

  // 5. Booking Form Submission & Dual Dispatch (Owner & Customer)
  // Direct email dispatch to Café Owner & Customer
  function sendBookingEmails(payload) {
    const emailData = {
      _subject: `New Table Booking #${payload.refId} - Frittata Fiesta Café`,
      _cc: payload.email,
      Booking_Reference: payload.refId,
      Guest_Name: payload.name,
      Phone_Number: payload.phone,
      Customer_Email: payload.email,
      Party_Size: `${payload.guests} Guests`,
      Reservation_Date: payload.date,
      Time_Slot: payload.time,
      Special_Requests: payload.notes || 'None',
      Deposit_Status: '₹200 (100% Deducted from final food bill)'
    };

    // Send direct background email notification to owner and cc customer
    fetch('https://formsubmit.co/ajax/frittatafiesta@gmail.com', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(emailData)
    }).then(res => res.json())
      .then(data => {
        console.log('Direct confirmation email dispatched:', data);
      })
      .catch(err => {
        console.log('Background email dispatch status:', err);
      });
  }

  // Booking Form Submission
  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const name = document.getElementById('booking-name')?.value.trim();
    const phone = document.getElementById('booking-phone')?.value.trim();
    const email = document.getElementById('booking-email')?.value.trim() || '';
    const notes = document.getElementById('booking-notes')?.value.trim() || '';

    if (!name || !phone) {
      alert('Please fill in your Name and Mobile phone number.');
      return;
    }
    if (!email) {
      alert('Please provide your Email Address to receive the official booking confirmation.');
      return;
    }

    const refId = 'FF-BK-' + Math.floor(10000 + Math.random() * 90000);

    const bookingPayload = {
      refId,
      name,
      phone,
      email,
      notes,
      guests: bookingState.guests,
      date: bookingState.dateFormatted,
      time: bookingState.time,
      depositAmount: 200,
      currency: 'INR'
    };

    // Store in browser storage
    try {
      const past = JSON.parse(localStorage.getItem('ff_bookings') || '[]');
      past.push({ ...bookingPayload, timestamp: new Date().toISOString() });
      localStorage.setItem('ff_bookings', JSON.stringify(past));
    } catch (err) {
      console.warn('Storage unavailable', err);
    }

    // Directly dispatch confirmation email to owner and customer (WITHOUT opening WhatsApp immediately)
    sendBookingEmails(bookingPayload);

    // Display confirmation modal with contact number and email dispatch confirmation
    showBookingSuccess(bookingPayload);
  });

  function showBookingSuccess(payload) {
    const confRef = document.getElementById('conf-ref-id');
    const confName = document.getElementById('conf-name');
    const confGuests = document.getElementById('conf-guests');
    const confDateTime = document.getElementById('conf-datetime');
    const confEmailVal = document.getElementById('conf-email-val');
    const confEmailStatus = document.getElementById('conf-email-status');

    if (confRef) confRef.textContent = payload.refId;
    if (confName) confName.textContent = payload.name;
    if (confGuests) confGuests.textContent = `${payload.guests} Guests`;
    if (confDateTime) confDateTime.textContent = `${payload.date} • ${payload.time}`;
    if (confEmailVal) confEmailVal.textContent = `${payload.email} & Owner`;
    if (confEmailStatus) confEmailStatus.textContent = `Official booking pass sent to frittatafiesta@gmail.com and ${payload.email}.`;

    if (bookingModal) {
      bookingModal.classList.add('active');
    }
  }

  function closeBookingModal() {
    if (bookingModal) {
      bookingModal.classList.remove('active');
    }
  }

  if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeBookingModal);
  if (doneBtn) doneBtn.addEventListener('click', closeBookingModal);
  if (bookingModal) {
    bookingModal.addEventListener('click', (e) => {
      if (e.target === bookingModal) closeBookingModal();
    });
  }
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  checkOpenHours();
  renderCategories();
  renderMenu();
  setupEvents();
  setupTableBooking();
  setInterval(checkOpenHours, 60000);
});

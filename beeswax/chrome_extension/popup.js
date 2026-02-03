document.addEventListener("DOMContentLoaded", async () => {
  console.log("chrome.storage exists?", chrome.storage);

  // Elements
  const addCouponButton = document.getElementById("add-coupon");
  const couponSection = document.getElementById("section");
  const toggleExpiry = document.getElementById("toggle-expiry");
  const toggleSeasonal = document.getElementById("toggle-seasonal");
  const loginBtn = document.getElementById("login-btn");
  const signupBtn = document.getElementById("signup-btn");
  const authBar = document.getElementById("auth-bar");
  const authForm = document.getElementById("auth-form");
  const submitAuth = document.getElementById("submit-auth");
  const cancelAuth = document.getElementById("cancel-auth");
  const emailInput = document.getElementById("email-input");
  const passwordInput = document.getElementById("password-input");
  const logoutBtn = document.getElementById("logout-btn");

  let jwtToken = null;
  let authMode = null; // 'login' or 'signup'

  const server = "http://localhost:5000";

  loginBtn.addEventListener("click", () => {
    authMode = "login";
    authBar.style.display = "none";
    authForm.style.display = "flex";
    submitAuth.textContent = "Login";
  });

  logoutBtn.addEventListener("click", () => {
  chrome.storage.local.remove("jwt", () => {
    console.log("Logged out");
    // reset UI
    couponSection.innerHTML = '<p>No coupons available for this website.</p>';
    loginBtn.style.display = "inline-block";
    signupBtn.style.display = "inline-block";
    logoutBtn.style.display = "none";
    document.getElementById("user-status").style.display = "none";
  });
});


  signupBtn.addEventListener("click", () => {
    authMode = "signup";
    authBar.style.display = "none";
    authForm.style.display = "flex";
    submitAuth.textContent = "Sign Up";
  });

  cancelAuth.addEventListener("click", () => {
    authForm.style.display = "none";
    authBar.style.display = "flex";
    emailInput.value = "";
    passwordInput.value = "";
  });

  submitAuth.addEventListener("click", async () => {
    const email = emailInput.value;
    const password = passwordInput.value;
    if (!email || !password) return alert("Please fill in both fields");
    
    try {
      if (authMode === "login") {
        const res = await fetch(`${server}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        const data = await res.json();
        if (data.access_token) {
          jwtToken = data.access_token;
          chrome.storage.local.set({ jwt: jwtToken }, () => {
            console.log("JWT stored");
          });

          // Update UI immediately
          loginBtn.style.display = "none";
          signupBtn.style.display = "none";
          logoutBtn.style.display = "inline-block";  // <-- show logout

          authForm.style.display = "none";
          authBar.style.display = "none";

          alert("Logged in!");
        } else alert("Login failed");
      } else if (authMode === "signup") {
        const res = await fetch(`${server}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        if (res.ok) {
          alert("Account created! Please log in.");
          authForm.style.display = "none";
          authBar.style.display = "flex";
        } else {
          const data = await res.json();
          alert(data.error || "Signup failed");
        }
      }
    } catch (err) {
      console.error("Auth error:", err);
      alert("Auth request failed");
    }
  });

  // Load token on startup
 chrome.storage.local.get(["jwt"], (result) => {
  if (result.jwt) {
    jwtToken = result.jwt;
    loginBtn.style.display = "none";
    signupBtn.style.display = "none";
    logoutBtn.style.display = "inline-block"; // show logout
  }
});
  
  chrome.tabs.query({ active: true, lastFocusedWindow: true }, (tabs) => {
    const url = new URL(tabs[0].url);
    const domain = url.hostname;
    console.log("Domain being hashed:", domain);

    const encoder = new TextEncoder();
    crypto.subtle.digest("SHA-256", encoder.encode(domain))
      .then(hashBuffer => {
        const hashedDomain = Array.from(new Uint8Array(hashBuffer))
          .map(b => b.toString(16).padStart(2, "0"))
          .join("")
          .slice(0, 5);

        console.log("Full hash:", hashedDomain);
        console.log("First 5:",hashedDomain.slice(0, 5));
        const currSite = document.querySelector(".curr_site");
        if (currSite) {
          currSite.textContent = " to " + domain;
        }

       chrome.storage.local.get(["jwt"], (result) => {
        let headers = { "Content-Type": "application/json" };
        if (result.jwt) headers["Authorization"] = `Bearer ${result.jwt}`;

        fetch(`${server}/check_website?hashedDomain=${hashedDomain}`, { headers })
          .then(res => res.json())
          .then(data => {
            renderCoupons(data, domain); // ✅ now data is defined
          })
          .catch(err => console.error("Error fetching coupons:", err));
      });
      }).catch(err => console.error("Error hashing domain:", err));

  });


  addCouponButton.addEventListener("click", () => {
    chrome.tabs.query({ active: true, lastFocusedWindow: true }, (tabs) => {
      const url = new URL(tabs[0].url);
      const website = url.hostname; 
      const coupon = document.getElementById("coupon").value;
      const desc = document.getElementById("desc").value;

      if(coupon){

      if(type === 'expires'){

        const expiryDate = document.getElementById("expiry-date").value;

        if(expiryDate){
        fetch(`${server}/add_coupon`, {
          method: "POST",
          // headers: { "Content-Type": "application/json" },
          headers: {
          "Content-Type": "application/json",
          ...(jwtToken && { "Authorization": `Bearer ${jwtToken}` })},
          body: JSON.stringify({ website, coupon , desc, type , expiryDate}),
        })
          .then((response) => response.json())
          .then((data) => {
            location.reload()
          }).catch((err) => console.error(err));
        }else{alert('Please enter an expiry date')}
      }else if(type === 'seasonal'){
        const expiryDate = document.getElementById("expiry-date").value;
        const startDate = document.getElementById("start-date").value;

        if(expiryDate){
        if(startDate){

        fetch(`${server}/add_coupon`, {
          method: "POST",
          // headers: { "Content-Type": "application/json" },
          headers: {
          "Content-Type": "application/json",
          ...(jwtToken && { "Authorization": `Bearer ${jwtToken}` })},
          body: JSON.stringify({ website, coupon , desc, type, expiryDate, startDate}),
        })
          .then((response) => response.json())
          .then((data) => {
            location.reload()
          }).catch((err) => console.error(err));

        }else{alert('Please enter an expiry date')}
        }alert('Please enter a start date')

      }else{
        fetch(`${server}/add_coupon`, {
          method: "POST",
          // headers: { "Content-Type": "application/json" },
          headers: {
          "Content-Type": "application/json",
          ...(jwtToken && { "Authorization": `Bearer ${jwtToken}` })},
          body: JSON.stringify({ website, coupon , desc, type}),
        })
          .then((response) => response.json())
          .then((data) => {
            location.reload()
          }).catch((err) => console.error(err));
      }



      }else{
        alert('Please enter a coupon code')
      }
    });

  });

  toggleExpiry.addEventListener("click", () => {
    const settingsExpiary = document.getElementById("expiry-settings");
    if (settingsExpiary.style.display === "none") {
      type = 'expires';
      settingsExpiary.style.display = "block";
      toggleExpiry.textContent = "↑ Hide expiry settings ";
    } else {
      type = 'coupon';
      settingsExpiary.style.display = "none";
      toggleExpiry.textContent = "↓ Add expiry date";
    }
  });

  toggleSeasonal.addEventListener("click", () => {
    const settingsSeasonal = document.getElementById("seasonal-settings");
    if (settingsSeasonal.style.display === "none") {
      type = 'seasonal';
      settingsSeasonal.style.display = "block";
      toggleSeasonal.textContent = "↑ Hide Seasonal settings ";
    } else {
      type = 'expires';
      settingsSeasonal.style.display = "none";
      toggleSeasonal.textContent = "↓ Add seasonal coupon";
    }
  });
  

  function showcoupon(coupon) {
    const template = document.getElementById("template").content.cloneNode(true);
    const couponElement = template.querySelector(".coupon");
    couponElement.setAttribute("data-id", coupon._id);
    template.querySelector(".code").textContent = coupon.code;
    template.querySelector(".rating").textContent = coupon.rating;
    template.querySelector(".desc").textContent = coupon.desc;
    if(coupon.expiryDate){template.querySelector(".expiryDate").textContent = "Expires in " + coupon.expiresIn + " day(s)";}

    template.querySelector(".rate-up").addEventListener("click", () => {
      rateCoupon(coupon._id, 1);
    });
    template.querySelector(".rate-down").addEventListener("click", () => {
      rateCoupon(coupon._id, -1);
    });

    couponSection.appendChild(template);
  }

  function renderCoupons(data, domain) {
  couponSection.innerHTML = ''; // always clear first

  if (data.success && data.coupons.length > 0) {
    let coupons = data.coupons.filter(c => c.website === domain);

    if (coupons.length === 0) {
      couponSection.innerHTML = '<p>No coupons available for this website.</p>';
      return;
    }

    coupons.sort((a, b) => b.rating - a.rating);
    const shownCount = Math.min(coupons.length, 3);

    for (let i = 0; i < shownCount; i++) {
      showcoupon(coupons[i]);
    }

    if (coupons.length > 3) {
      const template = document.getElementById("showmore").content.cloneNode(true);
      const showmoreButton = template.querySelector(".showmoreButton");
      showmoreButton.addEventListener("click", () => {
        for (let i = shownCount; i < coupons.length; i++) {
          showcoupon(coupons[i]);
        }
        showmoreButton.remove();
      });
      couponSection.appendChild(showmoreButton);
    }
  } else {
    couponSection.innerHTML = '<p>No coupons available for this website.</p>';
  }
}


  function rateCoupon(couponId, ratingChange) {

    if (!jwtToken) {
      let rated = JSON.parse(localStorage.getItem("ratedCoupons") || "[]");
      if (rated.includes(couponId)) return alert("You have already rated this coupon!");
      rated.push(couponId);
      localStorage.setItem("ratedCoupons", JSON.stringify(rated));
    }

    fetch(`${server}/rate_coupon`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(jwtToken && { "Authorization": `Bearer ${jwtToken}` })
      },
      body: JSON.stringify({ coupon_id: couponId, rating_change: ratingChange }),
    })
      .then(res => res.json())
      .then(data => {
        if (!data.success && data.message === "Already rated") {
          alert("You have already rated this coupon!");
          const couponElement = document.querySelector(`.coupon[data-id="${couponId}"]`);
          if (couponElement) {
            const buttons = couponElement.querySelectorAll(".rate-buttons button");
            buttons.forEach(btn => {
              btn.disabled = true;
              btn.style.opacity = 0.5;
            });
          }
          return;
        }

        if (data.success) {
          const couponElement = document.querySelector(`.coupon[data-id="${couponId}"]`);
          if (!couponElement) return;

          if (data.deleted) {
            couponElement.style.transition = "opacity 0.3s";
            couponElement.style.opacity = "0";
            setTimeout(() => couponElement.remove(), 300);
          } else {
            const ratingElement = couponElement.querySelector(".rating");
            ratingElement.textContent = parseInt(ratingElement.textContent) + ratingChange;

            const buttons = couponElement.querySelectorAll(".rate-buttons button");
            buttons.forEach(btn => {
              btn.disabled = true;
              btn.style.opacity = 0.5;
            });
          }
        }
      })
      .catch(err => console.error("Error updating rating:", err));
  }

});

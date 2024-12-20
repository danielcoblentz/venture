// (dashboard page)
//search wrapper section 
const search = document.querySelector(".search-wrapper");

if (search) {
  const input = search.querySelector("input");

  // expand search bar on hover
  search.addEventListener("mouseenter", () => {
    if (!input.matches(":focus")) {
      search.classList.add("active");
    }
  });

  // close search bar when mouse leaves (if not focused or empty)
  search.addEventListener("mouseleave", () => {
    if (!input.matches(":focus") && !input.value.trim()) {
      search.classList.remove("active");
    }
  });
}

//dashboard create event icon logic:

document.getElementById("create-icon").addEventListener("click", () => {
  document.getElementById("modal-overlay").style.display = "flex";
});

document.getElementById("close-modal-btn").addEventListener("click", () => {
  document.getElementById("modal-overlay").style.display = "none";
});

window.addEventListener("click", (e) => {
  if (e.target === document.getElementById("modal-overlay")) {
      document.getElementById("modal-overlay").style.display = "none";
  }
});



//(account page)
// email update section
document.addEventListener("DOMContentLoaded", () => {
  const changeEmailLink = document.getElementById("change-email");
  const emailInputContainer = document.getElementById("email-input-container");
  const saveEmailButton = document.getElementById("save-email-btn");


  //show the email input field when "change" text is clicked within form
  if (changeEmailLink) {
    changeEmailLink.addEventListener("click", () => {
      console.log("Change link clicked");
      emailInputContainer.style.display = "flex";
    });
  }

  // hide input field and display message shoeing update works, on save button click
  if (saveEmailButton) {
    saveEmailButton.addEventListener("click", () => {
      const newEmail = document.getElementById("new-email").value;
      if (newEmail) {
        alert(`Email changed to: ${newEmail}`);
        emailInputContainer.style.display = "none";
      }
    });
  }
});

    //password hide / show logic
document.addEventListener("DOMContentLoaded", () => {
  const togglePasswordLink = document.getElementById("toggle-password");
  const newPasswordInput = document.getElementById("new-password");
  const currentPasswordInput = document.getElementById("current-password");

  // toggle visibility
  togglePasswordLink.addEventListener("click", () => {
    const isPasswordHidden = newPasswordInput.type === "password";

    //toggle input between password and text
    newPasswordInput.type = isPasswordHidden ? "text" : "password";
    currentPasswordInput.type = isPasswordHidden ? "text" : "password";

    //update link
    togglePasswordLink.textContent = isPasswordHidden ? "Hide" : "Show";
  });
});
// (home page)
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

//dashboard create event icon logic (show the form on click)
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
// email,password update section
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

//preview pannel logic for displaying event details to user
document.addEventListener("DOMContentLoaded", () => {
  // Preview panel elements
  const previewName = document.getElementById("preview-name");
  const previewDate = document.getElementById("preview-date");
  const previewLocation = document.getElementById("preview-location");
  const previewCost = document.getElementById("preview-cost");
  const previewDescription = document.getElementById("preview-description");
  const attendButton = document.getElementById("attend-button");

  // function to handle displaying event details
  window.showEventDetails = (eventBox) => {
      // retrieve data attributes from the clicked event box
      const eventId = eventBox.getAttribute("data-id");
      const eventName = eventBox.getAttribute("data-name");
      const eventDate = eventBox.getAttribute("data-date");
      const eventLocation = eventBox.getAttribute("data-location");
      const eventCost = eventBox.getAttribute("data-cost");
      const eventDescription = eventBox.getAttribute("data-description");

      //populate the preview panel with event details from DB
      previewName.textContent = `Name: ${eventName}`;
      previewDate.textContent = `Date: ${eventDate}`;
      previewLocation.textContent = `Location: ${eventLocation}`;
      previewCost.textContent = `Cost: ${eventCost}`;
      previewDescription.textContent = `Description: ${eventDescription}`;

      //display button and attach the event ID
      attendButton.style.display = "block";
      attendButton.onclick = () => {
          attendEvent(eventId);
      };
  };

  //function to handle attending an event (currently working on this)
  async function attendEvent(eventId) {
      try {
          const response = await fetch(`/attend-event/${eventId}`, {
              method: "POST",
              headers: {
                  "Content-Type": "application/json",
              },
          });

          // return error message to user
          if (!response.ok) {
              const error = await response.json();
              alert(error.message); 
              return;
          }
          
          //return success message to user
          const result = await response.json();
          alert(result.message); 
      } catch (error) {
          console.error("error attending the event:", error);
          alert("error occurred while marking attendance");
      }
  }
});


// attend event button logic







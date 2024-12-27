
const DEBUG = false;

document.addEventListener("DOMContentLoaded", () => {
    //(Home page)
    // search wrapper section
    const search = document.querySelector(".search-wrapper");

    if (search) {
        const input = search.querySelector("input");

        // expand search bar on hover
        search.addEventListener("mouseenter", () => {
            if (!input.matches(":focus")) {
                search.classList.add("active");
            }
        });

        //close search bar when mouse leaves (not currently in searhc bar)
        search.addEventListener("mouseleave", () => {
            if (!input.matches(":focus") && !input.value.trim()) {
                search.classList.remove("active");
            }
        });
    }


    //dashboard create event icon logic (show the form on click)
    const createIcon = document.getElementById("create-icon");
    const modalOverlay = document.getElementById("modal-overlay");
    const closeModalButton = document.getElementById("close-modal-btn");

    if (createIcon) {
        createIcon.addEventListener("click", () => {
            modalOverlay.style.display = "flex";
        });
    }

    if (closeModalButton) {
        closeModalButton.addEventListener("click", () => {
            modalOverlay.style.display = "none";
        });
    }

    window.addEventListener("click", (e) => {
        if (e.target === modalOverlay) {
            modalOverlay.style.display = "none";
        }
    });

    //(Account page)
    //email update section
    const changeEmailLink = document.getElementById("change-email");
    const emailInputContainer = document.getElementById("email-input-container");
    const saveEmailButton = document.getElementById("save-email-btn");

    if (changeEmailLink) {
        changeEmailLink.addEventListener("click", () => {
            if (DEBUG) console.log("Change email link clicked");
            emailInputContainer.style.display = "flex";
        });
    }

    if (saveEmailButton) {
        saveEmailButton.addEventListener("click", async () => {
            const newEmail = document.getElementById("new-email").value;
            if (newEmail) {
                try {
                    const response = await fetch('/update-email', {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ email: newEmail })
                    });

                    const result = await response.json();
                    if (response.ok) {
                        alert(result.message);
                        emailInputContainer.style.display = "none";
                    } else {
                        alert(result.message);
                    }
                } catch (error) {
                    console.error("Error updating email:", error);
                    alert("An error occurred while updating your email.");
                }
            }
        });
    }

    //password hide/show logic
    const togglePasswordLink = document.getElementById("toggle-password");
    const newPasswordInput = document.getElementById("new-password");
    const currentPasswordInput = document.getElementById("current-password");
    const savePasswordButton = document.getElementById("save-password-btn");

    if (togglePasswordLink) {
        togglePasswordLink.addEventListener("click", () => {
            const isPasswordHidden = newPasswordInput.type === "password";

            //toggle input between password and text()
            newPasswordInput.type = isPasswordHidden ? "text" : "password";
            currentPasswordInput.type = isPasswordHidden ? "text" : "password";

            //update link text
            togglePasswordLink.textContent = isPasswordHidden ? "Hide" : "Show";
        });
    }

    //(updating password)
    if (savePasswordButton) {
        savePasswordButton.addEventListener("click", async () => {
            const newPassword = document.getElementById("new-password").value;
            const currentPassword = document.getElementById("current-password").value;

            if (newPassword && currentPassword) {
                try {
                    const response = await fetch('/update-password', {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            new_password: newPassword,
                            current_password: currentPassword
                        })
                    });

                    const result = await response.json();
                    if (response.ok) {
                        alert(result.message);
                    } else {
                        alert(result.message);
                    }
                } catch (error) {
                    console.error("arror updating password:", error);
                    alert("an error occurred while updating your password");
                }
            } else {
                alert(" fill in both the current and new password fields");
            }
        });
    }


    //(Preview panel)
    //logic for displaying event details to the user
    const previewName = document.getElementById("preview-name");
    const previewDate = document.getElementById("preview-date");
    const previewEndTime = document.getElementById("preview-end-time");
    const previewLocation = document.getElementById("preview-location");
    const previewCost = document.getElementById("preview-cost");
    const previewDescription = document.getElementById("preview-description");
    const attendButton = document.getElementById("attend-button");
    const deleteForm = document.getElementById("delete-form");



    window.showEventDetails = (eventBox) => {
        // retrieve data attributes from the clicked event box
        const eventId = eventBox.getAttribute("data-id");
        const eventName = eventBox.getAttribute("data-name");
        const eventDate = eventBox.getAttribute("data-date");
        const eventEndTime = eventBox.getAttribute("data-end-time");
        const eventLocation = eventBox.getAttribute("data-location");
        const eventCost = eventBox.getAttribute("data-cost");
        const eventDescription = eventBox.getAttribute("data-description");
        const isCreator = eventBox.dataset.creator === "true";

        // populate the preview panel with event details from the event container
        previewName.textContent = `Name: ${eventName}`;
        previewDate.textContent = `Date: ${eventDate}`;
        previewEndTime.textContent = `End Time: ${eventEndTime}`;
        previewLocation.textContent = `Location: ${eventLocation}`;
        previewCost.textContent = `Cost: ${eventCost}`;
        previewDescription.textContent = `Description: ${eventDescription}`;

        if (isCreator) {
            deleteForm.style.display = "block";
            deleteForm.action = `/delete_event/${eventId}`;
        } else {
            deleteForm.style.display = "none";
        }

        // display the attend button 
        attendButton.style.display = "block";
        attendButton.onclick = () => {
            attendEvent(eventId);
        };
    };

    //attend event logic(adding to DB after successful submission)
    async function attendEvent(eventId) {
        try {
            const response = await fetch(`/attend-event/${eventId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            const result = await response.json();
            if (response.ok) {
                alert(result.message);
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error("error attending the event:", error);
            alert("error occurred while processing your request.");
        }
    }


    // fetch and display registered events(neede for star icon on home page)
    async function fetchRegisteredEvents() {
        try {
            const response = await fetch("/my-events");
            if (!response.ok) throw new Error("Failed to fetch events");

            const events = await response.json();
            if (DEBUG) console.log("fetched events:", events);

            // clear event container(home.hmtl)
            const eventContainer = document.querySelector(".event-container");
            eventContainer.innerHTML = "";

            if (events.length === 0) {
                eventContainer.innerHTML = "<p>You are not registered for any events.</p>";
            } else {
                events.forEach((event) => {
                    if (DEBUG) console.log("Processing event:", event);
                    const eventBox = document.createElement("div");
                    eventBox.classList.add("event-box");
                    eventBox.innerHTML = `
                        <div class="event-info">
                            <h3>${event.name}</h3>
                            <p>${event.date}</p>
                        </div>
                        <hr class="event-divider">
                        <p class="event-location">${event.location}</p>
                        <p class="event-cost">Cost: ${event.cost}</p>
                    `;
                    eventContainer.appendChild(eventBox);
                });
            }
        } catch (error) {
            console.error("error fetching registered events:", error);
            alert("An error occurred while fetching your registered events.");
        }
    }

    // event listener for fetching registered events(star icon)
    const starIcon = document.querySelector('.action-item img[alt="Attending Events Icon"]');
    if (starIcon) {
        starIcon.parentElement.addEventListener("click", fetchRegisteredEvents);
    }
});

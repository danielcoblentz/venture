// initialize Stripe
const stripe = Stripe("enter publishable key here ");

// create an instance of elements
const elements = stripe.elements();
const cardElement = elements.create("card");

// mount the card element to the page
cardElement.mount("#card-element");

document.getElementById('pay-button').addEventListener('click', async () => {
    const amount = parseFloat(document.getElementById('amount').value) * 100; // Convert dollars to cents
    if (!amount || amount <= 0) {
        alert("Please enter a valid amount.");
        return;
    }

    try {
        // create a PaymentIntent on the server
        const response = await fetch('/create-payment-intent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ amount }),
        });

        const data = await response.json();
        if (data.error) {
            alert(data.error);
            return;
        }

        // confirm the payment
        const { clientSecret } = data;
        const result = await stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: cardElement,
                billing_details: {
                    name: "Test User", // replace or fetch dynamically
                },
            },
        });

        if (result.error) {
            alert(`Payment failed: ${result.error.message}`);
        } else if (result.paymentIntent && result.paymentIntent.status === 'succeeded') {
            alert("Balance added successfully!");
            location.reload(); // refresh to update balance
        }
    } catch (err) {
        console.error("Error processing payment:", err);
        alert("An error occurred while processing your payment.");
    }
});

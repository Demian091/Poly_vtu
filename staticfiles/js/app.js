function buyData(event) {

    const service = document.getElementById("service").value;
    const plan = document.getElementById("plan").value;
    const phone = document.getElementById("phone").value;

    const button = event.target;

    button.disabled = true;
    button.innerText = "Processing...";

    if (!service || !plan || !phone) {
        // still redirect to receipt page with error info
        window.location.href = `/receipt/0/?error=missing_fields`;
        return;
    }

    if (phone.length !== 11) {
        window.location.href = `/receipt/0/?error=invalid_phone`;
        return;
    }

    fetch("/api/buy_data/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            service: service,
            plan: plan,
            phone: phone
        })
    })
    .then(res => res.json())
    .then(data => {

        // ALWAYS redirect (success OR fail)
        if (data.transaction_id) {
            window.location.href = `/receipt/${data.transaction_id}/`;
        } else {
            window.location.href = `/receipt/0/?error=transaction_failed`;
        }
    })
    .catch(err => {
        console.log(err);
        window.location.href = `/receipt/0/?error=server_error`;
    });
}


// CSRF helper
function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}



// Load plans dynamically
document.getElementById("service").addEventListener("change", loadPlans);

function loadPlans() {
    const service = document.getElementById("service").value;

    if (!service) return;

    fetch(`/api/get-plans/?service=${service}`)
        .then(res => res.json())
        .then(data => {

            const planSelect =
                document.getElementById("plan");

            planSelect.innerHTML =
                "<option>Select Plan</option>";

            data.forEach(plan => {

                const option =
                    document.createElement("option");

                option.value = plan.value;

                option.textContent =
`${plan.displayName} - ₦${plan.user_price}`;

                planSelect.appendChild(option);
            });
        })
        .catch(err => {
            console.error("Error loading plans:", err);
        });
}


// FUND WALLET
function fundWallet() {

    const amount = document.getElementById("fund-amount").value;

    if (!amount || amount <= 0) {

        showPopup(
            "Invalid Amount",
            "Enter a valid amount",
            "error"
        );

        return;
    }

    fetch("/api/fund-wallet/", {

        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },

        body: JSON.stringify({ amount: amount })
    })

    .then(res => res.json())
    .then(data => {

        if (data.authorization_url) {

            window.location.href = data.authorization_url;

        } else {

            showPopup(
                "Error",
                "Unable to initialize payment",
                "error"
            );
        }
    })

    .catch(err => {

        console.log(err);

        showPopup(
            "Error",
            "Something went wrong",
            "error"
        );
    });
}
   
        // Toggle password visibility
function togglePassword() {
    const input = document.getElementById('password');
    const icon = document.getElementById('eye-icon');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}


        // Toggle password visibility
        function togglePassword(inputId, iconId) {
            const input = document.getElementById(inputId);
            const icon = document.getElementById(iconId);
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        }

        // Password strength checker
function checkStrength(password) {
    const meter = document.getElementById('strength-meter');
    const bars = [
        document.getElementById('bar-1'),
        document.getElementById('bar-2'),
        document.getElementById('bar-3'),
        document.getElementById('bar-4')
    ];
    const text = document.getElementById('strength-text');
    
    meter.style.display = password.length > 0 ? 'block' : 'none';
    
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    
    const colors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-emerald-500'];
    const labels = ['Weak', 'Fair', 'Good', 'Strong'];
    
    bars.forEach((bar, i) => {
        bar.className = 'flex-1 strength-bar ' + (i < strength ? colors[strength - 1] : 'bg-slate-200');
    });
    
    text.textContent = strength > 0 ? labels[strength - 1] : 'Enter a password';
    text.className = 'text-xs ' + (strength > 0 ? 'text-' + colors[strength - 1].split('-')[1] + '-600' : 'text-slate-400');
}


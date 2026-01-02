async function createNote() {
    const text = document.getElementById("noteText").value.trim();
    if (!text) {
        document.getElementById("otpResult").innerText = "Please type a note first!";
        return;
    }

    try {
        const res = await fetch("/api/notes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        let data;
        try {
            data = await res.json();
        } catch (e) {
            data = { error: "Server returned invalid or empty response" };
        }

        if (res.ok) {
            document.getElementById("otpResult").innerText =
                `Your OTP: ${data.otp} (expires in 5 minutes)`;
            document.getElementById("noteText").value = "";
        } else {
            document.getElementById("otpResult").innerText =
                data.error || "Unknown error occurred";
        }
    } catch (err) {
        document.getElementById("otpResult").innerText =
            "Network error: " + err.message;
    }
}

async function getNote() {
    const otp = document.getElementById("otpInput").value.trim();
    if (!otp) {
        document.getElementById("noteOutput").innerText = "Please enter an OTP!";
        return;
    }

    try {
        const res = await fetch("/api/notes/retrieve", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ otp })
        });

        let data;
        try {
            data = await res.json();
        } catch (e) {
            data = { error: "Server returned invalid or empty response" };
        }

        if (res.ok) {
            document.getElementById("noteOutput").innerText =
                "Your Note: " + data.text;
            document.getElementById("otpInput").value = "";
        } else {
            document.getElementById("noteOutput").innerText =
                data.error || "Unknown error occurred";
        }
    } catch (err) {
        document.getElementById("noteOutput").innerText =
            "Network error: " + err.message;
    }
}

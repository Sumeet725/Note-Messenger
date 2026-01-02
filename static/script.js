async function createNote() {
    const text = document.getElementById("noteText").value;

    const res = await fetch("/api/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    });

    const data = await res.json();
    document.getElementById("otpResult").innerText =
        res.ok ? "Your OTP: " + data.otp : data.error;
}

async function getNote() {
    const otp = document.getElementById("otpInput").value;

    const res = await fetch("/api/notes/retrieve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ otp })
    });

    const data = await res.json();
    document.getElementById("noteOutput").innerText =
        res.ok ? data.text : data.error;
}

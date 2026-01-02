async function createNote() {
    const text = document.getElementById("noteText").value;
    const output = document.getElementById("otpResult");

    if (!text) {
        output.innerText = "Please type a note first!";
        return;
    }

    try {
        const res = await fetch("/api/notes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.error);

        output.innerText = `Your OTP: ${data.otp} (expires in 5 minutes)`;
        document.getElementById("noteText").value = "";
    } catch (err) {
        output.innerText = err.message;
    }
}

async function getNote() {
    const otp = document.getElementById("otpInput").value;
    const output = document.getElementById("noteOutput");

    if (!otp) {
        output.innerText = "Please enter an OTP!";
        return;
    }

    try {
        const res = await fetch("/api/notes/retrieve", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ otp })
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.error);

        output.innerText = "Your Note: " + data.text;
        document.getElementById("otpInput").value = "";
    } catch (err) {
        output.innerText = err.message;
    }
}

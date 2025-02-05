document.addEventListener("DOMContentLoaded", function () {
    console.log("🚀 JavaScript betöltődött!");

    // AJAX kérés a backendhez a cookie státusz lekérdezésére
    fetch("/cookie-status/")
        .then(response => response.json())
        .then(data => {
            let hasUnknownCookies = false;
            let allHandled = true;

            for (const [group, info] of Object.entries(data)) {
                console.log(`🔍 Csoport: ${group}, Elfogadva: ${info.accepted}`);

                if (info.accepted === true) {
                    info.scripts.forEach(scriptContent => {
                        insertScript(scriptContent);
                    });
                } else if (info.accepted === false) {
                    console.log(`🚫 Süti "${group}" elutasítva, nem töltünk be semmit.`);
                } else {
                    console.log(`❓ Süti "${group}" HIÁNYZIK, banner kell!`);
                    hasUnknownCookies = true;
                    allHandled = false;
                }
            }

            if (allHandled && !hasUnknownCookies) {
                console.log("✅ Minden süti beállítva, banner eltűnik!");
                document.getElementById("cookie-banner").style.display = "none";
            } else {
                console.log("⚠️ Vannak hiányzó vagy ismeretlen sütik, banner megjelenik!");
                document.getElementById("cookie-banner").style.display = "block";

                // 🔹 FIGYELEM! Itt hozzáadjuk az "Elfogadom" gomb eseménykezelőjét!
                document.querySelectorAll(".cc-cookie-accept").forEach(button => {
                    button.removeEventListener("click", acceptCookie); // Megelőzzük a duplikált eventeket
                    button.addEventListener("click", acceptCookie);
                });

                // 🔹 És az "Elutasítás" gomb eseménykezelőjét is frissítjük
                document.querySelectorAll(".cc-cookie-decline").forEach(button => {
                    button.removeEventListener("click", declineCookie);
                    button.addEventListener("click", declineCookie);
                });
            }
        })
        .catch(error => {
            console.error("❌ Hiba történt a cookie-status lekérésekor:", error);
            console.log("⚠️ Hiba miatt mutatjuk a cookie bannert!");
            document.getElementById("cookie-banner").style.display = "block";
        });
});

// **Elfogadás eseménykezelő függvény**
function acceptCookie(event) {
    let group = event.target.getAttribute("data-cookie-group");
    console.log(`✅ Elfogadott csoport: ${group}`);

    fetch(`/cookie-accept/${group}/`)
        .then(response => response.json())
        .then(data => {
            console.log("📩 Backend válasza:", data);

            if (data.scripts.length > 0) {
                data.scripts.forEach(scriptContent => {
                    insertScript(scriptContent);
                });
                console.log("🚀 Google Analytics elindítva!");
            } else {
                console.warn("⚠️ Nincs visszakapott script!");
            }

            document.getElementById("cookie-banner").style.display = "none";
        })
        .catch(error => console.error("❌ Hiba történt:", error));
}

// **Elutasítás eseménykezelő függvény**
function declineCookie(event) {
    let group = event.target.getAttribute("data-cookie-group");
    console.log(`🚫 Elutasított csoport: ${group}`);

    fetch(`/cookie-decline/${group}/`)
        .then(response => response.json())
        .then(() => {
            document.getElementById("cookie-banner").style.display = "block";
            console.log("✅ Süti elutasítva, banner újra megjelenik!");
            document.getElementById("cookie-banner").style.display = "none";
        })
        .catch(error => console.error("❌ Hiba történt az elutasításnál:", error));
}

// **Script beillesztő függvény**
function insertScript(scriptContent) {
    let tempDiv = document.createElement("div");
    tempDiv.innerHTML = scriptContent;
    let scripts = tempDiv.getElementsByTagName("script");

    for (let script of scripts) {
        let newScript = document.createElement("script");
        if (script.src) {
            newScript.src = script.src;
            newScript.async = true;
        } else {
            newScript.textContent = script.textContent;
        }
        document.body.appendChild(newScript);
    }
}
